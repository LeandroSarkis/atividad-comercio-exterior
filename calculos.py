# calculos.py

INCOTERMS = {
    #"EXW – Ex Works":                    {"frete_intl": False, "seguro": False},
    "FOB – Free On Board":               {"frete_intl": False, "seguro": False},
    #"CFR – Cost and Freight":            {"frete_intl": True,  "seguro": False},
    "CIF – Cost, Insurance & Freight":   {"frete_intl": True,  "seguro": True},
    #"CPT – Carriage Paid To":            {"frete_intl": True,  "seguro": False},
    #"CIP – Carriage and Insurance Paid": {"frete_intl": True,  "seguro": True},
    #"DAP – Delivered At Place":          {"frete_intl": True,  "seguro": True},
    #"DDP – Delivered Duty Paid":         {"frete_intl": True,  "seguro": True},
}

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
    # 1. Coleta e tratamento dos dados (conversão para float e taxas em decimais)
    preco_mercado        = to_float(dados.get("preco_mercado", 0))
    aliquota_cbs_ibs     = to_float(dados.get("aliquota", 0)) / 100
    lucro_interno        = to_float(dados.get("lucro_interno", 0)) / 100
    credito_rec          = to_float(dados.get("credito_rec", 0))
    embalagem_interna    = to_float(dados.get("embalagem_interna", 0))
    
    custo_exportacao     = to_float(dados.get("custo_exportacao", 0))
    embalagem_exportacao = to_float(dados.get("embalagem_exportacao", 0))
    lucro_exportacao     = to_float(dados.get("lucro_exportacao", 0)) / 100
    outros_custos        = to_float(dados.get("outros_custos", 0))
    taxa_cambio          = to_float(dados.get("taxa_cambio", 1))
    incoterm_key         = dados.get("incoterm", "FOB – Free On Board")

    # 2. Desfazendo o Preço do Mercado Interno (Retrocesso)
    
    # Remove a alíquota CBS/IBS por dentro (Ex: R$ 122 com 22% de imposto vira R$ 100)
    preco_sem_imposto = preco_mercado / (1 + aliquota_cbs_ibs) if aliquota_cbs_ibs >= 0 else preco_mercado
    
    # Remove a margem de lucro interna para descobrir o custo base do produto
    # Formato "Margem sobre o Preço de Venda" (Ex: se o lucro é 20%, o custo representa 80% do preço)
    custo_base_interno = preco_sem_imposto * (1 - lucro_interno)

    # 3. Ajustes de Exportação (Subtrai o que não vai gastar e os créditos que vai ganhar)
    subtotal1 = custo_base_interno - (credito_rec + embalagem_interna)

    # 4. Adiciona os novos custos logísticos da exportação
    custos_exportacao_totais = float(sum([custo_exportacao, embalagem_exportacao, outros_custos]))
    fob_brl_custo = subtotal1 + custos_exportacao_totais

    # 5. Aplica a nova margem de lucro de exportação (Margem sobre o Preço de Venda)
    # Se o lucro desejado for 15%, dividimos o custo por 0.85 para embutir o lucro corretamente
    if lucro_exportacao < 1:
        fob_brl_venda = fob_brl_custo / (1 - lucro_exportacao)
    else:
        fob_brl_venda = fob_brl_custo  # Evita divisão por zero ou números negativos se o lucro for >= 100%
    
    # 6. Conversão Cambial para Dólar
    fob_usd = fob_brl_venda / taxa_cambio if taxa_cambio > 0 else 0

    # 7. Retorno dos dados calculados
    return {
        "preco_mercado": preco_mercado,
        "aliquota_cbs_ibs": aliquota_cbs_ibs,
        "lucro_interno": lucro_interno,
        "credito_rec": credito_rec,
        "embalagem_interna": embalagem_interna,
        "custo_exportacao": custo_exportacao,
        "embalagem_exportacao": embalagem_exportacao,
        "lucro_exportacao": lucro_exportacao,
        "fob_brl": round(fob_brl_venda, 2),  # Preço de venda final em R$
        "fob_usd": round(fob_usd, 2),        # Preço de venda final em US$
        "taxa_cambio": taxa_cambio,
        "incoterm": incoterm_key,
    }

def fmt_brl(v):
    return "R$ {:,.2f}".format(v).replace(",","X").replace(".","," ).replace("X",".")

def fmt_usd(v):
    return "$ {:,.2f}".format(v)