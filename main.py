import flet as ft

from calculos import to_float, calcular_exportacao, fmt_brl, fmt_usd

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

# ── Helpers ───────────────────────────────────────────────────────────────────
def mk_field(label, hint="", prefix="", suffix="", value="", expand=True, disabled=False):
    return ft.TextField(
        label=label,
        hint_text=hint or None,
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

def mk_text_field(label, expand=True):
    return ft.TextField(
        label=label,
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


# ═══════════════════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title   = "Comex · Preço de Exportação"
    page.bgcolor = SURFACE
    page.padding = 0
    page.scroll  = ft.ScrollMode.AUTO

    try:
        page.window.width  = 860
        page.window.height = 940
    except Exception:
        pass

    tela_atual  = {"idx": 0}
    ja_calculou = {"sim": False}

    # ── ETAPA 1 · Cadastro & Tributos ─────────────────────────────────────────
    f_produto   = mk_text_field("Nome do Produto")
    f_ncm       = mk_text_field("Código NCM")
    f_preco     = mk_field("Preço de Mercado Interno", hint="0,00", prefix="R$ ")
    f_cambio    = mk_field("Taxa de Câmbio (BRL/USD)", prefix="R$ ", value="5.80")
    f_aliquota  = mk_field("Alíquota CBS + IBS", hint="26.5", suffix="%", value="26.5")
    f_lucro_int = mk_field("Margem de Lucro Interno", hint="15", suffix="%", value="15")
    f_credito   = mk_field("Crédito Tributário Recuperável", prefix="R$ ", value="0")

    # ── ETAPA 2 · Custos & Incoterm ───────────────────────────────────────────
    f_embal_int  = mk_field("Embalagem Interna",          prefix="R$ ", value="0")
    f_embal_exp  = mk_field("Embalagem de Exportação",    prefix="R$ ", value="0")
    f_custo_exp  = mk_field("Custos de Exportação",       prefix="R$ ", value="0")
    f_lucro_exp  = mk_field("Margem de Lucro Exportação", suffix="%",   value="10")
    f_outros     = mk_field("Outros Custos",               prefix="R$ ", value="0")

    # Campos CIF — sempre na tela, habilitados/desabilitados conforme seleção
    f_frete_intl  = mk_field("Frete Internacional",  prefix="R$ ", value="0", disabled=True)
    f_seguro_intl = mk_field("Seguro Internacional", prefix="R$ ", value="0", disabled=True)

    incoterm_selecionado = {"valor": "FOB – Free On Board"}

    incoterm_desc = ft.Text(
        INCOTERM_CONFIG["FOB – Free On Board"]["descricao"],
        size=12, color=TEXT_SUB, italic=True,
    )
    lbl_intl = ft.Text(
        "Frete e seguro internacionais — disponíveis apenas para CIF:",
        size=12, color=TEXT_DIS, italic=True,
    )

    # ── Botões toggle FOB / CIF ───────────────────────────────────────────────
    def _btn_incoterm_style(ativo: bool):
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            bgcolor=PRIMARY if ativo else SURFACE,
            color="#FFFFFF" if ativo else TEXT_SUB,
            side=ft.BorderSide(1.5, PRIMARY if ativo else BORDER),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            overlay_color=ft.Colors.with_opacity(0.08, "#FFFFFF"),
        )

    btn_fob = ft.ElevatedButton(
    content=ft.Text("FOB - Free On Board"),  
    style=_btn_incoterm_style(True),  
    expand=True
)
    btn_cif = ft.ElevatedButton(
    content=ft.Text("CIF - Cost, Insurance"), 
    style=_btn_incoterm_style(False), 
    expand=True
)

    # ── ETAPA 3 · Resultado ───────────────────────────────────────────────────
    area_resultado = ft.Column([], spacing=10)
    msg_erro       = ft.Text("", color=ERROR_CLR, size=12)

    # ── Atualiza visual dos campos CIF ────────────────────────────────────────
    def set_cif_fields(enabled: bool):
        for f in [f_frete_intl, f_seguro_intl]:
            f.disabled     = not enabled
            f.bgcolor      = CARD_BG   if enabled else "#F2F4F8"
            f.border_color = BORDER    if enabled else BORDER_DIS
            f.label_style  = ft.TextStyle(color=TEXT_SUB if enabled else TEXT_DIS, size=12)
            f.text_style   = ft.TextStyle(
                color=TEXT_MAIN if enabled else TEXT_DIS,
                weight=ft.FontWeight.W_500,
            )
            if f.prefix:
                f.prefix = ft.Text("R$ ", color=TEXT_SUB if enabled else TEXT_DIS)
        lbl_intl.color = TEXT_SUB if enabled else TEXT_DIS

    # ── Lógica de seleção do incoterm ─────────────────────────────────────────
    def selecionar_incoterm(chave: str):
        incoterm_selecionado["valor"] = chave
        is_cif = INCOTERM_CONFIG[chave]["cif"]

        btn_fob.style = _btn_incoterm_style(not is_cif)
        btn_cif.style = _btn_incoterm_style(is_cif)

        incoterm_desc.value = INCOTERM_CONFIG[chave]["descricao"]
        set_cif_fields(is_cif)

        if ja_calculou["sim"]:
            executar_calculo()
        else:
            page.update()

    btn_fob.on_click = lambda e: selecionar_incoterm("FOB – Free On Board")
    btn_cif.on_click = lambda e: selecionar_incoterm("CIF – Cost, Insurance and Freight")

    def recalcular_se_possivel(e):
        if ja_calculou["sim"]:
            executar_calculo()

    f_frete_intl.on_change  = recalcular_se_possivel
    f_seguro_intl.on_change = recalcular_se_possivel

    # ── Executar cálculo ───────────────────────────────────────────────────────
    def executar_calculo():
        msg_erro.value = ""

        chave  = incoterm_selecionado["valor"]
        is_cif = INCOTERM_CONFIG[chave]["cif"]

        dados = {
            "preco_mercado":        f_preco.value,
            "aliquota":             f_aliquota.value,
            "lucro_interno":        f_lucro_int.value,
            "credito_rec":          f_credito.value,
            "embalagem_interna":    f_embal_int.value,
            "embalagem_exportacao": f_embal_exp.value,
            "custo_exportacao":     f_custo_exp.value,
            "lucro_exportacao":     f_lucro_exp.value,
            "outros_custos":        f_outros.value,
            "taxa_cambio":          f_cambio.value,
            "incoterm":             chave,
            "frete_intl":           f_frete_intl.value if is_cif else "0",
            "seguro_intl":          f_seguro_intl.value if is_cif else "0",
        }

        validacoes = [
            ("preco_mercado", "Preço de Mercado Interno", 0.01),
            ("taxa_cambio",   "Taxa de Câmbio",           0.01),
            ("aliquota",      "Alíquota CBS+IBS",         0),
            ("lucro_interno", "Margem de Lucro Interno",  0),
        ]
        for key, label, minv in validacoes:
            try:
                v = to_float(dados[key])
                if v < minv:
                    raise ValueError
            except Exception:
                msg_erro.value = f"Valor inválido em: {label}"
                page.update()
                return False

        try:
            res = calcular_exportacao(dados)
        except Exception as ex:
            msg_erro.value = f"Erro no cálculo: {ex}"
            page.update()
            return False

        ja_calculou["sim"] = True
        area_resultado.controls.clear()
        area_resultado.controls += [
            ft.Text("Resumo da Exportação",
                    size=15, weight=ft.FontWeight.W_700, color=PRIMARY),
            ft.Text(
                f"Produto: {f_produto.value or '–'}   ·   "
                f"NCM: {f_ncm.value or '–'}   ·   "
                f"Incoterm: {chave.split('–')[0].strip()}",
                size=11, color=TEXT_SUB,
            ),
            ft.Divider(color=BORDER, height=1),

            secao_titulo("Tributos", ft.Icons.RECEIPT_LONG_ROUNDED),
            linha_res("Alíquota CBS + IBS", f_aliquota.value + "%"),
            linha_res("Valor de Tributos",  fmt_brl(res.get("total_tributos", 0))),
            linha_res("Crédito Recuperável (−)", fmt_brl(res.get("credito_rec", 0))),

            secao_titulo("Custos", ft.Icons.INVENTORY_2_ROUNDED),
            linha_res("Custos Internos Totais", fmt_brl(res.get("custos_internos", 0))),
            linha_res("Custos de Exportação",   fmt_brl(res.get("custo_exportacao", 0))),
            *(
                [linha_res("Frete Internacional",  fmt_brl(res.get("frete_intl", 0))),
                 linha_res("Seguro Internacional", fmt_brl(res.get("seguro_intl", 0)))]
                if is_cif else []
            ),

            ft.Divider(color=BORDER, height=1),

            ft.Row([
                resultado_card("Preço FOB (BRL)", fmt_brl(res.get("fob_brl", 0)), destaque=True),
                resultado_card("Preço FOB (USD)", fmt_usd(res.get("fob_usd", 0)), destaque=True),
            ], spacing=10),
            ft.Row([
                resultado_card("Preço CIF (BRL)", fmt_brl(res.get("cif_brl", 0))),
                resultado_card("Preço CIF (USD)", fmt_usd(res.get("cif_usd", 0))),
            ], spacing=10),
            ft.Row([
                resultado_card("Lucro Estimado (BRL)", fmt_brl(res.get("lucro_brl", 0))),
                resultado_card("Margem Estimada",      f"{res.get('margem_pct', 0):.1f}%"),
            ], spacing=10),

            ft.Divider(color=BORDER, height=1),
            ft.Text("ℹ️  Valores estimados para fins de simulação.",
                    size=10, color=TEXT_SUB, italic=True),
        ]
        page.update()
        return True

    # ── Estrutura de etapas ────────────────────────────────────────────────────
    ETAPAS = ["Cadastro & Tributos", "Custos & Incoterm", "Resultado"]

    bloco_etapa1 = mk_card(
        secao_titulo("Cadastro da Mercadoria", ft.Icons.INVENTORY_ROUNDED),
        ft.Row([f_produto, f_ncm], spacing=12),
        ft.Row([f_preco, f_cambio], spacing=12),

        secao_titulo("Tributação CBS & IBS", ft.Icons.ACCOUNT_BALANCE_ROUNDED),
        chip_info("Conforme reforma tributária. Alíquota combinada típica: 26–27%."),
        ft.Row([f_aliquota, f_lucro_int], spacing=12),
        f_credito,
    )

    bloco_etapa2 = mk_card(
        secao_titulo("Custos de Exportação", ft.Icons.LOCAL_SHIPPING_ROUNDED),
        ft.Row([f_embal_int, f_embal_exp], spacing=12),
        ft.Row([f_custo_exp, f_lucro_exp], spacing=12),
        f_outros,

        secao_titulo("Incoterm", ft.Icons.PUBLIC_ROUNDED),
        ft.Text("Selecione o termo de negociação internacional:",
                size=12, color=TEXT_SUB),
        ft.Row([btn_fob, btn_cif], spacing=10),
        incoterm_desc,
        lbl_intl,
        ft.Row([f_frete_intl, f_seguro_intl], spacing=12),
    )

    bloco_etapa3 = mk_card(
        msg_erro,
        area_resultado,
    )

    blocos = [bloco_etapa1, bloco_etapa2, bloco_etapa3]

    # ── Navegação ─────────────────────────────────────────────────────────────
    conteudo  = ft.Column([blocos[0]], spacing=16)
    indicador = ft.Text("", size=12, color=TEXT_SUB, weight=ft.FontWeight.W_600)
    barra     = ft.ProgressBar(value=1/3, bgcolor=BORDER, color=ACCENT)

    btn_ant = ft.ElevatedButton(
    content=ft.Text("← Anterior"), 
    style=ft.ButtonStyle(
        bgcolor=SURFACE,           
        color=PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=8)
    ),
)
    btn_prox = ft.ElevatedButton(
    content=ft.Text("Próximo →"), 
    style=ft.ButtonStyle(
        bgcolor=PRIMARY,         
        color="#FFFFFF",
        shape=ft.RoundedRectangleBorder(radius=8)
    ),
)
    btn_calc = ft.ElevatedButton(
    content=ft.Text("⚡ Calcular Exportação"),
    style=ft.ButtonStyle(
        bgcolor=ACCENT,            
        color="#FFFFFF",
        shape=ft.RoundedRectangleBorder(radius=8)
    ),
    visible=False,
)

    def atualizar():
        idx = tela_atual["idx"]
        conteudo.controls = [blocos[idx]]
        indicador.value   = f"Etapa {idx + 1} de {len(ETAPAS)}: {ETAPAS[idx]}"
        barra.value       = (idx + 1) / len(ETAPAS)
        btn_ant.visible   = idx > 0
        btn_calc.visible  = idx == 1
        btn_prox.visible  = idx == 0
        page.update()

    def ir_prox(e):
        if tela_atual["idx"] < len(ETAPAS) - 1:
            tela_atual["idx"] += 1
        atualizar()

    def ir_ant(e):
        if tela_atual["idx"] > 0:
            tela_atual["idx"] -= 1
        atualizar()

    def fazer_calculo(e):
        if executar_calculo():
            tela_atual["idx"] = 2
            atualizar()

    btn_prox.on_click = ir_prox
    btn_ant.on_click  = ir_ant
    btn_calc.on_click = fazer_calculo

    # ── Header ────────────────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.IMPORT_EXPORT_ROUNDED, color="#FFFFFF", size=22),
                bgcolor=ACCENT, border_radius=10, padding=8,
            ),
            ft.Column([
                ft.Text("App Comex", size=19, weight=ft.FontWeight.W_800, color="#FFFFFF"),
                ft.Text("Simulador de Preço de Exportação", size=11, color="#90AAC4"),
            ], spacing=0, expand=True),
        ], spacing=14),
        bgcolor=PRIMARY,
        padding=ft.Padding(left=28, right=28, top=16, bottom=16),
    )

    page.add(
        header,
        ft.Container(
            content=ft.Column([
                ft.Row([barra], expand=True),
                indicador,
                conteudo,
                ft.Row([btn_ant, ft.Container(expand=True), btn_calc, btn_prox], spacing=10),
            ], spacing=14),
            padding=ft.Padding(left=24, right=24, top=18, bottom=24),
            expand=True,
        ),
    )
    atualizar()


if __name__ == "__main__":
    ft.app(target=main)