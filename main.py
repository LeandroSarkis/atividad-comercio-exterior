import flet as ft

from calculos import (
    to_float, 
    calcular_exportacao_FOB, 
    calcular_exportacao_CIF, 
    fmt_brl, 
    fmt_usd
)
from constants import (
    PRIMARY, ACCENT, SURFACE, CARD_BG, TEXT_MAIN, TEXT_SUB, TEXT_DIS, 
    ERROR_CLR, BORDER, BORDER_DIS, MUTED_BG, INCOTERM_CONFIG
)
from components import (
    mk_field, mk_text_field, secao_titulo, chip_info, mk_card, 
    resultado_card, linha_res
)

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
    f_produto   = mk_text_field("Nome do Produto", hint="Ex: Café em grãos")
    f_ncm       = mk_text_field("Código NCM", hint="Ex: 0901.11.10")
    f_preco     = mk_field("Preço de Mercado Interno", hint="0,00", prefix="R$ ")
    f_cambio    = mk_field("Taxa de Câmbio (BRL/USD)", hint="5,80", prefix="R$ ")
    f_aliquota  = mk_field("Alíquota CBS + IBS", hint="26,5", suffix="%")
    f_lucro_int = mk_field("Margem de Lucro Interno", hint="15", suffix="%")
    f_credito   = mk_field("Crédito Tributário Recuperável", hint="0,00", prefix="R$ ")

    # ── ETAPA 2 · Custos & Incoterm ───────────────────────────────────────────
    f_embal_int  = mk_field("Embalagem Interna",          hint="0,00", prefix="R$ ")
    f_embal_exp  = mk_field("Embalagem de Exportação",    hint="0,00", prefix="R$ ")
    f_custo_exp  = mk_field("Custos de Exportação",       hint="0,00", prefix="R$ ")
    f_lucro_exp  = mk_field("Margem de Lucro Exportação", hint="10", suffix="%")
    f_outros     = mk_field("Outros Custos",              hint="0,00", prefix="R$ ")

    f_frete_intl  = mk_field("Frete Internacional",  hint="0,00", prefix="R$ ", disabled=True)
    f_seguro_intl = mk_field("Seguro Internacional", hint="0,00", prefix="R$ ", disabled=True)

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
            "preco_mercado":        f_preco.value or "0",
            "aliquota":             f_aliquota.value or "0",
            "lucro_interno":        f_lucro_int.value or "0",
            "credito_rec":          f_credito.value or "0",
            "embalagem_interna":    f_embal_int.value or "0",
            "embalagem_exportacao": f_embal_exp.value or "0",
            "custo_exportacao":     f_custo_exp.value or "0",
            "lucro_exportacao":     f_lucro_exp.value or "0",
            "outros_custos":        f_outros.value or "0",
            "taxa_cambio":          f_cambio.value or "0",
            "incoterm":             chave,
            "frete_internacional":  f_frete_intl.value if (is_cif and f_frete_intl.value) else "0",
            "seguro_internacional": f_seguro_intl.value if (is_cif and f_seguro_intl.value) else "0",
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
                msg_erro.value = f"Valor inválido em: {label} (Obrigatório)"
                page.update()
                return False

        try:
            if is_cif:
                res = calcular_exportacao_CIF(dados)
            else:
                res = calcular_exportacao_FOB(dados)
        except Exception as ex:
            msg_erro.value = f"Erro no cálculo: {ex}"
            page.update()
            return False

        frete_val = res.get("frete_internacional", 0)
        seguro_val = res.get("seguro_internacional", 0)
        fob_brl = res.get("fob_brl", 0)
        fob_usd = res.get("fob_usd", 0)
        taxa = res.get("taxa_cambio", 1)

        cif_brl = fob_brl + frete_val + seguro_val if is_cif else 0
        cif_usd = cif_brl / taxa if (is_cif and taxa > 0) else 0

        preco_brl_label = "Preço CIF (BRL)" if is_cif else "Preço FOB (BRL)"
        preco_usd_label = "Preço CIF (USD)" if is_cif else "Preço FOB (USD)"
        
        preco_brl_val = cif_brl if is_cif else fob_brl
        preco_usd_val = cif_usd if is_cif else fob_usd

        ja_calculou["sim"] = True
        area_resultado.controls.clear()
        
        area_resultado.controls += [
            ft.Text("Resumo da Exportação", size=15, weight=ft.FontWeight.W_700, color=PRIMARY),
            ft.Text(
                f"Produto: {f_produto.value or '–'}   ·   "
                f"NCM: {f_ncm.value or '–'}   ·   "
                f"Incoterm: {chave.split('–')[0].strip()}",
                size=11, color=TEXT_SUB,
            ),
            ft.Divider(color=BORDER, height=1),

            secao_titulo("Tributos & Créditos", ft.Icons.RECEIPT_LONG_ROUNDED),
            linha_res("Alíquota CBS + IBS Base", f"{res.get('aliquota_cbs_ibs', 0)*100:.1f}%"),
            linha_res("Crédito Recuperável (−)", fmt_brl(res.get("credito_rec", 0))),

            secao_titulo("Custos Adicionais (Exportação)", ft.Icons.INVENTORY_2_ROUNDED),
            linha_res("Custos de Exportação", fmt_brl(res.get("custo_exportacao", 0))),
            linha_res("Embalagem de Export.", fmt_brl(res.get("embalagem_exportacao", 0))),
            *(
                [linha_res("Frete Internacional",  fmt_brl(frete_val)),
                 linha_res("Seguro Internacional", fmt_brl(seguro_val))]
                if is_cif else []
            ),

            ft.Divider(color=BORDER, height=1),

            ft.Row([
                resultado_card(preco_brl_label, fmt_brl(preco_brl_val), destaque=True),
                resultado_card(preco_usd_label, fmt_usd(preco_usd_val), destaque=True),
            ], spacing=10),

            ft.Divider(color=BORDER, height=1),
            ft.Text("Valores estimados para fins acadêmicos.",
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
        style=ft.ButtonStyle(bgcolor=SURFACE, color=PRIMARY, shape=ft.RoundedRectangleBorder(radius=8)),
    )
    btn_prox = ft.ElevatedButton(
        content=ft.Text("Próximo →"), 
        style=ft.ButtonStyle(bgcolor=PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8)),
    )
    btn_calc = ft.ElevatedButton(
        content=ft.Text("Calcular Exportação"),
        style=ft.ButtonStyle(bgcolor=ACCENT, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8)),
        visible=False,
    )

    btn_limpar = ft.OutlinedButton(
        content=ft.Text("Limpar Campos"),
        style=ft.ButtonStyle(color=ERROR_CLR, side=ft.BorderSide(1.5, ERROR_CLR), shape=ft.RoundedRectangleBorder(radius=8)),
    )

    def limpar_campos(e):
        idx = tela_atual["idx"]
        if idx == 0:
            f_produto.value, f_ncm.value, f_preco.value, f_cambio.value, f_aliquota.value, f_lucro_int.value, f_credito.value = "", "", "", "", "", "", ""
        elif idx == 1:
            f_embal_int.value, f_embal_exp.value, f_custo_exp.value, f_lucro_exp.value, f_outros.value, f_frete_intl.value, f_seguro_intl.value = "", "", "", "", "", "", ""
            selecionar_incoterm("FOB – Free On Board")

        ja_calculou["sim"] = False
        area_resultado.controls.clear()
        msg_erro.value = ""
        page.update()

    btn_limpar.on_click = limpar_campos

    def atualizar():
        idx = tela_atual["idx"]
        conteudo.controls = [blocos[idx]]
        indicador.value   = f"Etapa {idx + 1} de {len(ETAPAS)}: {ETAPAS[idx]}"
        barra.value       = (idx + 1) / len(ETAPAS)
        
        btn_ant.visible    = idx > 0
        btn_calc.visible   = idx == 1
        btn_prox.visible   = idx == 0
        btn_limpar.visible = idx < 2 
        page.update()

    def ir_prox(e):
        if tela_atual["idx"] < len(ETAPAS) - 1: tela_atual["idx"] += 1
        atualizar()

    def ir_ant(e):
        if tela_atual["idx"] > 0: tela_atual["idx"] -= 1
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
            ft.Container(content=ft.Icon(ft.Icons.IMPORT_EXPORT_ROUNDED, color="#FFFFFF", size=22), bgcolor=ACCENT, border_radius=10, padding=8),
            ft.Column([
                ft.Text("", size=19, weight=ft.FontWeight.W_800, color="#FFFFFF"),
                ft.Text("Simulador de Preço de Exportação", size=11, color="#90AAC4"),
            ], spacing=0, expand=True),
        ], spacing=14),
        bgcolor=PRIMARY, padding=ft.Padding(left=28, right=28, top=16, bottom=16),
    )

    page.add(
        header,
        ft.Container(
            content=ft.Column([
                ft.Row([barra], expand=True),
                indicador,
                conteudo,
                ft.Row([btn_ant, btn_limpar, ft.Container(expand=True), btn_calc, btn_prox], spacing=10),
            ], spacing=14),
            padding=ft.Padding(left=24, right=24, top=18, bottom=24), expand=True,
        ),
    )
    atualizar()

if __name__ == "__main__":
    ft.app(target=main)