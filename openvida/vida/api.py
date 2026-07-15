"""Public section, including homepage and signup."""

import io
import os
import re
import zipfile

import cgm.extract as cgm
from flask import (
    Blueprint,
    Response,
    abort,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from lxml import etree
from sqlalchemy import desc, or_
from vida_py.basedata import (
    BodyStyle,
    Engine,
    ModelYear,
    PartnerGroup,
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
    get_vin_components_by_partner_group_id,
)
from vida_py.basedata import Session as BaseDataSession
from vida_py.diag import Session as DiagSession
from vida_py.diag import get_valid_profiles_for_selected
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py.service import (
    Document,
    DocumentProfile,
    Qualifier,
    Resource,
)
from vida_py.service import Session as ServiceRepoSession

from openvida import settings
from openvida.vida.epc import (
    get_epc_part_by_path,
    get_epc_part_info,
    get_epc_parts,
    get_epc_subelements,
    get_epc_top_level,
)
from openvida.vida.service import get_doc_by_chronicle, get_doc_by_link
from openvida.xslt_extension.table_xslt_extension import TableXsltExtension

blueprint = Blueprint("api", __name__, static_folder="../static", url_prefix="/Vida")


@blueprint.route("/DataImages/<path:filename>")
def image_by_path(filename):
    return _send_image(LocalizedGraphics.path == filename)


@blueprint.route("/img/<code>")
def image_by_code(code):
    return _send_image(LocalizedGraphics.fkGraphic == code)


@blueprint.route("/img_raw/<code>")
def raw_image_by_code(code):
    return _send_image(LocalizedGraphics.fkGraphic == code, True)


@blueprint.route("/ProfileImg/<profile>")
def profile_img(profile):
    if profile == "null":
        return send_from_directory("static", "img/ProfileImgPlaceholder.png")
    with BaseDataSession() as _basedata:
        path = (
            _basedata.query(VehicleModel.ImagePath)
            .outerjoin(VehicleProfile, VehicleProfile.fkVehicleModel == VehicleModel.Id)
            .filter(VehicleProfile.Id == profile)
            .one()[0]
        )
    return image_by_path(path)


def _send_image(filter, raw=False):
    with ImagesSession() as _images:
        img = _images.query(LocalizedGraphics).filter(filter).one()
        img_type = (
            _images.query(GraphicFormats)
            .outerjoin(
                Graphics,
                Graphics.fkGraphicFormat == GraphicFormats.id,
            )
            .filter(Graphics.id == img.fkGraphic)
            .one()
        )
    if img_type.description.lower() == "cgm" and not raw:
        svg_str = cgm.extract_vector_svg_from_bytes(img.imageData)
        return Response(
            svg_str,
            mimetype="image/svg+xml",
        )
    return send_file(
        io.BytesIO(img.imageData),
        mimetype=f"image/{img_type.description.lower()}",
        as_attachment=request.args.get("Download", False),
        download_name=img.path,
    )


@blueprint.route("/decode_vin/")
def decode_vin():
    vin = request.args.get("vinNumber", False)
    partnerGroup = int(request.args.get("partnerGroup", 1001))
    if not vin or len(vin) != 17:
        return abort(400)

    with BaseDataSession() as _basedata:
        profiles = get_vin_components_by_partner_group_id(_basedata, vin, partnerGroup)

    if not profiles:
        return abort(404)
    (
        model_id,
        model_cid,
        image_path,
        year_id,
        body_id,
        engine_id,
        transm_id,
        model_desc,
        year_desc,
        body_desc,
        engine_desc,
        transm_desc,
        year_cid,
        engine_cid,
        transm_cid,
    ) = profiles[0]
    return {
        "image": image_path,
        "chassis": vin[-6:],
        "model": model_id,
        "year": year_id,
        "engine": engine_id,
        "transmission": transm_id,
        "body": body_id,
    }


@blueprint.route("/profile", methods=["GET", "POST"])
def get_profile():
    with BaseDataSession() as _basedata:
        query = _basedata.query(VehicleProfile)

        def _arg_filter(query, field, key):
            if (val := request.args.get(key, None)) is None:
                return query
            return query.filter(or_(field == val, field == None))

        query = _arg_filter(query, VehicleProfile.Id, "Id")
        query = _arg_filter(query, VehicleProfile.fkPartnerGroup, "fkPartnerGroup")
        query = _arg_filter(query, VehicleProfile.fkVehicleModel, "fkVehicleModel")
        query = _arg_filter(query, VehicleProfile.fkModelYear, "fkModelYear")
        query = _arg_filter(query, VehicleProfile.fkEngine, "fkEngine")
        query = _arg_filter(query, VehicleProfile.fkTransmission, "fkTransmission")
        query = _arg_filter(query, VehicleProfile.fkSteering, "fkSteering")
        query = _arg_filter(query, VehicleProfile.fkBodyStyle, "fkBodyStyle")
        query = _arg_filter(query, VehicleProfile.fkSpecialVehicle, "fkSpecialVehicle")
        profile = query.order_by(desc(VehicleProfile.FolderLevel)).first()
        return {
            "Id": profile.Id,
            "FolderLevel": profile.FolderLevel,
            "Description": profile.Description,
            "Title": profile.Title,
            "ChassisNoFrom": profile.ChassisNoFrom,
            "ChassisNoTo": profile.ChassisNoTo,
            "fkNodeECU": profile.fkNodeECU,
            "fkPartnerGroup": profile.fkPartnerGroup,
            "fkVehicleModel": profile.fkVehicleModel,
            "fkModelYear": profile.fkModelYear,
            "fkEngine": profile.fkEngine,
            "fkTransmission": profile.fkTransmission,
            "fkSteering": profile.fkSteering,
            "fkBodyStyle": profile.fkBodyStyle,
            "fkSpecialVehicle": profile.fkSpecialVehicle,
            "NodeECU": e.Description if (e := profile.NodeECU) is not None else "",
            "PartnerGroup": e.Description if (e := profile.PartnerGroup) is not None else "",
            "VehicleModel": e.Description if (e := profile.VehicleModel) is not None else "",
            "ModelYear": e.Description if (e := profile.ModelYear) is not None else "",
            "Engine": e.Description if (e := profile.Engine) is not None else "",
            "Transmission": e.Description if (e := profile.Transmission) is not None else "",
            "Steering": e.Description if (e := profile.Steering) is not None else "",
            "BodyStyle": e.Description if (e := profile.BodyStyle) is not None else "",
            "SpecialVehicle": e.Description if (e := profile.SpecialVehicle) is not None else "",
        }


@blueprint.route("/partnerGroups", methods=["GET", "POST"])
def get_partner_groups():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": f"{e.Description} ({e.Cid})"}
            for e in _basedata.query(PartnerGroup).all()
        ]


