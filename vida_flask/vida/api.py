# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import os
import re
import zipfile

from flask import Blueprint, abort, request, send_file, url_for
from lxml import etree
from sqlalchemy import desc, distinct, func, or_
from vida_py import ServiceRepoSession
from vida_py.basedata import BodyStyle, Engine, ModelYear, PartnerGroup
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import (
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
    get_vin_components_by_partner_group_id
)
from vida_py.diag import Session as DiagSession
from vida_py.diag import get_valid_profiles_for_selected
from vida_py.epc import Session as EpcSession
from vida_py.epc import (
    AttachmentData,
    CatalogueComponents,
    ComponentAttachments,
    ComponentConditions,
    Lexicon,
    PartItems,
    VirtualToShared
)
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py.service import (
    Document,
    DocumentLink,
    DocumentLinkTitle,
    DocumentProfile,
    Qualifier,
    Resource,
)

from vida_flask import settings
from vida_flask.xslt_extension.table_xslt_extension import TableXsltExtension

blueprint = Blueprint("api", __name__, static_folder="../static", url_prefix="/Vida")


@blueprint.route("/DataImages/<path:filename>")
def image(filename):
    with ImagesSession() as _images:
        img = (
            _images.query(LocalizedGraphics)
            .filter(LocalizedGraphics.path == filename)
            .one()
        )
        img_type = (
            _images.query(GraphicFormats)
            .outerjoin(
                Graphics,
                Graphics.fkGraphicFormat == GraphicFormats.id,
            )
            .filter(Graphics.id == img.fkGraphic)
            .one()
        )
    if request.args.get("AsPage", False):
        return send_file(
            io.BytesIO(img.imageData),
            mimetype=f"image/{img_type.description.lower()}",
            as_attachment=False,
        )
    return send_file(
        io.BytesIO(img.imageData),
        mimetype=f"image/{img_type.description.lower()}",
        as_attachment=True,
        download_name=filename,
    )


@blueprint.route("/decode_vin/")
def decode_vin():
    vin = request.args.get('vinNumber', False)
    partnerGroup = int(request.args.get('partnerGroup', 1001))
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
        transm_cid
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


@blueprint.route("/profiles", methods=["GET", "POST"])
def get_profiles():
    with BaseDataSession() as _basedata:
        query = _basedata.query(VehicleProfile)
        if (val := request.args.get("fkPartnerGroup", None)) is not None:
            query = query.filter(
                or_(
                    VehicleProfile.fkPartnerGroup == val,
                    VehicleProfile.fkPartnerGroup == None,
                )
            )
        if (val := request.args.get("fkVehicleModel", None)) is not None:
            query = query.filter(
                or_(
                    VehicleProfile.fkVehicleModel == val,
                    VehicleProfile.fkVehicleModel == None,
                )
            )
        if (val := request.args.get("fkModelYear", None)) is not None:
            query = query.filter(
                or_(VehicleProfile.fkModelYear == val, VehicleProfile.fkModelYear == None)
            )
        if (val := request.args.get("fkEngine", None)) is not None:
            query = query.filter(
                or_(VehicleProfile.fkEngine == val, VehicleProfile.fkEngine == None)
            )
        if (val := request.args.get("fkTransmission", None)) is not None:
            query = query.filter(
                or_(
                    VehicleProfile.fkTransmission == val,
                    VehicleProfile.fkTransmission == None,
                )
            )
        if (val := request.args.get("fkSteering", None)) is not None:
            query = query.filter(
                or_(VehicleProfile.fkSteering == val, VehicleProfile.fkSteering == None)
            )
        if (val := request.args.get("fkBodyStyle", None)) is not None:
            query = query.filter(
                or_(VehicleProfile.fkBodyStyle == val, VehicleProfile.fkBodyStyle == None)
            )
        if (val := request.args.get("fkSpecialVehicle", None)) is not None:
            query = query.filter(
                or_(
                    VehicleProfile.fkSpecialVehicle == val,
                    VehicleProfile.fkSpecialVehicle == None,
                )
            )

        profile = query.order_by(
            desc(VehicleProfile.FolderLevel)
        ).first()
        return {c.name: getattr(profile, c.name) for c in profile.__table__.columns}


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
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(ModelYear).all()
        ]


@blueprint.route("/vehicleModels", methods=["GET", "POST"])
def get_vehicle_models():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(VehicleModel).all()
        ]


@blueprint.route("/engines", methods=["GET", "POST"])
def get_engines():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(Engine).all()
        ]


