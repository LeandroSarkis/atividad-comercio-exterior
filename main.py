import flet as ft

# ── Paleta de cores ──────────────────────────────────────────────────────────
PRIMARY   = "#0A2540"
ACCENT    = "#00C896"
SURFACE   = "#F5F7FA"
CARD_BG   = "#FFFFFF"
TEXT_MAIN = "#0A2540"
TEXT_SUB  = "#5A6A7A"
ERROR_CLR = "#E53935"
BORDER    = "#D0D8E4"

INCOTERMS = {
    "EXW – Ex Works":                    {"frete_intl": False, "seguro": False},
    "FOB – Free On Board":               {"frete_intl": False, "seguro": False},
    "CFR – Cost and Freight":            {"frete_intl": True,  "seguro": False},
    "CIF – Cost, Insurance & Freight":   {"frete_intl": True,  "seguro": True},
    "CPT – Carriage Paid To":            {"frete_intl": True,  "seguro": False},
    "CIP – Carriage and Insurance Paid": {"frete_intl": True,  "seguro": True},
    "DAP – Delivered At Place":          {"frete_intl": True,  "seguro": True},
    "DDP – Delivered Duty Paid":         {"frete_intl": True,  "seguro": True},
}

# Funçao mestre para converter qualquer formato numérico (BR ou US) com segurança
def to_float(v):
    if v is None:
        return 0.0
    s = str(v).strip()
    if not s:
        return 0.0
    # Se tiver vírgula, limpa o padrão brasileiro (ex: 1.500,00 -> 1500.00)
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)

def calcular_exportacao(dados):
    preco_mercado  = to_float(dados.get("preco_mercado", 0))
    cbs_pct        = to_float(dados.get("cbs_pct", 0)) / 100
    ibs_pct        = to_float(dados.get("ibs_pct", 0)) / 100
    credito_rec    = to_float(dados.get("credito_rec", 0))
    embalagem      = to_float(dados.get("embalagem", 0))
    frete_interno  = to_float(dados.get("frete_interno", 0))
    desembaraco    = to_float(dados.get("desembaraco", 0))
    seguro_interno = to_float(dados.get("seguro_interno", 0))
    outros_custos  = to_float(dados.get("outros_custos", 0))
    taxa_cambio    = to_float(dados.get("taxa_cambio", 1))
    incoterm_key   = dados.get("incoterm", "FOB – Free On Board")
    frete_intl     = to_float(dados.get("frete_intl", 0))
    seguro_intl    = to_float(dados.get("seguro_intl", 0))

    cfg = INCOTERMS.get(incoterm_key, {"frete_intl": False, "seguro": False})

    valor_cbs      = preco_mercado * cbs_pct
    valor_ibs      = preco_mercado * ibs_pct
    total_tributos = valor_cbs + valor_ibs

    custos_internos = float(sum([embalagem, frete_interno, desembaraco, seguro_interno, outros_custos]))

    fob_brl = preco_mercado - credito_rec + custos_internos
    fob_usd = fob_brl / taxa_cambio if taxa_cambio else 0

    fi = frete_intl if cfg["frete_intl"] else 0.0
    si = seguro_intl if cfg["seguro"]    else 0.0

    cif_brl = fob_brl + fi + si
    cif_usd = cif_brl / taxa_cambio if taxa_cambio else 0

    lucro_brl  = fob_brl - preco_mercado
    margem_pct = (lucro_brl / fob_brl * 100) if fob_brl else 0

    return {
        "preco_mercado":   preco_mercado,
        "valor_cbs":       valor_cbs,
        "valor_ibs":       valor_ibs,
        "total_tributos":  total_tributos,
        "credito_rec":     credito_rec,
        "custos_internos": custos_internos,
        "fob_brl":   fob_brl,
        "fob_usd":   fob_usd,
        "fi":        fi,
        "si":        si,
        "cif_brl":   cif_brl,
        "cif_usd":   cif_usd,
        "lucro_brl":   lucro_brl,
        "margem_pct":  margem_pct,
        "taxa_cambio": taxa_cambio,
        "incoterm":    incoterm_key,
    }

def fmt_brl(v):
    return "R$ {:,.2f}".format(v).replace(",","X").replace(".","," ).replace("X",".")

