from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Cm, RGBColor

def create_doc():
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri (Body)'

    # Set orientation to landscape
    section = doc.sections[-1]
    old_width, old_height = section.page_width, section.page_height
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_height = old_width
    section.page_width = old_height

    # Set the margins
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)