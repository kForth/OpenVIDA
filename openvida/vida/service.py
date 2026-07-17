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
from openvida.vida import const
from openvida.xslt_extension.table_xslt_extension import TableXsltExtension


@with_session(ServiceRepoSession)
def get_doc_by_chronicle(chronicle: str, *, session: Session | None = None) -> Document | None:
    if session is None:
        return None
    return session.query(Document).filter(Document.chronicleId == chronicle).first()


@with_session(ServiceRepoSession)
def get_doc_by_link(element_from: str, *, session: Session | None = None) -> Document | None:
    if session is None:
        return None
    return (
        session.query(Document)
        .join(DocumentLink, Document.projectDocumentId == DocumentLink.projectDocumentTo)
        .filter(DocumentLink.elementFrom == element_from)
        .first()
    )


def document_to_dict(doc: Document | None) -> dict[str, int | str | bool | None]:
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


def dom_to_str(dom):
    if dom is None:
        return None
    return etree.tostring(dom, pretty_print=True).decode("utf-8")


def doc_to_xml(doc):
    if doc is None:
        return None

    # Extract XML file from zip
    with zipfile.ZipFile(io.BytesIO(doc.XmlContent)) as _zip:
        return etree.parse(io.BytesIO(_zip.read(_zip.filelist[0])))


def doc_to_html_raw(doc):
    if doc is None:
        return None

    # Get raw XML from doc
    dom = doc_to_xml(doc)

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
    return transform(dom)


def doc_to_html(doc):
    if doc is None:
        return None

    # Get raw HTML from document XML
    html_dom = doc_to_html_raw(doc)

    # Add default classes to all elements of a type
    for t, c in (("table", "table table-borderless"), ("td", "px-3"), ("img", "w-100")):
        for e in html_dom.xpath(f"//{t}"):
            e.attrib["class"] = f"{e.attrib.get('class', '')} {c}".strip()

    # Convert raw HTML dom to a string
    html_str = etree.tostring(html_dom, pretty_print=True).decode("utf-8")

    # Replace classes with bootstrap classes
    for p, r in const.BOOTSTRAP_CLASSES:
        html_str = re.sub(rf"\b{p}\b", r, html_str)

    # Replace self-closing tags when they shouldn't be self-closing
    # eg: <a name="" />, <td valign="top" width="430 />
    for tag in const.NON_SELF_CLOSING_TAGS:
        html_str = re.sub(rf"<({tag})(\s[^<>]*?)?\s*/>", r"<\1\2></\1>", html_str)

    # Remove div attributes and stylesheet
    for search, replace in const.REPLACE_STRINGS:
        html_str = re.sub(search, replace, html_str)

    return html_str