def fmt_usd(v):
    return "$ {:,.2f}".format(v)

def mk_field(label, hint="", prefix="", suffix="", value=""):
    return ft.TextField(
        label=label,
        hint_text=hint or None,
        prefix=ft.Text(prefix) if prefix else None,
        suffix=ft.Text(suffix) if suffix else None,
        value=value,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(color=TEXT_SUB, size=13),
        text_style=ft.TextStyle(color=TEXT_MAIN, weight=ft.FontWeight.W_500),
        expand=True,
        bgcolor=CARD_BG,
    )

def mk_text_field(label):
    return ft.TextField(
        label=label,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=CARD_BG,
        label_style=ft.TextStyle(color=TEXT_SUB, size=13),
        expand=True,
    )

def secao_titulo(texto):
    return ft.Container(
        content=ft.Text(texto, size=14, weight=ft.FontWeight.W_700, color=PRIMARY),
        padding=ft.Padding(top=16, right=0, bottom=4, left=0),
        border=ft.Border(bottom=ft.BorderSide(2, ACCENT)),
    )

def resultado_card(label, valor, destaque=False):
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=11, color=TEXT_SUB),
            ft.Text(valor,
                    size=16 if destaque else 14,
                    weight=ft.FontWeight.W_700,
                    color=ACCENT if destaque else TEXT_MAIN),
        ], spacing=2),
        bgcolor=CARD_BG,
        # LINHA CORRIGIDA AQUI: Mudou para ft.Border.all com parâmetros nomeados
        border=ft.Border.all(width=1, color=BORDER),
        border_radius=10,
        padding=14,
        expand=True,
    )

