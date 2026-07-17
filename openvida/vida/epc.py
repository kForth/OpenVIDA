"""EPC query helpers for catalogue navigation and part lookups."""

__author__ = "Kestin Goforth"
__copyright__ = "Copyright 2026"
__license__ = "MIT"


from functools import reduce
from operator import iadd
from typing import Any

from sqlalchemy import Integer, cast, distinct, func, or_
from sqlalchemy.orm import Session
from vida_py.epc import (
    AttachmentData,
    CatalogueComponents,
    CCPartnerGroup,
    ComponentAttachments,
    ComponentConditions,
    Lexicon,
    PartItems,
    VirtualToShared,
)
from vida_py.epc import Session as EpcSession

from openvida.utils import compress_years, with_session
from openvida.vida import basedata


@with_session(EpcSession)
def get_epc_top_level(
    profile: str, language: int, *, session: Session | None = None
) -> list[dict[str, int | str]]:
    if session is None:
        return []
    valid_profiles = basedata.get_valid_profiles(profile, session=None)
    query = (
        session.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,
            CatalogueComponents.AssemblyLevel,
            CatalogueComponents.TypeId,
            CatalogueComponents.ComponentPath,
            AttachmentData.Code,
        )
        .join(Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId)
        .join(
            VirtualToShared,
            CatalogueComponents.Id
            == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, 0),
        )
        .join(
            ComponentConditions,
            VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent,
        )
        .outerjoin(
            ComponentAttachments,
            ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id,
        )
        .outerjoin(AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData)
        .filter(
            or_(
                ComponentConditions.fkProfile == None,  # noqa: E711
                ComponentConditions.fkProfile.in_(valid_profiles),
            ),
            Lexicon.fkLanguage == language,
            CatalogueComponents.TypeId == 2,
        )
        .order_by(CatalogueComponents.Id)
        .all()
    )

    cols = ("id", "description", "assemblyLevel", "type", "path", "attachment")
    return [dict(zip(cols, e, strict=True)) for e in query]


@with_session(EpcSession)
def get_epc_subelements(
    parent: int, level: int, profile: str, language: int, *, session: Session | None = None
) -> list[dict[str, int | str]]:
    if session is None:
        return []
    valid_profiles = basedata.get_valid_profiles(profile, session=None)
    query = (
        session.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,
            CatalogueComponents.AssemblyLevel,
            CatalogueComponents.TypeId,
            CatalogueComponents.ComponentPath,
            AttachmentData.Code,
            func.dbo.getSectionDocFootnote(CatalogueComponents.Id, language),
        )
        .join(Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId)
        .join(
            VirtualToShared,
            CatalogueComponents.Id
            == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, level),
        )
        .join(
            ComponentConditions,
            VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent,
        )
        .outerjoin(
            ComponentAttachments,
            ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id,
        )
        .outerjoin(AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData)
        .filter(
            or_(
                ComponentConditions.fkProfile == None,  # noqa: E711
                ComponentConditions.fkProfile.in_(valid_profiles),
            ),
            Lexicon.fkLanguage == language,
            or_(
                VirtualToShared.fkCatalogueComponent_Parent == parent,
                CatalogueComponents.ParentComponentId == parent,
            ),
        )
        .all()
    )
    cols = ("id", "description", "assemblyLevel", "type", "path", "attachment", "note")
    return [dict(zip(cols, e, strict=True)) for e in query]


@with_session(EpcSession)
def get_epc_parts(
    parent: int, language: int, *, session: Session | None = None
) -> list[dict[str, int | str]]:
    if session is None:
        return []
    query = (
        session.query(
            distinct(CatalogueComponents.Id),
            func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            CatalogueComponents.TypeId,
            PartItems.ItemNumber,
            cast(CatalogueComponents.Quantity, Integer),
            CatalogueComponents.HotspotKey,
            AttachmentData.Code,
            CatalogueComponents.ComponentPath,
        )
        .outerjoin(PartItems, PartItems.Id == CatalogueComponents.fkPartItem)
        .outerjoin(
            ComponentAttachments,
            ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id,
        )
        .outerjoin(AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData)
        .filter(CatalogueComponents.ParentComponentId == parent)
        .all()
    )
    cols = ("id", "description", "note", "type", "number", "quantity", "key", "attachment", "path")
    return [dict(zip(cols, e, strict=True)) for e in query]


@with_session(EpcSession)
def get_epc_part_by_path(
    path: str, language: int, *, session: Session | None = None
) -> dict[str, int | str]:
    cols = (
        "id",
        "description",
        "note",
        "type",
        "number",
        "quantity",
        "key",
        "attachment",
        "path",
        "assemblyLevel",
    )
    if not path or session is None:
        return dict.fromkeys(cols, "")
    # TODO: This does not return descriptions
    query = (
        session.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,  # func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            CatalogueComponents.TypeId,
            PartItems.ItemNumber,
            cast(CatalogueComponents.Quantity, Integer),
            CatalogueComponents.HotspotKey,
            AttachmentData.Code,
            CatalogueComponents.ComponentPath,
            CatalogueComponents.AssemblyLevel,
        )
        .outerjoin(PartItems, PartItems.Id == CatalogueComponents.fkPartItem)
        .outerjoin(
            ComponentAttachments,
            ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id,
        )
        .outerjoin(AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData)
        .join(Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId)
        .filter(
            CatalogueComponents.ComponentPath == path.replace("/", ","),
            Lexicon.fkLanguage == language,
        )
        .one()
    )
    return dict(zip(cols, query, strict=True))


