# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from vida_py.service import Document, DocumentLink
from vida_py.service import Session as ServiceRepoSession

from openvida.utils import with_session


@with_session(ServiceRepoSession)
def get_doc_by_chronicle(chronicle, *, session: ServiceRepoSession = None):
    return session.query(Document).filter(Document.chronicleId == chronicle).first()


def get_doc_by_link(element_from, *, session: ServiceRepoSession = None):
    return (
        session.query(Document)
        .join(DocumentLink, Document.projectDocumentId == DocumentLink.projectDocumentTo)
        .filter(DocumentLink.elementFrom == element_from)
        .first()
    )
