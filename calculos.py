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
    preco_mercado  = to_float(dados.get("preco_mercado", 0))
    aliquota_cbs_ibs = to_float(dados.get("aliquota", 0)) / 100
    lucro_interno = to_float(dados.get("lucro_interno", 0)) / 100
    credito_rec    = to_float(dados.get("credito_rec", 0))
    embalagem_interna      = to_float(dados.get("embalagem_interna", 0))
    custo_exportacao  = to_float(dados.get("custo_exportacao", 0))
    embalagem_exportacao      = to_float(dados.get("embalagem_exportacao", 0))
    lucro_exportacao     = to_float(dados.get("lucro_exportacao", 0)) / 100
    outros_custos  = to_float(dados.get("outros_custos", 0))
    taxa_cambio    = to_float(dados.get("taxa_cambio", 1))
    incoterm_key   = dados.get("incoterm", "FOB – Free On Board")

    cfg = INCOTERMS.get(incoterm_key, {"frete_intl": False, "seguro": False})

    mercado_interno_sem_aliquotas = (preco_mercado * aliquota_cbs_ibs) / (1 + aliquota_cbs_ibs)

    mercado_interno_sem_lucro = mercado_interno_sem_aliquotas / lucro_interno

    subtotal1 = mercado_interno_sem_lucro - (credito_rec + embalagem_interna)

    custos_internos = float(sum([custo_exportacao, embalagem_exportacao, outros_custos]))

    fob_brl = subtotal1 + custos_internos

    fob_brl_exportacao = fob_brl / lucro_exportacao if lucro_exportacao else 0
    
    fob_usd = fob_brl_exportacao / taxa_cambio if taxa_cambio else 0

    return {
        "preco_mercado":   preco_mercado,
        "aliquota_cbs_ibs": aliquota_cbs_ibs,
        "lucro_interno":   lucro_interno,
        "credito_rec":     credito_rec,
        "embalagem_interna": embalagem_interna,
        "custo_exportacao": custo_exportacao,
        "embalagem_exportacao": embalagem_exportacao,
        "lucro_exportacao": lucro_exportacao,
        "fob_brl":   fob_brl,
        "fob_usd":   fob_usd,
        "taxa_cambio": taxa_cambio,
        "incoterm":    incoterm_key,
    }

def fmt_brl(v):
    return "R$ {:,.2f}".format(v).replace(",","X").replace(".","," ).replace("X",".")

def fmt_usd(v):
    return "$ {:,.2f}".format(v)