def main(page: ft.Page):
    page.title  = "App Comex – Cálculo de Exportação"
    page.bgcolor = SURFACE
    page.padding = 0
    page.scroll  = ft.ScrollMode.AUTO

    try:
        page.window.width  = 820
        page.window.height = 900
    except Exception:
        pass

    tela_atual = {"idx": 0}
    resultados = {}

    # ── Campos ───────────────────────────────────────────────────────────────
    f_produto = mk_text_field("Nome do Produto")
    f_ncm     = mk_text_field("Código NCM (ex: 8471.30.19)")
    f_preco   = mk_field("Preço de Mercado Interno", hint="0,00", prefix="R$ ")
    f_cambio  = mk_field("Taxa de Câmbio (USD/BRL)", hint="5,80", prefix="R$ ", value="5.80")

    f_cbs     = mk_field("Alíquota CBS", hint="9.9",  suffix="%", value="9.9")
    f_ibs     = mk_field("Alíquota IBS", hint="17.0", suffix="%", value="17.0")
    f_credito = mk_field("Crédito Tributário Recuperável", hint="0,00", prefix="R$ ", value="0")

    f_embal   = mk_field("Embalagem",      prefix="R$ ", value="0")
    f_fretein = mk_field("Frete Interno",  prefix="R$ ", value="0")
    f_desemb  = mk_field("Desembaraço",    prefix="R$ ", value="0")
    f_seguro  = mk_field("Seguro Interno", prefix="R$ ", value="0")
    f_outros  = mk_field("Outros Custos",  prefix="R$ ", value="0")

    dd_incoterm = ft.Dropdown(
        label="Incoterm",
        options=[ft.dropdown.Option(k) for k in INCOTERMS],
        value="FOB – Free On Board",
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=CARD_BG,
        label_style=ft.TextStyle(color=TEXT_SUB, size=13),
        expand=True,
    )
    f_frete_intl  = mk_field("Frete Internacional",  prefix="R$ ", value="0")
    f_seguro_intl = mk_field("Seguro Internacional", prefix="R$ ", value="0")

    txt_info = ft.Text(
        "Este Incoterm não inclui frete/seguro internacional.",
        color=TEXT_SUB, size=12, italic=True,
    )

    def on_incoterm_change(e):
        cfg = INCOTERMS.get(dd_incoterm.value, {})
        partes = []
        if cfg.get("frete_intl"): partes.append("frete internacional")
        if cfg.get("seguro"):     partes.append("seguro internacional")
        txt_info.value = (
            "Este Incoterm inclui: " + " e ".join(partes) + "."
            if partes else
            "Este Incoterm não inclui frete/seguro internacional."
        )
        page.update()

    dd_incoterm.on_change = on_incoterm_change

    area_resultado = ft.Column([], spacing=10)
    msg_erro = ft.Text("", color=ERROR_CLR, size=12)

    def executar_calculo():
        msg_erro.value = ""
        dados = {
            "preco_mercado":  f_preco.value,
            "cbs_pct":        f_cbs.value,
            "ibs_pct":        f_ibs.value,
            "credito_rec":    f_credito.value,
            "embalagem":      f_embal.value,
            "frete_interno":  f_fretein.value,
            "desembaraco":    f_desemb.value,
            "seguro_interno": f_seguro.value,
            "outros_custos":  f_outros.value,
            "taxa_cambio":    f_cambio.value,
            "incoterm":       dd_incoterm.value,
            "frete_intl":     f_frete_intl.value,
            "seguro_intl":    f_seguro_intl.value,
        }
        
        # Validação inicial dos campos obrigatórios e essenciais
        for key, label, minv in [
            ("preco_mercado", "Preço de Mercado", 0.01),
            ("taxa_cambio",   "Taxa de Câmbio",   0.01),
            ("cbs_pct",       "CBS %",             0),
            ("ibs_pct",       "IBS %",             0),
        ]:
            try:
                v = to_float(dados[key])
                if v < minv: raise ValueError
            except Exception:
                msg_erro.value = f"Valor numérico inválido ou menor que o permitido em: {label}"
                page.update()
                return False

        # Executa o cálculo capturando qualquer erro de digitação dos outros campos
        try:
            res = calcular_exportacao(dados)
        except Exception:
            msg_erro.value = "Erro ao processar valores. Verifique se há letras em campos de número."
            page.update()
            return False
            
        resultados.update(res)
        area_resultado.controls.clear()

        def linha(a, b):
            return ft.Row([
                ft.Text(a, size=12, color=TEXT_SUB, expand=2),
                ft.Text(b, size=12, color=TEXT_MAIN, weight=ft.FontWeight.W_600,
                        expand=2, text_align=ft.TextAlign.RIGHT),
            ])

        area_resultado.controls += [
            ft.Text("📋 Resumo da Exportação", size=16,
                    weight=ft.FontWeight.W_700, color=PRIMARY),
            ft.Text(
                f"Produto: {f_produto.value or '–'}  |  "
                f"NCM: {f_ncm.value or '–'}  |  "
                f"Incoterm: {res['incoterm']}",
                size=11, color=TEXT_SUB,
            ),
            ft.Divider(color=BORDER),
            secao_titulo("Tributos"),
            linha("CBS",                     fmt_brl(res["valor_cbs"])),
            linha("IBS",                     fmt_brl(res["valor_ibs"])),
            linha("Total de Tributos",       fmt_brl(res["total_tributos"])),
            linha("Crédito Recuperável (−)", fmt_brl(res["credito_rec"])),
            secao_titulo("Custos Internos"),
            linha("Custos Internos Totais",  fmt_brl(res["custos_internos"])),
            ft.Divider(color=BORDER),
            ft.Row([
                resultado_card("Preço FOB (BRL)", fmt_brl(res["fob_brl"]), destaque=True),
                resultado_card("Preço FOB (USD)", fmt_usd(res["fob_usd"]), destaque=True),
            ], spacing=10),
            ft.Row([
                resultado_card("Preço CIF/CPT (BRL)", fmt_brl(res["cif_brl"])),
                resultado_card("Preço CIF/CPT (USD)", fmt_usd(res["cif_usd"])),
            ], spacing=10),
            ft.Row([
                resultado_card("Lucro Estimado (BRL)", fmt_brl(res["lucro_brl"])),
                resultado_card("Margem Estimada",      f"{res['margem_pct']:.1f}%"),
            ], spacing=10),
            ft.Divider(color=BORDER),
            ft.Text("ℹ️  Valores estimados para fins de simulação acadêmica.",
                    size=10, color=TEXT_SUB, italic=True),
        ]
        page.update()
        return True

    # ── Stepper ───────────────────────────────────────────────────────────────
    ETAPAS = ["Mercadoria", "Tributos", "Custos", "Incoterm", "Resultado"]
    indicador = ft.Text("", size=13, color=PRIMARY, weight=ft.FontWeight.W_600)

    def mk_card(*controles):
        return ft.Container(
            content=ft.Column(list(controles), spacing=12),
            bgcolor=CARD_BG, border_radius=14, padding=24,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=14,
                                color="#1A000000", offset=ft.Offset(0, 3)),
        )

    blocos = [
        mk_card(
            secao_titulo("1 · Cadastro da Mercadoria"),
            ft.Row([f_produto, f_ncm], spacing=12),
            ft.Row([f_preco,   f_cambio], spacing=12),
        ),
        mk_card(
            secao_titulo("2 · Tributos CBS & IBS"),
            ft.Text("Alíquotas configuráveis conforme reforma tributária "
                    "(normalmente 26–27% combinados).", size=12, color=TEXT_SUB),
            ft.Row([f_cbs, f_ibs], spacing=12),
            f_credito,
        ),
        mk_card(
            secao_titulo("3 · Custos de Exportação"),
            ft.Row([f_embal,  f_fretein], spacing=12),
            ft.Row([f_desemb, f_seguro],  spacing=12),
            f_outros,
        ),
        mk_card(
            secao_titulo("4 · Incoterm"),
            ft.Row([dd_incoterm]),
            txt_info,
            ft.Row([f_frete_intl, f_seguro_intl], spacing=12),
            ft.Text("Informe frete/seguro internacional apenas se aplicável ao Incoterm.",
                    size=11, color=TEXT_SUB, italic=True),
        ),
        mk_card(area_resultado),
    ]

    conteudo = ft.Column([blocos[0]], spacing=16)

    btn_ant  = ft.ElevatedButton("← Anterior", bgcolor=SURFACE, color=PRIMARY,
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    btn_prox = ft.ElevatedButton("Próximo →", bgcolor=PRIMARY, color="#FFFFFF",
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    btn_calc = ft.ElevatedButton("🧮  Calcular Exportação", bgcolor=ACCENT, color="#FFFFFF",
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                  visible=False)
    barra    = ft.ProgressBar(value=0.2, bgcolor=BORDER, color=ACCENT)

    def atualizar():
        idx = tela_atual["idx"]
        conteudo.controls  = [blocos[idx]]
        indicador.value    = f"Etapa {idx+1} de {len(ETAPAS)}: {ETAPAS[idx]}"
        barra.value        = (idx + 1) / len(ETAPAS)
        btn_ant.visible    = idx > 0
        eh_incoterm        = idx == len(ETAPAS) - 2
        btn_calc.visible   = eh_incoterm
        btn_prox.visible   = (idx < len(ETAPAS) - 1) and not eh_incoterm
        page.update()

    def ir_prox(e):
        if tela_atual["idx"] == len(ETAPAS) - 2:
            if not executar_calculo():
                return
        if tela_atual["idx"] < len(ETAPAS) - 1:
            tela_atual["idx"] += 1
        atualizar()

    def ir_ant(e):
        if tela_atual["idx"] > 0:
            tela_atual["idx"] -= 1
        atualizar()

    btn_prox.on_click = ir_prox
    btn_ant.on_click  = ir_ant
    btn_calc.on_click = ir_prox

    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.IMPORT_EXPORT_ROUNDED, color=ACCENT, size=28),
            ft.Column([
                ft.Text("App Comex", size=20, weight=ft.FontWeight.W_700, color="#FFFFFF"),
                ft.Text("Cálculo de Preço de Exportação", size=11, color="#A0B8D0"),
            ], spacing=0),
        ], spacing=12),
        bgcolor=PRIMARY,
        padding=ft.Padding(left=28, right=28, top=18, bottom=18),
    )

    page.add(
        header,
        ft.Container(
            content=ft.Column([
                barra,
                indicador,
                conteudo,
                msg_erro,
                ft.Row([btn_ant, ft.Container(expand=True), btn_calc, btn_prox], spacing=10),
            ], spacing=14),
            padding=ft.Padding(left=24, right=24, top=20, bottom=20),
            expand=True,
        ),
    )
    atualizar()

ft.run(main)