@with_session(EpcSession)
def get_part_item(
    partnumber: str, language: int, *, session: Session | None = None
) -> dict[str, str | bool | int]:
    keys = ("itemNumber", "description", "isSoftware", "stockRate", "unitType")
    if session is None:
        return dict.fromkeys(keys, "")
    result = (
        session.query(
            PartItems.ItemNumber,
            Lexicon.Description,
            PartItems.IsSoftware,
            PartItems.StockRate,
            PartItems.UnitType,
        )
        .outerjoin(Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId)
        .filter(
            PartItems.ItemNumber == partnumber,
            Lexicon.fkLanguage == language,
        )
        .one()
    )
    return dict(zip(keys, result, strict=True))


@with_session(EpcSession)
def get_part_usages(
    partnumber: str, language: int, *, session: Session | None = None
) -> list[dict[str, int | str]]:
    keys = ("id", "description", "notes", "profileId", "quantity", "path")
    if session is None:
        return []
    usages = (
        session.query(
            CatalogueComponents.Id,
            func.dbo.GetPartText(CatalogueComponents.Id, language),
            func.dbo.GetPartNotes(CatalogueComponents.Id, language),
            ComponentConditions.fkProfile,
            cast(CatalogueComponents.Quantity, Integer),
            CatalogueComponents.ComponentPath,
        )
        .outerjoin(PartItems, CatalogueComponents.fkPartItem == PartItems.Id)
        .outerjoin(
            ComponentConditions,
            ComponentConditions.fkCatalogueComponent == CatalogueComponents.ParentComponentId,
        )
        .outerjoin(CCPartnerGroup, CCPartnerGroup.fkCatalogueComponent == CatalogueComponents.Id)
        .filter(PartItems.ItemNumber == partnumber)
        .all()
    )
    return [dict(zip(keys, row, strict=True)) for row in usages]


@with_session(EpcSession)
def get_epc_part_info(
    partnumber: str, language: int, *, session: Session | None = None
) -> tuple[dict[str, int | str], list[dict[str, str | int]]]:
    if session is None:
        return ({}, [])
    part = get_part_item(partnumber, language, session=session)
    usages = get_part_usages(partnumber, language, session=session)

    usage_profiles = list({e["profileId"] for e in usages})
    profile_keys, profile_values = basedata.get_profile_values(usage_profiles, session=None)

    usage_paths: list[str] = list(
        set(reduce(iadd, [str(e["path"]).split(",") for e in usages], []))
    )
    path_items = (
        session.query(
            distinct(CatalogueComponents.Id),
            Lexicon.Description,
        )
        .join(Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId)
        .filter(
            CatalogueComponents.Id.in_(usage_paths),
            Lexicon.fkLanguage == language,
        )
        .all()
    )
    path_names: dict[int, str] = dict(path_items)
    profiles: list[dict[str, str | None]] = [
        dict(zip(profile_keys, info, strict=True)) for info in profile_values
    ]

    usage_tree: dict[str | None, dict[str | None, Any]] = {}
    for item in profiles:
        current = usage_tree
        for key in profile_keys:
            val = item[key]
            if val not in current:
                current[val] = {}
            current = current[val]

    def generate_profile_names(tree: dict[str | None, dict[str | None, Any]]) -> dict[str, str]:
        names = {}

        def _explore_branches(branches, prefix="", i=0):
            if i == len(profile_keys) - 1:
                for id_ in branches:
                    names[id_] = prefix
            elif i == len(profile_keys) - 2:
                prefix_ = prefix + " " + compress_years(branches.keys())
                ids = reduce(iadd, (e.keys() for e in branches.values()), [])
                _explore_branches(ids, prefix_, i + 1)
            else:
                for key, branch in branches.items():
                    prefix_ = (prefix + " " + key) if key is not None else prefix
                    _explore_branches(branch, prefix_, i + 1)

        _explore_branches(tree)
        return names

    profile_names: dict[str, str] = generate_profile_names(usage_tree)
    applications: dict[str, dict[str, int | str]] = {}
    for usage in usages:
        _id = str(usage["id"])
        if _id not in applications:
            path = str(usage["path"])
            applications[_id] = {
                "id": _id,
                "profile": profile_names.get(str(usage["profileId"]), "??"),
                "title": usage["description"],
                "note": usage["notes"] or "",
                "qty": usage["quantity"] or 0,
                "path": "/".join(path.split(",")[:-1]),
                "location": " > ".join(path_names.get(int(e), "??") for e in path.split(",")[:1]),
            }

    return part, sorted(applications.values(), key=lambda x: x["profile"])