@blueprint.route("/transmissions", methods=["GET", "POST"])
def get_transmissions():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(Transmission).all()
        ]


@blueprint.route("/steerings", methods=["GET", "POST"])
def get_steerings():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(Steering).all()
        ]


@blueprint.route("/bodyStyles", methods=["GET", "POST"])
def get_body_styles():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(BodyStyle).all()
        ]


@blueprint.route("/specialVehicles", methods=["GET", "POST"])
def get_special_vehicles():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(SpecialVehicle).all()
        ]


@blueprint.route("/epc/topLevelToc/")
def get_epc_top_level():
    language = request.args.get("language", False) or 15
    profile = request.args.get("selectedProfile", False)
    if not profile:
        return abort(400)

    with BaseDataSession() as _basedata:
        valid_profiles = [e[0] for e in get_valid_profiles_for_selected(_basedata, profile)]
    with EpcSession() as _epc:
        query = _epc.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,
            CatalogueComponents.AssemblyLevel,
            CatalogueComponents.TypeId,
            CatalogueComponents.ComponentPath,
        ).join(
            Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId
        ).join(
            VirtualToShared, CatalogueComponents.Id == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, 0)
        ).join(
            ComponentConditions, VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent
        ).filter(
            or_(ComponentConditions.fkProfile is None, ComponentConditions.fkProfile.in_(valid_profiles)),
            CatalogueComponents.TypeId == 2,
            Lexicon.fkLanguage == language
        ).order_by(
            CatalogueComponents.Id
        ).all()

    cols = ("id", "description", "assemblyLevel", "type", "path")
    return [dict(zip(cols, e)) for e in query]


@blueprint.route("/epc/getTocElements")
def get_epc_subelements():
    language = request.args.get("language", False) or 15
    parent = request.args.get("parentId", False)
    level = request.args.get("assemblyLevel", False)
    profile = request.args.get("selectedProfile", False)
    if not profile or not parent:
        return abort(400)

    with BaseDataSession() as _basedata:
        valid_profiles = [e[0] for e in get_valid_profiles_for_selected(_basedata, profile)]
    with EpcSession() as _epc:
        query = _epc.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,
            CatalogueComponents.AssemblyLevel,
            CatalogueComponents.TypeId,
        ).join(
            Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId
        ).join(
            VirtualToShared, CatalogueComponents.Id == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, level)
        ).join(
            ComponentConditions, VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent
        ).filter(
            or_(ComponentConditions.fkProfile is None, ComponentConditions.fkProfile.in_(valid_profiles)),
            Lexicon.fkLanguage == language,
            or_(
                VirtualToShared.fkCatalogueComponent_Parent == parent,
                CatalogueComponents.ParentComponentId == parent
            )
        ).all()
    cols = ("id", "description", "assemblyLevel", "type")
    return [dict(zip(cols, e)) for e in query]

@blueprint.route("/resources/")
def resources():
    with ServiceRepoSession() as _service:
        res = _service.query(Resource).all()
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "type": doc.type.Title,
                "url": url_for('api.resource_file', id_=doc.id)
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
            _service.query(Qualifier.id, Qualifier.title)
            .order_by(Qualifier.qualifierCode)
            .all()
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
            _docs = [
                dict(zip(("chronicleId", "title"), e[:2]))
                for e in docs
                if e[2] == qual[0]
            ]
            if _docs:
                docs_by_qual.append(
                    {
                        "qual": dict(zip(("id", "title"), qual)),
                        "docs": _docs,
                    }
                )
    return docs_by_qual


def get_doc_by_chronicle(chronicle):
    with ServiceRepoSession() as _service:
        return _service.query(Document).filter(Document.chronicleId == chronicle).first()


def get_doc_by_link(elememt_from):
    with ServiceRepoSession() as _service:
        return (
            _service.query(Document)
            .join(DocumentLinkTitle, DocumentLinkTitle.fkDocument == Document.id)
            .join(DocumentLink, DocumentLink.elementTo == DocumentLinkTitle.element)
            .filter(DocumentLink.elementFrom == elememt_from)
            .first()
        )


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
        return None
    return doc_to_html(doc)


def doc_to_html(doc):
    # Extract xml file from zip
    with zipfile.ZipFile(io.BytesIO(doc.XmlContent)) as _zip:
        dom = etree.parse(io.BytesIO(_zip.read(_zip.filelist[0])))

    ext = TableXsltExtension()
    ns = etree.FunctionNamespace(
        "xalan://com.ford.vcc.vida.web.xsltextension.TableXsltExtension"
    )
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
