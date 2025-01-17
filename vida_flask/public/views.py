# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import io
import re
import zipfile

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
)
from lxml import etree
from vida_py import ServiceRepoSession
from vida_py.service import Document, DocumentProfile

from vida_flask import settings

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
        docs = (
            _service.query(Document)
            .outerjoin(DocumentProfile, DocumentProfile.fkDocument == Document.id)
            .filter(DocumentProfile.profileId == profile)
            .all()
        )
        print(docs)
        return render_template("public/documents.html", documents=docs)


@blueprint.route("/document/<chronicle>/")
def document(chronicle):
    with ServiceRepoSession() as _service:
        doc = _service.query(Document).filter(Document.chronicleId == chronicle).first()
    if not doc:
        return abort(404)

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

    return render_template("public/document.html", content=html_str)
