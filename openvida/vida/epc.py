# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from functools import reduce
from operator import iadd

from sqlalchemy import Integer, cast, distinct, func, or_
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

import openvida.vida.basedata as basedata
from openvida.utils import compress_years, with_session


@with_session(EpcSession)
def get_epc_top_level(profile, language, *, session: EpcSession=None):
    valid_profiles = basedata.get_valid_profiles(profile, session=None)
    query = session.query(
        distinct(CatalogueComponents.Id),
        Lexicon.Description,
        CatalogueComponents.AssemblyLevel,
        CatalogueComponents.TypeId,
        CatalogueComponents.ComponentPath,
        AttachmentData.Code,
    ).join(
        Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId
    ).join(
        VirtualToShared, CatalogueComponents.Id == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, 0)
    ).join(
        ComponentConditions, VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent
    ).outerjoin(
        ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
    ).outerjoin(
        AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
    ).filter(
        or_(ComponentConditions.fkProfile is None, ComponentConditions.fkProfile.in_(valid_profiles)),
        Lexicon.fkLanguage == language,
        CatalogueComponents.TypeId == 2,
    ).order_by(
        CatalogueComponents.Id
    ).all()

    cols = ("id", "description", "assemblyLevel", "type", "path", "attachment")
    return [dict(zip(cols, e)) for e in query]

@with_session(EpcSession)
def get_epc_subelements(parent, level, profile, language, *, session: EpcSession=None):
    valid_profiles = basedata.get_valid_profiles(profile, session=None)
    query = session.query(
        distinct(CatalogueComponents.Id),
        Lexicon.Description,
        CatalogueComponents.AssemblyLevel,
        CatalogueComponents.TypeId,
        CatalogueComponents.ComponentPath,
        AttachmentData.Code,
        func.dbo.getSectionDocFootnote(CatalogueComponents.Id, language),
    ).join(
        Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId
    ).join(
        VirtualToShared, CatalogueComponents.Id == func.dbo.fn_SplitWithLevel(VirtualToShared.AlternateComponentPath, level)
    ).join(
        ComponentConditions, VirtualToShared.fkCatalogueComponent == ComponentConditions.fkCatalogueComponent
    ).outerjoin(
        ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
    ).outerjoin(
        AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
    ).filter(
        or_(ComponentConditions.fkProfile is None, ComponentConditions.fkProfile.in_(valid_profiles)),
        Lexicon.fkLanguage == language,
        or_(
            VirtualToShared.fkCatalogueComponent_Parent == parent,
            CatalogueComponents.ParentComponentId == parent
        )
    ).all()
    cols = ("id", "description", "assemblyLevel", "type", "path", "attachment", "note")
    return [dict(zip(cols, e)) for e in query]

@with_session(EpcSession)
def get_epc_parts(parent, language, *, session: EpcSession=None):
    query = session.query(
        distinct(CatalogueComponents.Id),
        func.dbo.GetPartText(CatalogueComponents.Id, language),
        func.dbo.GetPartNotes(CatalogueComponents.Id, language),
        CatalogueComponents.TypeId,
        PartItems.ItemNumber,
        cast(CatalogueComponents.Quantity, Integer),
        CatalogueComponents.HotspotKey,
        AttachmentData.Code,
        CatalogueComponents.ComponentPath
    ).outerjoin(
        PartItems, PartItems.Id == CatalogueComponents.fkPartItem
    ).outerjoin(
        ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
    ).outerjoin(
        AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
    ).filter(
        CatalogueComponents.ParentComponentId == parent
    ).all()
    cols = ("id", "description", "note", "type", "number", "quantity", "key", "attachment", "path")
    return [dict(zip(cols, e)) for e in query]

@with_session(EpcSession)
def get_epc_part_by_path(path, language, *, session: EpcSession=None):
    query = session.query(
        distinct(CatalogueComponents.Id),
        func.dbo.GetPartText(CatalogueComponents.Id, language),
        func.dbo.GetPartNotes(CatalogueComponents.Id, language),
        CatalogueComponents.TypeId,
        PartItems.ItemNumber,
        cast(CatalogueComponents.Quantity, Integer),
        CatalogueComponents.HotspotKey,
        AttachmentData.Code,
        CatalogueComponents.ComponentPath,
        CatalogueComponents.AssemblyLevel
    ).outerjoin(
        PartItems, PartItems.Id == CatalogueComponents.fkPartItem
    ).outerjoin(
        ComponentAttachments, ComponentAttachments.fkCatalogueComponent == CatalogueComponents.Id
    ).outerjoin(
        AttachmentData, AttachmentData.Id == ComponentAttachments.fkAttachmentData
    ).filter(
        CatalogueComponents.ComponentPath == path.replace("/", ",")
    ).one()
    cols = ("id", "description", "note", "type", "number", "quantity", "key", "attachment", "path", "assemblyLevel")
    return dict(zip(cols, query))

