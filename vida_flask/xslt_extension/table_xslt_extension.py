# Translated from `com.ford.vcc.vida.web.xsltextension.TabelXsltExtension.class`

import traceback

from lxml import etree


class Colspec:
    colnum = ""
    colname = ""
    colwidth = ""
    colsep = ""
    rowsep = ""


class Spanspec:
    spanname = ""
    namest = ""
    namend = ""


class TableXsltExtension:
    row_count: int
    num_colspecs: int
    colspec: list[Colspec]
    root: etree._Element
    more_rows: dict[int, int]
    spanspec: dict[str, Spanspec]

    def get_table_nodes(self, _, els: list[etree._Element]) -> etree._Element:
        try:
            self.row_count = 0
            self.num_colspecs = 0
            self.colspec = []
            self.more_rows = {}
            self.spanspec = {}
            self.root = etree.Element("tableroot")

            doc = els[0]
            self.get_metadata(self.root, doc)
            rows = doc.iter("row")
            row_node = None
            next_node = next(rows)
            while (row_node := next_node) is not None:
                next_node = next(rows, None)  # nit.nextNode()
                colsep = row_node.attrib.get("colsep", None)
                rowsep = row_node.attrib.get("rowsep", None)
                self.write_row(row_node, self.root, colsep, rowsep, next_node is None)
        except Exception:
            traceback.print_exc()
            self.root = etree.Element("tableroot")
            node = etree.SubElement(self.root, "error")
            text = etree.SubElement(node, "p")
            text.text = "An error occured when generating a table"

        return [self.root]

    def get_metadata(self, to_node: etree._Element, n: etree._Element):
        colsep = n.attrib.get("colsep", "1")
        rowsep = n.attrib.get("rowsep", "1")

        if to_node is not None and (e := n.attrib.get("frame", None)) is not None:
            to_node.attrib["frame"] = e

        for n2 in n.iter("tgroup"):
            colsep = n2.attrib.get("colsep", colsep)
            rowsep = n2.attrib.get("rowsep", rowsep)

        width = ""
        total_col_width = 0
        for n2 in n.iter("colspec"):
            colwidth = e if (e := n2.attrib.get("colwidth", None)) is not None else None
            if colwidth is not None and colwidth.endswith("*"):
                colwidth = colwidth[:-1]
                width = "100%"
                total_col_width += float(colwidth)

        count = 0
        rowsep2 = None
        for n2 in n.iter("colspec"):
            cspec = Colspec()

            if (e := n2.attrib.get("colname", None)) is not None:
                cspec.colname = e

            if (e := n2.attrib.get("colnum", None)) is not None:
                cspec.colnum = e

            if count == 0 and cspec.colnum is not None and cspec.colnum != "":
                for _ in range(1, int(cspec.colnum)):
                    cspec2 = Colspec()
                    cspec2.colsep = "1"
                    cspec2.rowsep = "1"
                    self.colspec.append(cspec2)
                    count += 1

            colwidth = e if (e := n2.attrib.get("colwidth", None)) is not None else None
            if colwidth is not None and colwidth.endswith("*"):
                colwidth = colwidth[:-1]
                w = float(colwidth) / total_col_width * 100.0
                colwidth = f"{w:0.0f}%"

            colsep2 = e if (e := n2.attrib.get("colsep", None)) is not None else None
            rowsep2 = e if (e := n2.attrib.get("rowsep", None)) is not None else None

            cspec.colsep = colsep2
            cspec.rowsep = rowsep2
            cspec.colwidth = colwidth
            self.colspec.append(cspec)
            col_node = etree.SubElement(to_node, "col")
            if colwidth is not None:
                col_node.attrib["style"] = f"width:{colwidth};"

            count += 1

        for n2 in n.iter("spanspec"):
            sspec = Spanspec()
            if (e := n2.attrib.get("spanname", None)) is not None:
                sspec.span_name = e
            if (e := n2.attrib.get("namest", None)) is not None:
                sspec.name_start = e
            if (e := n2.attrib.get("nameend", None)) is not None:
                sspec.name_end = e

            if sspec.span_name is not None:
                self.spanspec[sspec.span_name] = sspec

        to_node.attrib["width"] = width
        self.num_colspecs = count

    def get_colspec_pos_by_name(self, name: str) -> int:
        if name is None:
            return 0
        for i, cspec in enumerate(self.colspec):
            if name == cspec.colname:
                return i
        return 0

    def get_empty_td(self, row: etree._Element, specNumber: int) -> etree._Element:
        node = etree.SubElement(row, "td")
        etree.SubElement(node, "ptxt")
        return node

    def get_colspan_td(
        self, row: etree._Element, moreRow: str, specNumberStart: int, specNumberEnd: int
    ) -> etree._Element:
        node = etree.SubElement(row, "td")
        node.attrib["colspan"] = str(specNumberEnd - specNumberStart + 1)
        if moreRow is not None:
            moreRowValue = int(moreRow)
            node.attrib["rowspan"] = str(moreRowValue + 1)

            for i in range(1, moreRowValue + 1):
                insertValue = self.more_rows.get(self.row_count + i)
                if insertValue is None:
                    insertValue = 0

                insertValue = insertValue + specNumberEnd - specNumberStart + 1
                self.more_rows[self.row_count + i] = insertValue

        return node

    def get_td(
        self, row: etree._Element, moreRow: str, specNumber: int
    ) -> etree._Element:
        node = etree.SubElement(row, "td")
        if moreRow is not None:
            moreRowValue = int(moreRow)
            node.attrib["rowspan"] = str(moreRowValue + 1)

            for i in range(1, moreRowValue + 1):
                insertValue = self.more_rows.get(self.row_count + i)
                if insertValue is None:
                    insertValue = 0

                insertValue = insertValue + 1
                self.more_rows[self.row_count + i] = insertValue

        return node

    def get_style(
        self,
        align: str,
        valign: str,
        colsep: str,
        rowsep: str,
        specNumber: int,
        lastRow: bool,
    ) -> str:
        style = ""

        try:
            if colsep is not None:
                csep = colsep
            elif specNumber < len(self.colspec):
                csep = self.colspec[specNumber].colsep
            else:  # if self.num_colspecs == specNumber + 1:
                csep = "0"

            if rowsep is not None:
                rsep = rowsep
            elif specNumber < len(self.colspec):
                rsep = self.colspec[specNumber].rowsep
            else:  # if self.num_colspecs == specNumber + 1:
                rsep = "0"
            if lastRow:
                rsep = "0"

            if csep == "0":
                style = style + " border-right:none;"
            else:
                style = style + " border-right:1px solid #000000;"

            if rsep == "0":
                style = style + " border-bottom:none;"
            else:
                style = style + " border-bottom:1px solid #000000;"

            if align is not None:
                style = style + " text-align:" + align + ";"

            style = style + " vertical-align:" + valign + ";"
        except:
            traceback.print_exc()

        return style

    def adopt_nodes(self, fromNode: etree._Element, toNode: etree._Element):
        toNode.append(fromNode)
        for n2 in fromNode.iter("entry"):
            if len(n2) <= 0:
                entry = etree.SubElement(toNode, "entry")
                etree.SubElement(entry, "ptxt")
            else:
                toNode.append(n2)

    def write_row(
        self,
        no: etree._Element,
        toNode: etree._Element,
        colsep: str,
        rowsep: str,
        lastRow: bool,
    ):
        row = etree.SubElement(toNode, "tr")
        current_counter = self.more_rows.get(self.row_count, 0)
        count = current_counter
        for n2 in no.iter("entry"):
            count += 1
            name_start = n2.attrib.get("namest", None)
            name_end = n2.attrib.get("nameend", None)
            more_row = n2.attrib.get("morerows", None)
            colsep2 = n2.attrib.get("colsep", colsep)
            rowsep2 = n2.attrib.get("rowsep", rowsep)
            colname = n2.attrib.get("colname", None)
            align = n2.attrib.get("align", None)
            valign = n2.attrib.get("valign", "top")

            if sspec := self.spanspec.get(n2.attrib.get("spanname"), False):
                name_start = sspec.name_start
                name_end = sspec.name_end

            if colname is not None:
                for end_pos in range(count, self.get_colspec_pos_by_name(colname)):
                    node = self.get_empty_td(row, count)
                    node.attrib["style"] = self.get_style(
                        align, valign, colsep2, rowsep2, count, lastRow
                    )
                    count += 1
            if (
                count + current_counter == 0
                and name_start is not None
                and colname is None
                and name_end is None
            ):
                start_pos = self.get_colspec_pos_by_name(name_start)

                for _ in range(0, start_pos):
                    node = self.get_empty_td(row, count)
                    node.attrib["style"] = self.get_style(
                        align, valign, colsep2, rowsep2, start_pos, lastRow
                    )
                    count += 1

                node = self.get_td(row, more_row, count)
                node.attrib["style"] = self.get_style(
                    align, valign, colsep2, rowsep2, count, lastRow
                )
                self.adopt_nodes(n2, node)
            elif (
                count + current_counter == 0
                and name_start is not None
                and colname is None
            ):
                start_pos = self.get_colspec_pos_by_name(name_start)
                end_pos = self.get_colspec_pos_by_name(name_end)

                for _ in range(start_pos):
                    node = self.get_empty_td(row, count)
                    node.attrib["style"] = self.get_style(
                        align, valign, colsep2, rowsep2, start_pos, lastRow
                    )
                    count += 1

                count += end_pos - start_pos
                node = self.get_colspan_td(row, more_row, start_pos, end_pos)
                node.attrib["style"] = self.get_style(
                    align, valign, colsep2, rowsep2, start_pos, lastRow
                )
                self.adopt_nodes(n2, node)
            elif name_start is not None and name_end is not None:
                start_pos = self.get_colspec_pos_by_name(name_start)
                end_pos = self.get_colspec_pos_by_name(name_end)
                count += end_pos - start_pos
                node = self.get_colspan_td(row, more_row, start_pos, end_pos)
                node.attrib["style"] = self.get_style(
                    align, valign, colsep2, rowsep2, start_pos, lastRow
                )
                self.adopt_nodes(n2, node)
                row.append(node)
            else:
                node = self.get_td(row, more_row, count)
                node.attrib["style"] = self.get_style(
                    align, valign, colsep2, rowsep2, count, lastRow
                )
                self.adopt_nodes(n2, node)

        for start_pos in (count, self.num_colspecs):
            node = self.get_empty_td(row, count)
            node.attrib["style"] = self.get_style(
                align, valign, colsep2, rowsep2, count, lastRow
            )

        self.row_count += 1
