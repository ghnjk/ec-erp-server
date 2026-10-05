#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: label_page_adapter
@author: jkguo
@create: 2026/10/5
"""

NOTE_LINE_HEIGHT = 14


class LabelPageAdapter(object):
    """
    默认面单：用 Order No 结束一单，备注画在 100×150mm 热敏画布上。
    """

    carrier_names = ()

    def page_matches(self, page_text: str, order: dict) -> bool:
        order_no = str(order.get("platformOrderId") or "")
        if not order_no:
            return False
        text = page_text or ""
        return f"Order No:{order_no}" in text or f"Order No: {order_no}" in text

    def has_continuation_pages(self) -> bool:
        return False

    def is_continuation_page(self, page_text: str) -> bool:
        return False

    def keep_native_page_size(self) -> bool:
        return False

    def note_text_width(self, page_width: float):
        return None

    def note_footer_height(self, note_count: int, page_height: float = 0) -> float:
        return NOTE_LINE_HEIGHT * ((note_count or 0) + 1)


class DbaLabelPageAdapter(LabelPageAdapter):
    """
    DBA：平台订单号确认是哪一单。命中之后，带 Lista de postagem 的明细页和签字页仍属于这一单。
    """

    carrier_names = ("DBA",)

    def page_matches(self, page_text: str, order: dict) -> bool:
        order_no = str(order.get("platformOrderId") or "")
        if not order_no:
            return False
        return order_no in (page_text or "")

    def has_continuation_pages(self) -> bool:
        return True

    def is_continuation_page(self, page_text: str) -> bool:
        return "Lista de postagem" in (page_text or "")

    def keep_native_page_size(self) -> bool:
        return True

    def note_text_width(self, page_width: float):
        return float(page_width)


class MercadoLabelPageAdapter(LabelPageAdapter):
    """
    Mercado：页面上的平台订单号是拆开的，用包裹号匹配。页面保持原尺寸。
    """

    carrier_names = ("Mercado Envíos Agências",)

    def page_matches(self, page_text: str, order: dict) -> bool:
        package_no = str(order.get("packageNo") or "")
        if not package_no:
            return False
        return package_no in (page_text or "")

    def keep_native_page_size(self) -> bool:
        return True

    def note_text_width(self, page_width: float):
        return float(page_width)


_REGISTERED_ADAPTERS = (
    DbaLabelPageAdapter(),
    MercadoLabelPageAdapter(),
)


def get_label_page_adapter(shipping_carrier_name: str) -> LabelPageAdapter:
    name = (shipping_carrier_name or "").strip()
    if not name:
        return LabelPageAdapter()
    folded = name.casefold()
    for adapter in _REGISTERED_ADAPTERS:
        for carrier in adapter.carrier_names:
            if folded == carrier.casefold():
                return adapter
    return LabelPageAdapter()


def group_label_pages(page_texts, orders, adapter: LabelPageAdapter):
    """
    按订单顺序把页面下标分成若干组。无法和订单一一对应时返回 None。
    有延续页的物流在命中订单号后不立刻结束，后续延续页仍归入当前订单。
    """
    groups = []
    current = []
    matched = False
    order_idx = 0
    page_index = 0
    total = len(page_texts)
    while page_index < total:
        if order_idx >= len(orders):
            return None
        text = page_texts[page_index] or ""
        order = orders[order_idx]
        if matched and adapter.has_continuation_pages() and not adapter.is_continuation_page(text):
            groups.append(current)
            current = []
            matched = False
            order_idx += 1
            continue
        current.append(page_index)
        if not matched and adapter.page_matches(text, order):
            matched = True
        if matched and not adapter.has_continuation_pages():
            groups.append(current)
            current = []
            matched = False
            order_idx += 1
        page_index += 1
    if matched and current:
        groups.append(current)
        order_idx += 1
    elif current:
        return None
    if order_idx != len(orders):
        return None
    return groups