@blueprint.route("/modelYears", methods=["GET", "POST"])
def get_model_years():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(ModelYear).all()]


@blueprint.route("/vehicleModels", methods=["GET", "POST"])
def get_vehicle_models():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(VehicleModel).all()]


@blueprint.route("/engines", methods=["GET", "POST"])
def get_engines():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(Engine).all()]


@blueprint.route("/transmissions", methods=["GET", "POST"])
def get_transmissions():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(Transmission).all()]


@blueprint.route("/steerings", methods=["GET", "POST"])
def get_steerings():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(Steering).all()]


@blueprint.route("/bodyStyles", methods=["GET", "POST"])
def get_body_styles():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(BodyStyle).all()]


@blueprint.route("/specialVehicles", methods=["GET", "POST"])
def get_special_vehicles():
    with BaseDataSession() as _basedata:
        return [{"id": e.Id, "text": e.Description} for e in _basedata.query(SpecialVehicle).all()]


@blueprint.route("/epc/getComponents/")
def get_epc_components():
    profile = request.args.get("selectedProfile", False)
    if not profile:
        return abort(400)
    language = request.args.get("language", False) or 15
    path = request.args.get("path", "")
    if not path:
        return get_epc_top_level(profile, language)
    component = get_epc_part_by_path(path, language)
    level = component["assemblyLevel"]
    id_ = component["id"]
    # if level in (1, 2):
    if component["type"] in (1, 2):
        return get_epc_subelements(id_, level, profile, language)
    return get_epc_parts(id_, language)


@blueprint.route("/epc/getPartByPath/")
def epc_get_part_by_path():
    language = request.args.get("language", False) or 15
    path = request.args.get("path", False)
    if not path:
        return {"type": 2, "path": ""}
        # return abort(400)
    return get_epc_part_by_path(path, language)


@blueprint.route("/epc/part/<partnumber>")
def epc_get_part_info(partnumber):
    language = request.args.get("language", False) or 15
    part, applications = get_epc_part_info(partnumber, language)
    return {"part": part, "applications": applications}


