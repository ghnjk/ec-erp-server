#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: test
@author: jkguo
@create: 2024/9/30
"""
from ec.bigseller.big_seller_client import BigSellerClient
from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from PyPDF2.generic import AnnotationBuilder


# def main():
#     c = BigSellerClient("KIMKm_rwaaZ_mb5xplP0mmytEBQEzeZhWhFFdhpPmts",
#                         cookies_file_path="cookies/big_seller.cookies")
#     c.login("1036543883@qq.com",
#             "0e7243fff9ec44329f2f6a299937bde7e3f9e90df559f2077ff578a70865dd42607c8d9ca826bf02e9d5be57f7c95455c235b7ba2fe49910ec68698e970089d524055")
#     c.test_print_order()


def add_mark_to_page(page, original_width, original_height, new_height):
    import io
    # 创建一个 PDF 对象
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(original_width, new_height))
    # 在 PDF 上添加文本
    picking_quantity = "{:<5}".format("10")
    picking_unit_name = "{:>4s}".format("pcs")
    picking_sku_name = "{:<10s}".format("G-10-YELLOW")
    text = f" * {picking_quantity} {picking_unit_name} {picking_sku_name}"

    ###
    from reportlab.lib.units import mm, inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.graphics.barcode import code128
    import reportlab.lib.styles
    style_sheet = getSampleStyleSheet()
    style = style_sheet['Heading4']
    # style.fontSize = 14
    # style.leading = 10
    # style.firstLineIndent = 22
    line_height = 12
    cnt = 0
    mark_rect_height = new_height - original_height
    can.setFillColorRGB(0.7, 0.7, 0.7)
    can.rect(0, 0, original_width, mark_rect_height, fill=1)

    for i in range(12):
        line = text
        if len(line) == 0:
            continue
        p = Paragraph(line, style)
        p.wrapOn(can, 3 * inch, 8 * inch)
        if i < 6:
            p.drawOn(can, 0, mark_rect_height - line_height - line_height * cnt)
        else:
            p.drawOn(can, original_width / 2, mark_rect_height - line_height - line_height * (cnt - 6))
        cnt += 1

    can.showPage()
    #
    # can.acroForm.textfield(text, maxlen=original_width, x=0, y=original_height, width=original_width,
    #                        height=(new_height - original_height))
    #
    can.save()

    # 移动到 packet 的开始位置
    packet.seek(0)

    overlay = PdfReader(packet).pages[0]

    page.merge_page(overlay)
    return packet


def process_and_mark_pdf(merger, mark_order_dir, pdf_file_name):
    origin_path = f"{mark_order_dir}/{pdf_file_name}"
    reader = PdfReader(origin_path)
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        print(page.mediabox)
        print(f"page {i} text:")
        print(page.extract_text())
        print("----")
        original_width = page.mediabox[2]
        original_height = page.mediabox[3]
        new_height = original_height / 150.0 * 180.0
        transfer_y = new_height - original_height
        page.mediabox.upper_right = (original_width, new_height)
        page.add_transformation(Transformation().translate(0, transfer_y))
        if i == len(reader.pages) - 1:
            # last page
            add_mark_to_page(page, original_width, original_height, new_height)
        merger.add_page(page)


def main():
    mark_order_dir = f"data/pdf/1727665065662500"
    all_pdf_path = f"{mark_order_dir}/all.pdf"
    merger = PdfWriter()
    process_and_mark_pdf(merger, mark_order_dir,
                         "two.pdf")
    process_and_mark_pdf(merger, mark_order_dir,
                         "one.pdf")
    merger.write(all_pdf_path)
    merger.close()


if __name__ == '__main__':
    main()
