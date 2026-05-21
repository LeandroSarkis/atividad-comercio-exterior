import flet as ft
from constants import (
    PRIMARY, ACCENT, CARD_BG, TEXT_MAIN, TEXT_SUB, TEXT_DIS, 
    BORDER, BORDER_DIS, MUTED_BG
)

def mk_field(label, hint="", prefix="", suffix="", value="", expand=True, disabled=False):
    return ft.TextField(
        label=label,
        hint_text=hint or None,
        hint_style=ft.TextStyle(color=TEXT_DIS) if hint else None,
        prefix=ft.Text(prefix, color=TEXT_DIS if disabled else TEXT_SUB) if prefix else None,
        suffix=ft.Text(suffix, color=TEXT_DIS if disabled else TEXT_SUB) if suffix else None,
        value=value,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER_DIS if disabled else BORDER,
        focused_border_color=ACCENT,
        disabled=disabled,
        label_style=ft.TextStyle(color=TEXT_DIS if disabled else TEXT_SUB, size=12),
        text_style=ft.TextStyle(
            color=TEXT_DIS if disabled else TEXT_MAIN,
            weight=ft.FontWeight.W_500,
        ),
        expand=expand,
        bgcolor="#F2F4F8" if disabled else CARD_BG,
        border_radius=8,
    )

def mk_text_field(label, hint="", expand=True):
    return ft.TextField(
        label=label,
        hint_text=hint or None,
        hint_style=ft.TextStyle(color=TEXT_DIS) if hint else None,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=CARD_BG,
        label_style=ft.TextStyle(color=TEXT_SUB, size=12),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        expand=expand,
        border_radius=8,
    )

def secao_titulo(texto, icon=None):
    row_controls = []
    if icon:
        row_controls.append(ft.Icon(icon, color=ACCENT, size=16))
    row_controls.append(
        ft.Text(texto, size=13, weight=ft.FontWeight.W_700, color=PRIMARY)
    )
    return ft.Container(
        content=ft.Row(row_controls, spacing=8),
        padding=ft.Padding(top=8, right=0, bottom=6, left=0),
        border=ft.Border(bottom=ft.BorderSide(1.5, ACCENT)),
        margin=ft.Margin(top=4, bottom=4, left=0, right=0),
    )

def chip_info(texto):
    return ft.Container(
        content=ft.Text(texto, size=11, color=TEXT_SUB, italic=True),
        bgcolor=MUTED_BG,
        border=ft.Border.all(1, BORDER),
        border_radius=6,
        padding=ft.Padding(left=10, right=10, top=6, bottom=6),
    )

def mk_card(*controles, padding=24):
    return ft.Container(
        content=ft.Column(list(controles), spacing=12),
        bgcolor=CARD_BG,
        border_radius=14,
        padding=padding,
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=18,
            color="#14000000", offset=ft.Offset(0, 4),
        ),
    )

def resultado_card(label, valor, destaque=False):
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=11, color=TEXT_SUB),
            ft.Text(
                valor,
                size=17 if destaque else 14,
                weight=ft.FontWeight.W_700,
                color=ACCENT if destaque else TEXT_MAIN,
            ),
        ], spacing=3),
        bgcolor="#F0FBF6" if destaque else MUTED_BG,
        border=ft.Border.all(width=1.5, color=ACCENT if destaque else BORDER),
        border_radius=10,
        padding=14,
        expand=True,
    )

def linha_res(label, valor):
    return ft.Row([
        ft.Text(label, size=12, color=TEXT_SUB, expand=3),
        ft.Text(valor, size=12, color=TEXT_MAIN, weight=ft.FontWeight.W_600,
                expand=2, text_align=ft.TextAlign.RIGHT),
    ])