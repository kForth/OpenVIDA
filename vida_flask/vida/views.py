# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import re
import zipfile

from flask import Blueprint, request, send_file
from lxml import etree
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
from vida_py.diag import get_valid_profiles_for_selected
from vida_py.epc import (
    CatalogueComponents,
    ComponentConditions,
    ComponentDescriptions,
    Lexicon,
    PartItems,
)
from vida_py.epc import Session as EpcSession
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py.service import Document, DocumentProfile, Qualifier

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
    return send_file(
        io.BytesIO(img.imageData),
        mimetype=f"image/{img_type.description.lower()}",
        as_attachment=True,
        download_name=filename,
    )


@blueprint.route("/profiles_from_vin", methods=["GET", "POST"])
def get_vin_profiles():
    vin = request.args.get("vin", None)
    if not vin:
        return []
    # VINDecodeVariant
    # VINDecodeModel
    # VINVariantCodes
    return []


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


@blueprint.route("/markets", methods=["GET", "POST"])
def get_markets():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(PartnerGroup).all()
        ]


@blueprint.route("/modelYears", methods=["GET", "POST"])
def get_model_years():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(ModelYear).all()
        ]


@blueprint.route("/models", methods=["GET", "POST"])
def get_models():
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
def parts_for_profile(profile):

    with BaseDataSession() as _basedata, DiagSession() as _diag, EpcSession() as _epc:
        language = 15  # TODO

        profiles = [
            e[0] for e in get_valid_profiles_for_selected(_diag, profile)
        ]  # (ID, FolderLevel)

        profile = (
            _basedata.query(VehicleProfile).filter(VehicleProfile.Id == profile).first()
        )
        if profile is None:
            return []

        """
        SELECT * FROM CatalogueComponents
        LEFT JOIN PartItems ON PartItems.Id = CatalogueComponents.fkPartItem
        LEFT JOIN ComponentConditions ON ComponentConditions.fkCatalogueComponent = CatalogueComponents.Id
        WHERE ComponentConditions.fkProfile IN (
        SELECT Id FROM [basedata].[dbo].[VehicleProfile]
        WHERE (fkVehicleModel = 1006 OR fkVehicleModel IS NULL)
        AND (fkModelYear = 1190 OR fkModelYear IS NULL)
        AND (fkEngine = 1074 OR fkEngine IS NULL)
        AND (fkTransmission= 1033 OR fkTransmission IS NULL)
        AND (fkSteering = 1001 OR fkSteering IS NULL)
        AND (fkBodyStyle = 1004 OR fkBodyStyle IS NULL)
        AND (fkPartnerGroup = 1001 OR fkPartnerGroup IS NULL)
        )
        """
        profiles = [
            e[0]
            for e in (
                _basedata.query(VehicleProfile.Id)
                .filter(
                    or_(
                        profile.fkVehicleModel is None,
                        VehicleProfile.fkVehicleModel is None,
                        profile.fkVehicleModel == VehicleProfile.fkVehicleModel,
                    ),
                    or_(
                        profile.fkModelYear is None,
                        VehicleProfile.fkModelYear is None,
                        profile.fkModelYear == VehicleProfile.fkModelYear,
                    ),
                    or_(
                        profile.fkEngine is None,
                        VehicleProfile.fkEngine is None,
                        profile.fkEngine == VehicleProfile.fkEngine,
                    ),
                    or_(
                        profile.fkTransmission is None,
                        VehicleProfile.fkTransmission is None,
                        profile.fkTransmission == VehicleProfile.fkTransmission,
                    ),
                    or_(
                        profile.fkSteering is None,
                        VehicleProfile.fkSteering is None,
                        profile.fkSteering == VehicleProfile.fkSteering,
                    ),
                    or_(
                        profile.fkBodyStyle is None,
                        VehicleProfile.fkBodyStyle is None,
                        profile.fkBodyStyle == VehicleProfile.fkBodyStyle,
                    ),
                    or_(
                        profile.fkPartnerGroup is None,
                        VehicleProfile.fkPartnerGroup is None,
                        profile.fkPartnerGroup == VehicleProfile.fkPartnerGroup,
                    ),
                )
                .all()
            )
        ]

        components = (
            _epc.query(CatalogueComponents)
            .outerjoin(PartItems, PartItems.Id == CatalogueComponents.fkPartItem)
            .outerjoin(
                ComponentConditions,
                ComponentConditions.fkCatalogueComponent == CatalogueComponents.Id,
            )
            .filter(ComponentConditions.fkProfile.in_(profiles))
            .all()
        )

        # part = _epc.query(PartItems).filter(PartItems.ItemNumber == partnumber).one()
        # title = (
        #     _epc.query(Lexicon)
        #     .filter(
        #         Lexicon.DescriptionId == part.DescriptionId,
        #         Lexicon.fkLanguage == language,
        #     )
        #     .one()
        # )
        parts = [
            {
                # "part": {
                #     "id": part.Id,
                #     "code": part.Code,
                #     "itemNumber": part.ItemNumber,
                #     "isSoftware": part.IsSoftware,
                #     "stockRate": part.StockRate,
                #     "unitType": part.UnitType,
                # },
                "component": {
                    "id": comp.Id,
                    # "title": comp,
                },
                "descriptions": [
                    # {}
                    # for desc in _epc.query(Lexicon)
                    # .outerjoin(
                    #     ComponentDescriptions,
                    #     ComponentDescriptions.DescriptionId == Lexicon.DescriptionId,
                    # )
                    # .filter(
                    #     Lexicon.fkLanguage == language,
                    #     ComponentDescriptions.fkCatalogueComponent
                    #     == part.CatalogueComponents.Id,
                    # )
                    # .all()
                ],
            }
            for comp in components
        ]
    return parts


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


@blueprint.route("/docHtml/<chronicle>/", methods=["GET", "POST"])
def get_document_html(chronicle):
    with ServiceRepoSession() as _service:
        doc = _service.query(Document).filter(Document.chronicleId == chronicle).first()
    if doc is None:
        return None

    # Extract xml file from zip
    with zipfile.ZipFile(io.BytesIO(doc.XmlContent)) as _zip:
        dom = etree.parse(io.BytesIO(_zip.read(_zip.filelist[0])))

    # Transform xml doc using xslt template
    xslt = etree.parse(settings.VIDA_XSL_PATH)
    transform = etree.XSLT(xslt)
    html_dom = transform(dom)

    # Add classes to all elements of a type
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

    # Replace javascript functions
    html_str = re.sub(
        r"javascript:openLinkDoc\('([\w\d]*)', '([\w\d]*)', '([\w\d]*)', '([\w\d]*)'\)",
        r"/document/\1",
        html_str,
    )
    return html_str
