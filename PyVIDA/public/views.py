# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import re
from lxml import etree as ET
import zipfile

from flask import Blueprint, current_app, flash, redirect, render_template, request
from sqlalchemy.sql import or_
from vida_py import ServiceRepoSession, BaseDataSession, DiagRepoSession
from vida_py.service import Document, DocumentProfile
from vida_py.basedata import Engine, ModelYear, Transmission, VehicleModel, VehicleProfile
from vida_py.basedata.scripts import get_valid_profiles_for_selected_builder
from vida_py.diag import get_vin_components

from PyVIDA import settings

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        flash("POSTed.", "success")
        if redirect_url := request.args.get("next"):
            return redirect(redirect_url)
    return render_template("public/home.html")


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")


@blueprint.route("/documents/<profile>/")
def documents(profile):
    with ServiceRepoSession() as _service:
        # profiles = [
        #     e[0]
        #     for e in get_valid_profiles_for_selected_builder(_basedata, profile)
        #
        docs = _service.query(
            Document
        ).outerjoin(
            DocumentProfile, DocumentProfile.fkDocument == Document.id
        ).filter(
            DocumentProfile.profileId == profile
        ).all()
        print(docs)
        return render_template("public/documents.html", documents=docs)


@blueprint.route("/document/<chronicle>/")
def document(chronicle):
    with ServiceRepoSession() as _service:
        document = (
            _service.query(Document).filter(Document.chronicleId == chronicle).first()
        )
    with zipfile.ZipFile(io.BytesIO(document.XmlContent)) as _zip:
        dom = ET.parse(io.BytesIO(_zip.read(_zip.filelist[0])))

    # Transform xml doc using xslt template
    xslt = ET.parse(settings.VIDA_XSL_PATH)
    transform = ET.XSLT(xslt)
    html_dom = transform(dom)

    # Add classes to all elements of a type
    for t, c in (("table", "table table-borderless"), ("td", "px-3"), ("img", "w-100")):
        for e in html_dom.xpath(f"//{t}"):
            e.attrib['class'] = f"{e.attrib.get('class', '')} {c}".strip()

    # Replace classes with bootstrap classes
    html_str = ET.tostring(html_dom.find('div'), pretty_print=True).decode('utf-8')
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
        html_str = re.sub(fr"\b{p}\b", r, html_str)

    # Replace javascript functions
    html_str = re.sub(r"javascript:openLinkDoc\('([\w\d]*)', '([\w\d]*)', '([\w\d]*)', '([\w\d]*)'\)", r"/document/\1", html_str)

    return render_template("public/document.html", content=html_str)
