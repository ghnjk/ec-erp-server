#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: order_printing
@author: jkguo
@create: 2024/10/6
"""
import os
import threading
import json
import time
from datetime import datetime
from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.app_config import get_app_config, get_static_dir
from ec.bigseller.big_seller_client import BigSellerClient
from ec_erp_api.models.mysql_backend import OrderPrintTask
from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
import logging
import traceback


def append_log_to_task(task: OrderPrintTask, log: str):
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期和时间
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    if task.logs is None:
        task.logs = []
    task.logs.append(f"{formatted_now} - {log}")


class PrintOrderThread(threading.Thread):

    def __init__(self, task: OrderPrintTask, backend: MysqlBackend, client: BigSellerClient):
        super().__init__(daemon=True)
        self.name = f"print-{task.task_id}"
        self.task = task
        self.backend = backend
        self.client = client
        self.pdf_list = []
        self.base_dir = ""
        self.print_pdf_file_path = ""
        self.print_pdf_url = ""
        self.logger = logging.getLogger("ASYNC_TASK")

    def run(self):
        self.log(f"print-task thread {threading.current_thread()} start exec task {self.task.task_id}...")
        self._prepare_base_dir()
        try:
            # 下载所有的PDF
            if self._download_all_order_pdf():
                # 合成PDF
                self._gen_merge_pdf()
                # 添加所有打单编辑
                self._mark_all_order_printed()
                # 设置下载地址
                self.task.current_step = "PDF已生成，请下载并打印"
                self.task.pdf_file_url = self.print_pdf_url
                self._save_task()
        except Exception as e:
            self.log(f"EXCEPTION {self.task.task_id} process async task error: {e}")
            self.logger.error(traceback.format_exc())

    def _download_all_order_pdf(self):
        idx = 0
        for order in self.task.order_list:
            idx += 1
            mark_id = f"{self.task.task_id}{idx + 10000}"
            order_id = order["id"]
            platform = order["platform"]
            picking_notes = order["pickingNotes"]
            self.log(f"downloading order {order_id} platform {platform} mark_id {mark_id}...")
            self.log(json.dumps(picking_notes, ensure_ascii=False))
            origin_pdf_file = os.path.join(self.base_dir, f"{mark_id}.origin.pdf")
            noted_pdf_file = os.path.join(self.base_dir, f"{mark_id}.noted.pdf")
            for i in range(4):
                try:
                    self.client.download_order_mask_pdf_file(order_id, mark_id, platform, origin_pdf_file)
                    break
                except Exception as e:
                    time.sleep(1)
                    self.log(f"下载异常{e}")
                    self.logger.error(traceback.format_exc())
            if os.path.isfile(origin_pdf_file):
                self.task.progress = idx * 100 / len(self.task.order_list)
                append_log_to_task(self.task, f"download order {order_id} pdf success.")
                self._add_note_to_pdf(origin_pdf_file, noted_pdf_file, picking_notes)
                self.pdf_list.append(noted_pdf_file)
                self._save_task()
            else:
                self.task.current_step = "从bigseller下载pdf异常。"
                append_log_to_task(self.task, f"download order {order_id} pdf failed.")
                self._save_task()
                return False
        return True

    def log(self, msg):
        from datetime import datetime
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化日期和时间
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"{formatted_now} ASYNC_TASK >> {self.task.task_id} >> - {msg}")

    def _gen_merge_pdf(self):
        merger = PdfWriter()
        for pdf_file in self.pdf_list:
            reader = PdfReader(pdf_file)
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                merger.add_page(page)
        merger.write(self.print_pdf_file_path)
        self.log(f"合并pdf文件到{self.print_pdf_file_path}")
        append_log_to_task(self.task, f"合并pdf文件到{self.print_pdf_file_path}")

    def _prepare_base_dir(self):
        base_dir = os.path.join(
            get_static_dir(), "print"
        )
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        base_dir = os.path.join(
            base_dir, self.task.task_id
        )
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        self.base_dir = base_dir
        self.print_pdf_file_path = os.path.join(base_dir, f"{self.task.task_id}.all.pdf")
        self.print_pdf_url = f"/print/{self.task.task_id}/{self.task.task_id}.all.pdf"
        return base_dir

    def _save_task(self):
        self.backend.store_order_print_task(self.task)

    def _add_note_to_pdf(self, origin_pdf_file: str, noted_pdf_file: str, picking_notes: dict):
        """
        :param origin_pdf_file:
        :param noted_pdf_file:
        :param picking_notes:[
            {
                            "picking_quantity": "{:.1f}".format(quantity / note.picking_unit),
                            "picking_unit_name": note.picking_unit_name,
                            "picking_sku_name": note.picking_sku_name
            }
        ]
        :return:
        """
        reader = PdfReader(origin_pdf_file)
        writer = PdfWriter()
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            original_width = page.mediabox[2]
            original_height = page.mediabox[3]
            new_height = original_height / 150.0 * 180.0
            transfer_y = new_height - original_height
            page.mediabox.upper_right = (original_width, new_height)
            page.add_transformation(Transformation().translate(0, transfer_y))
            if i == len(reader.pages) - 1:
                # last page
                self._add_mark_to_page(page, original_width, original_height, new_height, picking_notes)
            writer.add_page(page)
        writer.write(noted_pdf_file)

    def _add_mark_to_page(self, page, original_width, original_height, new_height, picking_notes):
        import io
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        # 创建一个 PDF 对象
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(original_width, new_height))
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
        for note in self._format_picking_note(picking_notes):
            p = Paragraph(note, style)
            p.wrapOn(can, 3 * inch, 8 * inch)
            if cnt < 6:
                p.drawOn(can, 0, mark_rect_height - line_height - line_height * cnt)
            else:
                p.drawOn(can, original_width / 2, mark_rect_height - line_height - line_height * (cnt - 6))
            cnt += 1
        can.showPage()
        can.save()
        # 移动到 packet 的开始位置
        packet.seek(0)
        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        return packet

    def _format_picking_note(self, picking_notes: dict):
        """
        :param picking_notes:  [
            {
                            "picking_quantity": "{:.1f}".format(quantity / note.picking_unit),
                            "picking_unit_name": note.picking_unit_name,
                            "picking_sku_name": note.picking_sku_name
            }
        ]
        :return:
        """
        note_list = []
        for note in picking_notes:
            picking_quantity = note["picking_quantity"]
            picking_unit_name = note["picking_unit_name"]
            picking_sku_name = note["picking_sku_name"]
            note_list.append(f" * {picking_quantity} {picking_unit_name} {picking_sku_name}")
        return note_list

    def _mark_all_order_printed(self):
        for order in self.task.order_list:
            try:
                order_id = order["id"]
                self.client.mark_order_printed(order_id)
                self.log(f"订单{order_id}标记【已打印】")
                append_log_to_task(self.task, f"订单{order_id}标记【已打印】")
                self._save_task()
            except Exception as e:
                self.log(e)
