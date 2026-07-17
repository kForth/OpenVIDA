"""Public section, including homepage and signup."""

import io
import os
import re
import zipfile

from lxml import etree
from sqlalchemy.orm import Session
from vida_py.service import Document, DocumentLink
from vida_py.service import Session as ServiceRepoSession

from openvida import settings
from openvida.utils import with_session
from openvida.xslt_extension.table_xslt_extension import TableXsltExtension


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


def document_to_dict(doc: Document | None) -> dict[str, int | str | bool]:
    return {
        "id": doc.id if doc else None,
        "chronicleId": doc.chronicleId if doc else None,
        "projectDocumentId": doc.projectDocumentId if doc else None,
        "fkQualifier": doc.fkQualifier if doc else None,
        "version": doc.version if doc else None,
        "vccNumber": doc.vccNumber if doc else None,
        "nevisId": doc.nevisId if doc else None,
        "IEDate": doc.IEDate if doc else None,
        "fkDocumentType": doc.fkDocumentType if doc else None,
        "conditionType": doc.conditionType if doc else None,
        "path": doc.path if doc else None,
        "title": doc.title if doc else None,
        "hasSibling": doc.hasSibling if doc else None,
    }


def doc_to_html(doc):
    # Extract xml file from zip
    with zipfile.ZipFile(io.BytesIO(doc.XmlContent)) as _zip:
        dom = etree.parse(io.BytesIO(_zip.read(_zip.filelist[0])))

    ext = TableXsltExtension()
    ns = etree.FunctionNamespace("xalan://com.ford.vcc.vida.web.xsltextension.TableXsltExtension")
    ns["getTableNodes"] = ext.get_table_nodes

    # Transform xml doc using xslt template
    doc_type = doc.fkDocumentType
    stylesheet = "servinfo.xsl"
    if doc_type == 2:
        if doc.conditionType == "special_tool":
            stylesheet = "specialtool.xsl"
    elif doc_type in {4, 5}:
        if doc.conditionType == "condition":
            stylesheet = "diagcondition.xsl"
        elif doc.conditionType == "test":
            stylesheet = "diagtest.xsl"
    elif doc_type == 6:
        stylesheet = "bulletin.xsl"
    elif doc_type == 7:
        stylesheet = "installationinstr.xsl"

    xslt = etree.parse(os.path.join(settings.VIDA_XSL_PATH, stylesheet))
    transform = etree.XSLT(xslt)
    html_dom = transform(dom)

    # Add default classes to all elements of a type
    for t, c in (("table", "table table-borderless"), ("td", "px-3"), ("img", "w-100")):
        for e in html_dom.xpath(f"//{t}"):
            e.attrib["class"] = f"{e.attrib.get('class', '')} {c}".strip()

    # Replace classes with bootstrap classes
    html_str = etree.tostring(html_dom.find("div"), pretty_print=True).decode("utf-8")
    for p, r in (
        ("commonText", ""),
        ("commonBold", "fw-bold"),
        ("commonBoldMarginBottom", "fw-bold mb-2"),
        ("para", "mt-2"),
        ("bigTitle", "h3 fw-bold"),
        ("smallTitle", "h5 fw-bold"),
        ("listTitle", "h5"),
        ("internalLinkClass", "mx-1"),
        ("software", "text-decoration-underline text-primary"),
    ):
        html_str = re.sub(rf"\b{p}\b", r, html_str)

    return html_str
