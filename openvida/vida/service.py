"""Public section, including homepage and signup."""

from sqlalchemy.orm import Session
from vida_py.service import Document, DocumentLink
from vida_py.service import Session as ServiceRepoSession

from openvida.utils import with_session


@with_session(ServiceRepoSession)
def get_doc_by_chronicle(chronicle: str, *, session: Session | None = None) -> Document | None:
    return session.query(Document).filter(Document.chronicleId == chronicle).first()


def get_doc_by_link(element_from: str, *, session: Session | None = None) -> Document | None:
    return (
        session.query(Document)
        .join(DocumentLink, Document.projectDocumentId == DocumentLink.projectDocumentTo)
        .filter(DocumentLink.elementFrom == element_from)
        .first()
    )
