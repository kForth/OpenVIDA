# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import os
import re
import zipfile

from click import style
from flask import Blueprint, request, send_file
from lxml import etree
from numpy import require
from sqlalchemy import or_
from vida_py import ServiceRepoSession
from vida_py.basedata import BodyStyle, Engine, ModelYear, PartnerGroup
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import (
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
)
from vida_py.diag import Session as DiagSession
from vida_py.diag import get_valid_profiles_for_selected, get_vin_components
from vida_py.epc import (
    CatalogueComponents,
    ComponentConditions,
    Lexicon,
    PartItems,
)
from vida_py.epc import Session as EpcSession
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py.service import Document, DocumentProfile, Qualifier, DocumentLink, DocumentLinkTitle
from vida_flask import settings

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


@blueprint.route("/decode_vin/<vin>", methods=["GET", "POST"])
def decode_vin(vin):
    if not vin:
        return {}
    with BaseDataSession() as _basedata, DiagSession() as _diag:
        (
            model_id,
            model_str,
            model_year,
            engine_id,
            engine_str,
            transm_id,
            transm_str,
        ) = get_vin_components(_diag, vin)[0]
        return {
            "model": {"id": model_id, "text": model_str},
            "year": {"id": model_year, "text": model_year},
            "engine": {"id": engine_id, "text": engine_str},
            "transmission": {"id": transm_id, "text": transm_str},
        }
    return {}


@blueprint.route("/profiles", methods=["GET", "POST"])
def get_profiles():
    with BaseDataSession() as _basedata:
        profiles = (
            _basedata.query(VehicleProfile)
            .filter_by(**{k: v for k, v in request.args.items() if v is not None})
            .all()
        )
        return [
            {c.name: getattr(e, c.name) for c in e.__table__.columns} for e in profiles
        ]


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


# TODO: getPartProfiles:
# (
#     [
#         _basedata.query(VehicleProfile)
#         .filter(VehicleProfile.Id == e.fkProfile)
#         .one()
#         for e in _epc.query(ComponentConditions)
#         .filter(
#             ComponentConditions.fkCatalogueComponent
#             == component.ParentComponentId
#         )
#         .all()
#     ]
# )


@blueprint.route("/partsForProfile/<profile>", methods=["GET", "POST"])
@blueprint.route("/partsForProfile/<profile>/<int:language>", methods=["GET", "POST"])
def parts_for_profile(profile, language=15):
    with DiagSession() as _diag, EpcSession() as _epc:
        profiles = [e[0] for e in get_valid_profiles_for_selected(_diag, profile)]
        parts = (
            _epc.query(
                CatalogueComponents,
                ComponentConditions,
                PartItems,
                Lexicon,
            )
            .outerjoin(
                ComponentConditions,
                ComponentConditions.fkCatalogueComponent
                == CatalogueComponents.ParentComponentId,
            )
            .outerjoin(PartItems, PartItems.Id == CatalogueComponents.fkPartItem)
            .outerjoin(Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId)
            .filter(
                Lexicon.fkLanguage == language,
                or_(
                    ComponentConditions.fkProfile == None,
                    ComponentConditions.fkProfile.in_(profiles),
                ),
            )
            .order_by(CatalogueComponents.ComponentPath)
            .all()
        )

    _parts = {}
    for comp, cond, part, lexicon in parts:
        if comp.Id not in _parts:
            _parts[comp.Id] = {
                "path": comp.ComponentPath,
                "level": comp.AssemblyLevel,
                "sequence": comp.SequenceId,
                "part": {
                    "id": part.Id,
                    "number": part.ItemNumber,
                    "title": lexicon.Description,
                },
                "profiles": [cond.fkProfile],
            }
        else:
            if cond.fkProfile not in _parts[comp.Id]["profiles"]:
                _parts[comp.Id]["profiles"].append(cond.fkProfile)

    return list(_parts.values())


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
        return _service.query(
            Document
        ).join(
            DocumentLinkTitle, DocumentLinkTitle.fkDocument == Document.id
        ).join(
            DocumentLink, DocumentLink.elementTo == DocumentLinkTitle.element
        ).filter(
            DocumentLink.elementFrom == elememt_from
        ).first()

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

    # Transform xml doc using xslt template
    docType = doc.fkDocumentType
    stylesheet = "servinfo.xsl"
    if docType == 2:
      if doc.conditionType == "special_tool":
        stylesheet = "specialtool.xsl"
    elif docType == 4 or docType == 5:
        if doc.conditionType == "condition":
            stylesheet = "diagcondition.xsl"
        elif doc.conditionType == "test":
            stylesheet = "diagtest.xsl"
    elif docType == 6:
        stylesheet = "bulletin.xsl"
    elif docType == 7:
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
