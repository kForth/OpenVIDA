# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import re
import zipfile

from flask import Blueprint, abort, request, send_file
from lxml import etree
from vida_py.basedata import BodyStyle, Engine, ModelYear, PartnerGroup
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import (
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
)
from vida_py.images import GraphicFormats, Graphics, LocalizedGraphics
from vida_py.images import Session as ImagesSession
from vida_py import ServiceRepoSession
from vida_py.service import Document

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
def profiles():
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
def markets():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(PartnerGroup).all()
        ]


@blueprint.route("/modelYears", methods=["GET", "POST"])
def modelYears():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(ModelYear).all()
        ]


@blueprint.route("/models", methods=["GET", "POST"])
def models():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(VehicleModel).all()
        ]


@blueprint.route("/engines", methods=["GET", "POST"])
def engines():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(Engine).all()
        ]


@blueprint.route("/transmissions", methods=["GET", "POST"])
def transmissions():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(Transmission).all()
        ]


@blueprint.route("/steerings", methods=["GET", "POST"])
def steerings():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(Steering).all()
        ]


@blueprint.route("/bodyStyles", methods=["GET", "POST"])
def bodyStyles():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description} for e in _basedata.query(BodyStyle).all()
        ]


@blueprint.route("/specialVehicles", methods=["GET", "POST"])
def specialVehicles():
    with BaseDataSession() as _basedata:
        return [
            {"id": e.Id, "text": e.Description}
            for e in _basedata.query(SpecialVehicle).all()
        ]

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
