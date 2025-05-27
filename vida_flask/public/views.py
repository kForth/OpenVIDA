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
    url_for,
)
from sqlalchemy import or_
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
@blueprint.route("/parts/<partnumber>/<int:language>")
def part_info(partnumber, language=15):
    with BaseDataSession() as _basedata, EpcSession() as _epc, ImageRepoSession() as _images:
        part, title = (
            _epc.query(PartItems, Lexicon)
            .outerjoin(Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId)
            .filter(PartItems.ItemNumber == partnumber, Lexicon.fkLanguage == language)
            .one()
        )
        parent_lex = aliased(Lexicon)
        desc_lex = aliased(Lexicon)
        parent_desc = aliased(ComponentDescriptions)
        comp_desc = aliased(ComponentDescriptions)
        components = (  # profile, component, desc1, desc2, attachment
            _epc.query(
                ComponentConditions.fkProfile,
                CatalogueComponents,
                parent_lex,
                desc_lex,
                AttachmentData.Code,
            )
            .outerjoin(
                ComponentConditions,
                ComponentConditions.fkCatalogueComponent
                == CatalogueComponents.ParentComponentId,
            )
            .outerjoin(
                parent_desc,
                parent_desc.fkCatalogueComponent == CatalogueComponents.ParentComponentId,
            )
            .outerjoin(
                comp_desc,
                comp_desc.fkCatalogueComponent == CatalogueComponents.Id,
            )
            .outerjoin(
                parent_lex,
                parent_lex.DescriptionId == parent_desc.DescriptionId,
            )
            .outerjoin(
                desc_lex,
                desc_lex.DescriptionId == comp_desc.DescriptionId,
            )
            .outerjoin(
                ComponentAttachments,
                ComponentAttachments.fkCatalogueComponent
                == CatalogueComponents.ParentComponentId,
            )
            .outerjoin(
                AttachmentData,
                AttachmentData.Id == ComponentAttachments.fkAttachmentData,
            )
            .filter(
                CatalogueComponents.fkPartItem == part.Id,
                or_(
                    parent_desc.DescriptionId == None,
                    parent_lex.fkLanguage == language,
                ),
                or_(
                    comp_desc.DescriptionId == None,
                    desc_lex.fkLanguage == language,
                ),
            )
            .order_by(CatalogueComponents.Id)
            .all()
        )
        profiles = {
            e.Id: e
            for e in _basedata.query(VehicleProfile)
            .filter(VehicleProfile.Id.in_([e[0] for e in components]))
            .order_by(
                VehicleProfile.fkPartnerGroup,
                VehicleProfile.fkVehicleModel,
                VehicleProfile.fkModelYear,
                VehicleProfile.fkEngine,
                VehicleProfile.fkTransmission,
                VehicleProfile.fkSuspension,
                VehicleProfile.fkSteering,
                VehicleProfile.fkBrakeSystem,
                VehicleProfile.fkBodyStyle,
                VehicleProfile.fkSpecialVehicle,
                VehicleProfile.fkNodeECU,
                VehicleProfile.ChassisNoFrom,
                VehicleProfile.ChassisNoTo,
            )
            .all()
        }
        graphics = {
            g.fkGraphic: g.path
            for g in _images.query(LocalizedGraphics)
            .filter(LocalizedGraphics.fkGraphic.in_([e[-1] for e in components]))
            .all()
        }
        components = [
            (profiles[p], graphics.get(e[-1], None), *e) for p, *e in components
        ]
    return render_template(
        "public/part.html",
        part=part,
        title=title,
        components=components,
    )


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
