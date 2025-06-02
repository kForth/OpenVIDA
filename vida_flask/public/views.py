# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""


from functools import reduce
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import or_, func, cast, Integer, distinct
from sqlalchemy.orm import aliased
from vida_py.basedata import BodyStyle, Engine, ModelYear, PartnerGroup
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata import (
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
)
from vida_py.epc import (
    AttachmentData,
    CatalogueComponents,
    ComponentAttachments,
    ComponentConditions,
    ComponentDescriptions,
    Lexicon,
    PartItems,
)
from vida_py.epc import Session as EpcSession
from vida_py.images import LocalizedGraphics
from vida_py.images import Session as ImageRepoSession

from vida_flask.vida.api import get_doc_by_link, get_document_html

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
def part_list():
    return render_template("public/parts.html")


@blueprint.route("/parts/<partnumber>")
def part_info(partnumber):

    language = request.args.get("language", False) or 15
    with EpcSession() as _epc:
        part = _epc.query(
            PartItems.ItemNumber,
            Lexicon.Description
        ).join(
            CatalogueComponents, CatalogueComponents.fkPartItem == PartItems.Id
        ).join(
            Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId
        ).join(
            ComponentDescriptions, ComponentDescriptions.fkCatalogueComponent == CatalogueComponents.Id
        ).filter(
            ComponentDescriptions.DescriptionTypeId == 3,
            PartItems.ItemNumber == partnumber,
            Lexicon.fkLanguage == language,
        ).group_by(
            PartItems.ItemNumber,
            Lexicon.Description,
        ).one()

        usages = _epc.query(
            distinct(CatalogueComponents.Id),
            func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            CatalogueComponents.TypeId,
            cast(CatalogueComponents.Quantity, Integer),
            AttachmentData.Code,
            ComponentConditions.fkProfile
        ).outerjoin(
            PartItems, CatalogueComponents.fkPartItem == PartItems.Id
        ).outerjoin(
            ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
        ).outerjoin(
            AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
        ).outerjoin(
            ComponentConditions, ComponentConditions.fkCatalogueComponent == CatalogueComponents.ParentComponentId
        ).filter(
            PartItems.ItemNumber == partnumber
        ).all()

    with BaseDataSession() as _basedata:
        profiles = _basedata.query(
            VehicleProfile.Id,
            func.dbo.getProfileFullTitle(VehicleProfile.Id)
        ).filter(
            VehicleProfile.Id.in_([e[-1] for e in usages])
        ).all()

    return render_template("public/part.html", part=part, usages=usages, profiles=profiles)


@blueprint.route("/resources/")
def resources():
    return render_template("public/resources.html")


@blueprint.route("/documents/")
def documents():
    return render_template("public/documents.html")


@blueprint.route("/document/<chronicle>/")
def document(chronicle):
    doc_html = get_document_html(chronicle)
    if doc_html is None:
        return abort(404)
    return render_template("public/document.html", content=doc_html)

@blueprint.route("/doclink/<element>/")
def document2(element):
    doc = get_doc_by_link(element)
    if doc is None:
        return abort(404)
    return redirect(url_for("public.document", chronicle=doc.chronicleId))
