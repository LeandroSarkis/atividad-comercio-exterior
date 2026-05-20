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