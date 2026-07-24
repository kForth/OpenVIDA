"""Public page routes for template-rendered views."""

__author__ = "Kestin Goforth"
__copyright__ = "Copyright 2026"
__license__ = "MIT"

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
from vida_py.basedata import Session as BaseDataSession
from vida_py.basedata.models import (
    BodyStyle,
    Engine,
    ModelYear,
    PartnerGroup,
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
)

from openvida.vida import epc, service
from openvida.vida.api import get_epc_part_info

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
@blueprint.route("/parts/<path:path>/")
def part_list(path=""):
    part = epc.get_epc_part_by_path(path, 15)
    return render_template("public/parts.html", path=path, part=part)


@blueprint.route("/part/<partnumber>")
def part_info(partnumber):
    part, applications = get_epc_part_info(partnumber, 15)
    return render_template("public/part.html", part=part, applications=applications)


@blueprint.route("/resources/")
def resources():
    return render_template("public/resources.html")


@blueprint.route("/documents/", defaults={"chronicle": None})
@blueprint.route("/documents/<chronicle>/")
def documents(chronicle):
    doc = service.get_doc_by_chronicle(chronicle) if chronicle else None
    doc_dict = service.document_to_dict(doc)
    return render_template("public/documents.html", document=doc_dict)


@blueprint.route("/document/<chronicle>/")
def document(chronicle):
    doc = service.get_doc_by_chronicle(chronicle)
    doc_html = service.doc_to_html(doc)
    if doc_html is None:
        return abort(404)
    doc_dict = service.document_to_dict(doc)
    return render_template("public/document.html", document=doc_dict, content=doc_html)


@blueprint.route("/doclink/<element>/")
def document2(element):
    doc = service.get_doc_by_link(element)
    if doc is None:
        return abort(404)
    return redirect(url_for("public.document", chronicle=doc.chronicleId))