@blueprint.route("/resources/")
def resources():
    with ServiceRepoSession() as _service:
        res = _service.query(Resource).all()
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "type": doc.type.Title,
                "url": url_for("api.resource_file", id_=doc.id),
            }
            for doc in res
        ]


@blueprint.route("/resource/<int:id_>")
def resource_file(id_):
    with ServiceRepoSession() as _service:
        doc = _service.query(Resource).filter(Resource.id == id_).first()

        return send_file(io.BytesIO(doc.ResourceData), "pdf", download_name=doc.filename)


@blueprint.route("/docsByQual/<profile>", methods=["GET", "POST"])
def documents_by_qualifier(profile):
    with ServiceRepoSession() as _service, DiagSession() as _diag:
        profiles = [
            e[0] for e in get_valid_profiles_for_selected(_diag, profile)
        ]  # (ID, FolderLevel)

        quals = (
            _service.query(Qualifier.id, Qualifier.title).order_by(Qualifier.qualifierCode).all()
        )
        docs_by_qual = []
        docs = (
            _service.query(Document.chronicleId, Document.title, Document.fkQualifier)
            .outerjoin(DocumentProfile, DocumentProfile.fkDocument == Document.id)
            .filter(
                DocumentProfile.profileId.in_(profiles),
                # Document.fkQualifier == qual[0],
            )
            .order_by(Document.id)
            .all()
        )
        for qual in quals:
            _docs = [dict(zip(("chronicleId", "title"), e[:2])) for e in docs if e[2] == qual[0]]
            if _docs:
                docs_by_qual.append(
                    {
                        "qual": dict(zip(("id", "title"), qual)),
                        "docs": _docs,
                    }
                )
    return docs_by_qual


@blueprint.route("/document/<chronicle>/", methods=["GET", "POST"])
def get_document_html(chronicle):
    doc = get_doc_by_chronicle(chronicle)
    if doc is None:
        return None
    return doc_to_html(doc)


@blueprint.route("/doclink/<element>/", methods=["GET", "POST"])
def get_doclink_html(element):
    doc = get_doc_by_link(element)
    if doc is None:
        return "Error."
    return doc_to_html(doc)


def doc_to_html(doc):
    # Extract xml file from zip
    with zipfile.ZipFile(io.BytesIO(doc.XmlContent)) as _zip:
        dom = etree.parse(io.BytesIO(_zip.read(_zip.filelist[0])))

    ext = TableXsltExtension()
    ns = etree.FunctionNamespace("xalan://com.ford.vcc.vida.web.xsltextension.TableXsltExtension")
    ns["getTableNodes"] = ext.get_table_nodes

    # Transform xml doc using xslt template
    doc_type = doc.fkDocumentType
    stylesheet = "servinfo.xsl"
    if doc_type == 2:
        if doc.conditionType == "special_tool":
            stylesheet = "specialtool.xsl"
    elif doc_type in {4, 5}:
        if doc.conditionType == "condition":
            stylesheet = "diagcondition.xsl"
        elif doc.conditionType == "test":
            stylesheet = "diagtest.xsl"
    elif doc_type == 6:
        stylesheet = "bulletin.xsl"
    elif doc_type == 7:
        stylesheet = "installationinstr.xsl"

    xslt = etree.parse(os.path.join(settings.VIDA_XSL_PATH, stylesheet))
    transform = etree.XSLT(xslt)
    html_dom = transform(dom)

    # Add default classes to all elements of a type
    for t, c in (("table", "table table-borderless"), ("td", "px-3"), ("img", "w-100")):
        for e in html_dom.xpath(f"//{t}"):
            e.attrib["class"] = f"{e.attrib.get('class', '')} {c}".strip()

    # Replace classes with bootstrap classes
    html_str = etree.tostring(html_dom.find("div"), pretty_print=True).decode("utf-8")
    for p, r in (
        ("commonText", ""),
        ("commonBold", "fw-bold"),
        ("commonBoldMarginBottom", "fw-bold mb-2"),
        ("para", "mt-2"),
        ("bigTitle", "h3 fw-bold"),
        ("smallTitle", "h5 fw-bold"),
        ("listTitle", "h5"),
        ("internalLinkClass", "mx-1"),
        ("software", "text-decoration-underline text-primary"),
    ):
        html_str = re.sub(rf"\b{p}\b", r, html_str)

    return html_str
