import flet as ft

# ── Paleta ───────────────────────────────────────────────────────────────────
PRIMARY   = "#0D1F35"
ACCENT    = "#1AAB6D"
SURFACE   = "#EEF2F7"
CARD_BG   = "#FFFFFF"
TEXT_MAIN = "#0D1F35"
TEXT_SUB  = "#556070"
TEXT_DIS  = "#A0AABB"
ERROR_CLR = "#D32F2F"
BORDER    = "#CBD5E1"
BORDER_DIS= "#E8ECF2"
MUTED_BG  = "#F8FAFC"

INCOTERM_CONFIG = {
    "FOB – Free On Board": {
        "descricao": "Vendedor entrega a bordo do navio. Frete e seguro internacionais ficam por conta do comprador.",
        "cif": False,
    },
    "CIF – Cost, Insurance and Freight": {
        "descricao": "Vendedor arca com frete e seguro internacionais até o porto de destino.",
        "cif": True,
    },
}