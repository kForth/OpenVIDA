# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, request

from PyVIDA.vida.models.basedata import (
    BodyStyle,
    Engine,
    ModelYear,
    PartnerGroup,
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
)

blueprint = Blueprint("vida", __name__, static_folder="../static", url_prefix="/vida")


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
    return [
        e.to_dict()
        for e in VehicleProfile.query.filter_by(
            **{k: v for k, v in request.args.items() if v is not None}
        ).all()
    ]


@blueprint.route("/markets", methods=["GET", "POST"])
def markets():
    return [{"id": e.Id, "text": e.Description} for e in PartnerGroup.query.all()]


@blueprint.route("/modelYears", methods=["GET", "POST"])
def modelYears():
    return [{"id": e.Id, "text": e.Description} for e in ModelYear.query.all()]


@blueprint.route("/models", methods=["GET", "POST"])
def models():
    return [{"id": e.Id, "text": e.Description} for e in VehicleModel.query.all()]


@blueprint.route("/engines", methods=["GET", "POST"])
def engines():
    return [{"id": e.Id, "text": e.Description} for e in Engine.query.all()]


@blueprint.route("/transmissions", methods=["GET", "POST"])
def transmissions():
    return [{"id": e.Id, "text": e.Description} for e in Transmission.query.all()]


@blueprint.route("/steerings", methods=["GET", "POST"])
def steerings():
    return [{"id": e.Id, "text": e.Description} for e in Steering.query.all()]


@blueprint.route("/bodyStyles", methods=["GET", "POST"])
def bodyStyles():
    return [{"id": e.Id, "text": e.Description} for e in BodyStyle.query.all()]


@blueprint.route("/specialVehicles", methods=["GET", "POST"])
def specialVehicles():
    return [{"id": e.Id, "text": e.Description} for e in SpecialVehicle.query.all()]
