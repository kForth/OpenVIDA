"""Helpers for querying and shaping VIDA base-data profile values."""

__author__ = "Kestin Goforth"
__copyright__ = "Copyright 2026"
__license__ = "MIT"


from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from vida_py.basedata import (
    BodyStyle,
    BrakeSystem,
    Engine,
    ModelYear,
    SpecialVehicle,
    Steering,
    Transmission,
    VehicleModel,
    VehicleProfile,
)
from vida_py.basedata import Session as BaseDataSession
from vida_py.diag import get_valid_profiles_for_selected

from openvida.utils import with_session


@with_session(BaseDataSession)
def get_valid_profiles(profile: str, *, session: Session | None = None) -> list[str]:
    return [e[0] for e in get_valid_profiles_for_selected(session, profile)]


@with_session(BaseDataSession)
def get_profile_values(
    profiles: str, *, session: Session | None = None
) -> tuple[tuple[str, ...], list[tuple[str | None, ...]]]:
    # These keys should always match the query below.
    profile_keys = (
        "model",
        "engine",
        "transm",
        "body",
        "steering",
        "brake",
        "special",
        "year",
        "id",
    )
    if session is None:
        return profile_keys, []

    query = (
        select(
            VehicleModel.Description,
            Engine.Description,
            Transmission.Description,
            BodyStyle.Description,
            Steering.Description,
            BrakeSystem.Description,
            SpecialVehicle.Description,
            ModelYear.Description,
            VehicleProfile.Id.label("ProfileId"),
            # func.dbo.getProfileFullTitle(VehicleProfile.Id)
        )
        .outerjoin(VehicleModel, VehicleModel.Id == VehicleProfile.fkVehicleModel)
        .outerjoin(ModelYear, ModelYear.Id == VehicleProfile.fkModelYear)
        .outerjoin(Engine, Engine.Id == VehicleProfile.fkEngine)
        .outerjoin(Transmission, Transmission.Id == VehicleProfile.fkTransmission)
        .outerjoin(BodyStyle, BodyStyle.Id == VehicleProfile.fkBodyStyle)
        .outerjoin(Steering, Steering.Id == VehicleProfile.fkSteering)
        .outerjoin(BrakeSystem, BrakeSystem.Id == VehicleProfile.fkBrakeSystem)
        .outerjoin(SpecialVehicle, SpecialVehicle.Id == VehicleProfile.fkSpecialVehicle)
        .subquery()
    )

    profile_values: list[tuple[Any, ...]] = []
    # Execute query in batches of 1000 usage profiles
    for i in range(0, len(profiles), 1000):
        stmt = select(query).filter(query.c.ProfileId.in_(profiles[i : i + 1000]))
        profile_values.extend(tuple(e) for e in session.execute(stmt).all())

    return profile_keys, profile_values
