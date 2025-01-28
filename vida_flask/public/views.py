# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""


from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
)
from vida_py import ServiceRepoSession
from vida_py.basedata import BodyStyle, Engine, ModelYear, PartnerGroup
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import SpecialVehicle, Steering, Transmission, VehicleModel
from vida_py.diag import Session as DiagSession
from vida_py.diag import get_valid_profiles_for_selected
from vida_py.service import Document, DocumentProfile, Qualifier

from vida_flask.vida.api import get_document_html

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


@blueprint.route("/profile/", methods=["GET", "POST"])
def profile_select():
    """Profile select page."""
    if request.method == "POST":
        flash("POSTed.", "success")
        if redirect_url := request.args.get("next"):
            return redirect(redirect_url)

    with BaseDataSession() as _basedata:
        return render_template(
            "public/profile.html",
            markets=_basedata.query(PartnerGroup).all(),
            modelYears=sorted(
                _basedata.query(ModelYear).all(),
                key=lambda e: e.Description,
                reverse=True,
            ),
            vehicleModels=_basedata.query(VehicleModel).all(),
            bodyStyles=_basedata.query(BodyStyle).all(),
            engines=_basedata.query(Engine).all(),
            specialVehicles=_basedata.query(SpecialVehicle).all(),
            steerings=_basedata.query(Steering).all(),
            transmissions=_basedata.query(Transmission).all(),
        )


@blueprint.route("/parts/")
def parts():
    return render_template("public/parts.html")


@blueprint.route("/documents/")
def documents():
    return render_template("public/documents.html")


@blueprint.route("/document/<chronicle>/")
def document(chronicle):
    doc_html = get_document_html(chronicle)
    if doc_html is None:
        return abort(404)

    return render_template("public/document.html", content=doc_html)
