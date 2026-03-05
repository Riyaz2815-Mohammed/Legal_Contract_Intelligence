import docx
from docx.opc.constants import RELATIONSHIP_TYPE, CONTENT_TYPE
from docx.opc.packuri import PackURI
from docx.opc.part import XmlPart
import xml.etree.ElementTree as ET
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import sys

def test():
    document = docx.Document()
    comments_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"></w:comments>'
    
    try:
        from docx.opc.part import XmlPart
        from docx.oxml import parse_xml
        comments_part = XmlPart(
            PackURI('/word/comments.xml'), 
            CONTENT_TYPE.WML_COMMENTS, 
            parse_xml(comments_xml.encode('utf-8')), 
            document.part.package
        )
        document.part.relate_to(comments_part, RELATIONSHIP_TYPE.COMMENTS)
        print("Success adding part")
    except Exception as e:
        print("Error adding part:", e)
        return

    comment_id_str = "0"
    
    # Create comment element using OxmlElement
    comment_elem = OxmlElement('w:comment')
    comment_elem.set(qn('w:id'), comment_id_str)
    comment_elem.set(qn('w:author'), "Author")
    
    c_p = OxmlElement('w:p')
    c_r = OxmlElement('w:r')
    c_t = OxmlElement('w:t')
    c_t.text = "This is a comment"
    
    c_r.append(c_t)
    c_p.append(c_r)
    comment_elem.append(c_p)

    comments_part.element.append(comment_elem)

    p = document.add_paragraph("This is some text with a comment.")
    
    comment_start = OxmlElement('w:commentRangeStart')
    comment_start.set(qn('w:id'), comment_id_str)
    p._p.insert(0, comment_start)

    comment_end = OxmlElement('w:commentRangeEnd')
    comment_end.set(qn('w:id'), comment_id_str)
    p._p.append(comment_end)

    comment_ref_r = OxmlElement('w:r')
    comment_ref = OxmlElement('w:commentReference')
    comment_ref.set(qn('w:id'), comment_id_str)
    comment_ref_r.append(comment_ref)
    p._p.append(comment_ref_r)
    
    document.save('test_comment_out.docx')
    print("Saved docx")

if __name__ == '__main__':
    test()
