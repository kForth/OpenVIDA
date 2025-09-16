# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import os
import re
import zipfile

from flask import Blueprint, abort, request, send_file, url_for, send_from_directory
from lxml import etree
from sqlalchemy import  Integer, cast, desc, distinct, func, or_
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import (
    BodyStyle,
    BrakeSystem,
    Engine,
    ModelYear,
    PartnerGroup,
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
    CCPartnerGroup,
    ComponentAttachments,
    ComponentConditions,
    Lexicon,
    PartItems,
    VirtualToShared
)
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py.service import Session as ServiceRepoSession
from vida_py.service import (
    Document,
    DocumentLink,
    DocumentLinkTitle,
    DocumentProfile,
    Qualifier,
    Resource,
)

from openvida import settings
from openvida.xslt_extension.table_xslt_extension import TableXsltExtension

blueprint = Blueprint("api", __name__, static_folder="../static", url_prefix="/Vida")


@blueprint.route("/DataImages/<path:filename>")
def image_by_path(filename):
    return _send_image(LocalizedGraphics.path == filename)

@blueprint.route("/img/<code>")
def image_by_code(code):
    return _send_image(LocalizedGraphics.fkGraphic == code)

@blueprint.route("/ProfileImg/<profile>")
def profile_img(profile):
    if profile == "null":
        return send_from_directory("static", "img/ProfileImgPlaceholder.png")
    with BaseDataSession() as _basedata:
        path = _basedata.query(
            VehicleModel.ImagePath
        ).outerjoin(
            VehicleProfile, VehicleProfile.fkVehicleModel == VehicleModel.Id
        ).filter(
            VehicleProfile.Id == profile
        ).one()[0]
    return image_by_path(path)

def _send_image(filter):
    with ImagesSession() as _images:
        img = (
            _images.query(LocalizedGraphics)
            .filter(filter)
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
    return send_file(
        io.BytesIO(img.imageData),
        mimetype=f"image/{img_type.description.lower()}",
        as_attachment=request.args.get("Download", False),
        download_name=img.path,
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
        profile = query.order_by(
            desc(VehicleProfile.FolderLevel)
        ).first()
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
            func.dbo.getSectionDocFootnote(CatalogueComponents.Id, language),
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
    cols = ("id", "description", "assemblyLevel", "type", "note")
    return [dict(zip(cols, e)) for e in query]


@blueprint.route("/epc/getParts")
def get_epc_parts():
    language = request.args.get("language", False) or 15
    parent = request.args.get("parentId", False)
    if not parent:
        return abort(400)

    with EpcSession() as _epc:
        query = _epc.query(
            distinct(CatalogueComponents.Id),
            func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            CatalogueComponents.TypeId,
            PartItems.ItemNumber,
            cast(CatalogueComponents.Quantity, Integer),
            CatalogueComponents.HotspotKey,
            AttachmentData.Code,
        ).outerjoin(
            PartItems, PartItems.Id == CatalogueComponents.fkPartItem
        ).outerjoin(
            ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
        ).outerjoin(
            AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
        ).filter(
            CatalogueComponents.ParentComponentId == parent
        ).all()
    cols = ("id", "description", "note", "type", "number", "quantity", "key", "attachment")
    return [dict(zip(cols, e)) for e in query]

@blueprint.route("/epc/part/<partnumber>")
def get_epc_part_info(partnumber):
    language = request.args.get("language", False) or 15

    # Base.metadata.bind = engine

    with EpcSession() as _epc:
        part = _epc.query(
            PartItems.ItemNumber,
            Lexicon.Description,
            PartItems.IsSoftware,
            PartItems.StockRate,
            PartItems.UnitType,
        ).outerjoin(
            Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId
        ).filter(
            PartItems.ItemNumber == partnumber,
            Lexicon.fkLanguage == language,
        ).one()

        usages = _epc.query(
            CatalogueComponents.Id,
            func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            ComponentConditions.fkProfile,
            func.cast(CatalogueComponents.Quantity, Integer),
        ).outerjoin(
            PartItems, CatalogueComponents.fkPartItem == PartItems.Id
        ).outerjoin(
            ComponentConditions, ComponentConditions.fkCatalogueComponent == CatalogueComponents.ParentComponentId
        ).outerjoin(
            CCPartnerGroup, CCPartnerGroup.fkCatalogueComponent == CatalogueComponents.Id
        ).filter(
            PartItems.ItemNumber == partnumber
        ).all()
        usage_profiles = set([e[3] for e in usages])

    with BaseDataSession() as _basedata:
        profile_vals = _basedata.query(
            VehicleProfile.Id,
            VehicleModel.Description,
            ModelYear.Description,
            Engine.Description,
            Transmission.Description,
            BodyStyle.Description,
            Steering.Description,
            BrakeSystem.Description,
            SpecialVehicle.Description,
            # func.dbo.getProfileFullTitle(VehicleProfile.Id)
        ).outerjoin(
            VehicleModel, VehicleModel.Id == VehicleProfile.fkVehicleModel
        ).outerjoin(
            ModelYear, ModelYear.Id == VehicleProfile.fkModelYear
        ).outerjoin(
            Engine, Engine.Id == VehicleProfile.fkEngine
        ).outerjoin(
            Transmission, Transmission.Id == VehicleProfile.fkTransmission
        ).outerjoin(
            BodyStyle, BodyStyle.Id == VehicleProfile.fkBodyStyle
        ).outerjoin(
            Steering, Steering.Id == VehicleProfile.fkSteering
        ).outerjoin(
            BrakeSystem, BrakeSystem.Id == VehicleProfile.fkBrakeSystem
        ).outerjoin(
            SpecialVehicle, SpecialVehicle.Id == VehicleProfile.fkSpecialVehicle
        ).filter(
            VehicleProfile.Id.in_(usage_profiles)
        ).all()
        profile_names = dict([
            (_id, ", ".join([e for e in info if e]))
            for _id, *info in profile_vals
        ])
        applciations = sorted([
            {
                "id": _id,
                "profile": profile_names[profile],
                "title": text,
                "note": note or "",
                "qty": qty or 0
            }
            for (_id, text, note, profile, qty) in usages
        ], key=lambda x: x["profile"])

    return {
        "part": part,
        "applications": applciations
    }

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


def get_doc_by_link(element_from):
    with ServiceRepoSession() as _service:
        return (
            _service.query(Document)
            .join(DocumentLink, Document.projectDocumentId == DocumentLink.projectDocumentTo)
            .filter(DocumentLink.elementFrom == element_from)
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
        return "Error."
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