@with_session(EpcSession)
def get_part_item(partnumber, language, *, session: EpcSession=None):
    return session.query(
        PartItems.ItemNumber,
        Lexicon.Description,
        PartItems.IsSoftware,
        PartItems.StockRate,
        PartItems.UnitType,
    ).outerjoin(
        Lexicon, Lexicon.DescriptionId == PartItems.DescriptionId
    ).filter(
        PartItems.ItemNumber == partnumber,
        Lexicon.fkLanguage == language,
    ).one()

@with_session(EpcSession)
def get_part_usages(partnumber, language, *, session: EpcSession=None):
    return session.query(
        CatalogueComponents.Id,
        func.dbo.GetPartText(CatalogueComponents.Id, language),
        func.dbo.GetPartNotes(CatalogueComponents.Id, language),
        ComponentConditions.fkProfile,
        func.cast(CatalogueComponents.Quantity, Integer),
        CatalogueComponents.ComponentPath,
    ).outerjoin(
        PartItems, CatalogueComponents.fkPartItem == PartItems.Id
    ).outerjoin(
        ComponentConditions, ComponentConditions.fkCatalogueComponent == CatalogueComponents.ParentComponentId
    ).outerjoin(
        CCPartnerGroup, CCPartnerGroup.fkCatalogueComponent == CatalogueComponents.Id
    ).filter(
        PartItems.ItemNumber == partnumber
    ).all()

@with_session(EpcSession)
def get_epc_part_info(partnumber, language, *, session: EpcSession=None):
    part = get_part_item(partnumber, language, session=session)
    usages = get_part_usages(partnumber, language, session=session)

    usage_profiles = list({e[3] for e in usages})
    profile_keys, profile_values = basedata.get_profile_values(usage_profiles, session=None)

    usage_paths = list(set(reduce(iadd, [e[-1].split(",") for e in usages], [])))
    path_items = session.query(
        distinct(CatalogueComponents.Id),
        Lexicon.Description,
    ).join(
        Lexicon, Lexicon.DescriptionId == CatalogueComponents.DescriptionId
    ).filter(
        CatalogueComponents.Id.in_(usage_paths),
        Lexicon.fkLanguage == language,
    ).all()
    path_names = dict(path_items)
    profile_names = [dict(zip(profile_keys, info)) for info in profile_values]

    usage_tree = {}
    for item in profile_names:
        current = usage_tree
        for i, key in enumerate(profile_keys):
            if i < len(profile_keys) - 2:
                if item[key] not in current:
                    current[item[key]] = {}
                current = current[item[key]]
            if i == len(profile_keys) - 2:
                if item[key] not in current:
                    current[item[key]] = []
                current = current[item[key]]
            if i == len(profile_keys) - 1:
                current.append(item[key])

    def generate_profile_names(tree):
        names = {}
        def _explore_branches(branches, prefix="", i=0):
            if i == len(profile_keys) - 1:
                for id_ in branches:
                    names[id_] = prefix
            elif i == len(profile_keys) - 2:
                prefix_ = prefix + " " + compress_years(branches.keys())
                ids = sum(branches.values(), start=[])
                _explore_branches(ids, prefix_, i+1)
            else:
                for key, branch in branches.items():
                    prefix_ = (prefix + " " + key) if key else prefix
                    _explore_branches(branch, prefix_, i+1)
        _explore_branches(tree)
        return names
    profile_names = generate_profile_names(usage_tree)

    applications = {}
    for (_id, text, note, profile, qty, path) in usages:
        if _id not in applications:
            applications[_id] ={
                "id": _id,
                "profile": profile_names.get(profile, "??"),
                "title": text,
                "note": note or "",
                "qty": qty or 0,
                "path": "/".join(path.split(",")[:-1]),
                "location": " > ".join(path_names.get(int(e), "??") for e in path.split(",")[:1])
            }
    applications = sorted(applications.values(), key=lambda x: x["profile"])

    return part, applications
