from pathlib import Path

from fpdf import FPDF, HTMLMixin
from test.conftest import assert_pdf_equal

HERE = Path(__file__).resolve().parent


class PDF(FPDF, HTMLMixin):
    pass


def test_links(tmp_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=24)
    line_height = 10

    pdf.set_xy(80, 50)
    pdf.cell(
        w=40,
        h=line_height,
        txt="Cell link",
        border=1,
        align="C",
        link="https://github.com/PyFPDF/fpdf2",
    )

    pdf.set_xy(60, 100)
    pdf.write_html('<a href="https://github.com/PyFPDF/fpdf2">Link defined as HTML</a>')

    text = "Text link"
    pdf.text(x=80, y=150, txt=text)
    width = pdf.get_string_width(text)
    pdf.link(
        x=80,
        y=150 - line_height,
        w=width,
        h=line_height,
        link="https://github.com/PyFPDF/fpdf2",
    )

    pdf.add_page()
    link = pdf.add_link()
    pdf.set_link(link, page=1)
    pdf.set_xy(50, 50)
    pdf.cell(
        w=100, h=10, txt="Internal link to first page", border=1, align="C", link=link
    )

    assert_pdf_equal(pdf, HERE / "links.pdf", tmp_path)


def test_link_alt_text(tmp_path):
    """
    It can be tested that the reference file for this test
    has the link description read out loud by the NVDA screen reader
    when opened with Adobe Acrobat Reader.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=24)
    text = "PyFPDF/fpdf2"
    pdf.text(x=80, y=150, txt=text)
    width = pdf.get_string_width(text)
    line_height = 10
    pdf.link(
        x=80,
        y=150 - line_height,
        w=width,
        h=line_height,
        link="https://github.com/PyFPDF/fpdf2",
        alt_text="GitHub repository of the fpdf2 library",
    )
    assert_pdf_equal(pdf, HERE / "link_alt_text.pdf", tmp_path)
