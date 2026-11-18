"""Calculos energeticos do modulo de energia do Citizen Assist AI.

Necessidade estudada: agua quente para o banho em residencias da area da
Enel SP que usam chuveiro eletrico.

Alternativas comparadas para a mesma necessidade e o mesmo periodo (1 ano):
  Situacao atual  chuveiro eletrico, tempo de banho atual
  Alternativa A   eficiencia sem investimento: banho mais curto
  Alternativa B   fonte renovavel: aquecedor solar de agua com o chuveiro
                  eletrico como apoio nos dias de pouco sol
  Alternativa A+B as duas medidas juntas

Somente biblioteca padrao. Os parametros e suas fontes estao em
dados/parametros.json.
"""

import json
import os

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]
DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PARAMETROS = os.path.join(_RAIZ, "dados", "parametros.json")


def carregar_parametros(caminho=CAMINHO_PARAMETROS):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Conceitos basicos: energia = potencia x tempo
# ---------------------------------------------------------------------------

def energia_kwh(potencia_w, horas):
    """E (kWh) = P (kW) x t (h)."""
    if potencia_w < 0 or horas < 0:
        raise ValueError("potencia e tempo nao podem ser negativos")
    return potencia_w / 1000.0 * horas


def consumo_chuveiro_mensal(potencia_w, minutos_banho, pessoas,
                            banhos_por_pessoa_dia=1):
    """Consumo eletrico do chuveiro em cada mes (kWh), considerando os dias
    de cada mes. Devolve uma lista com 12 valores."""
    if pessoas <= 0 or minutos_banho <= 0 or banhos_por_pessoa_dia <= 0:
        raise ValueError("pessoas, minutos e banhos devem ser positivos")
    horas_por_dia = minutos_banho / 60.0 * pessoas * banhos_por_pessoa_dia
    return [energia_kwh(potencia_w, horas_por_dia * d) for d in DIAS_MES]


def elevacao_temperatura_c(potencia_w, vazao_l_min, calor_especifico=4.186,
                           densidade=1.0):
    """Quanto o chuveiro aquece a agua: dT = P / (m_ponto x c).

    Serve para conferir se a potencia e a vazao adotadas fazem sentido
    fisicamente (um banho morno exige elevar a agua uns 15 a 25 graus)."""
    if vazao_l_min <= 0:
        raise ValueError("a vazao deve ser positiva")
    vazao_kg_s = vazao_l_min * densidade / 60.0
    return potencia_w / (vazao_kg_s * calor_especifico * 1000.0)


# ---------------------------------------------------------------------------
# Aquecedor solar
# ---------------------------------------------------------------------------

def fracao_solar_fchart(carga_kwh, dias, irradiacao_kwh_m2_dia, temp_ambiente_c,
                        coletor):
    """Fracao solar de um mes pelo metodo f-chart (Duffie e Beckman, cap. 20).

    O f-chart estima, para um mes, que parte da carga termica e coberta pelo
    sol a partir de dois numeros adimensionais:
      X = perdas do coletor no mes / carga do mes
      Y = energia solar absorvida no mes / carga do mes
      f = 1,029Y - 0,065X - 0,245Y^2 + 0,0018X^2 + 0,0215Y^3
    A correlacao ja embute a variacao de sol de um dia para o outro, por isso
    a fracao solar nunca chega a 100% com folga, como acontece na pratica.

    'coletor' e um dicionario com: area_m2, fr_ta_n, fr_ul_w_m2k,
    razao_ta (angulo de incidencia), temp_agua_quente_c,
    volume_por_area_l_m2. A agua da rede e suposta na temperatura media do ar.
    """
    if carga_kwh <= 0:
        return 0.0
    if dias <= 0 or coletor["area_m2"] <= 0:
        raise ValueError("dias e area devem ser positivos")
    segundos = dias * 86400.0
    carga_j = carga_kwh * 3.6e6
    ta = temp_ambiente_c
    x = (coletor["area_m2"] * coletor["fr_ul_w_m2k"] * (100.0 - ta) * segundos
         / carga_j)
    # Correcao do volume de armazenamento (padrao do metodo: 75 L/m2)
    x *= (coletor["volume_por_area_l_m2"] / 75.0) ** -0.25
    # Correcao para aquecimento de agua de consumo (agua da rede = ar)
    tw = coletor["temp_agua_quente_c"]
    x *= (11.6 + 1.18 * tw + 3.86 * ta - 2.32 * ta) / (100.0 - ta)
    y = (coletor["area_m2"] * coletor["fr_ta_n"] * coletor["razao_ta"]
         * irradiacao_kwh_m2_dia * 3.6e6 * dias / carga_j)
    f = 1.029 * y - 0.065 * x - 0.245 * y ** 2 + 0.0018 * x ** 2 + 0.0215 * y ** 3
    return min(FRACAO_SOLAR_MAXIMA, max(0.0, f))


# Premissa do grupo: mesmo com o sistema folgado, sempre sobra alguma
# necessidade de apoio (sequencias de dias nublados). Tambem evita usar a
# correlacao fora da faixa em que foi ajustada (Y ate 3).
FRACAO_SOLAR_MAXIMA = 0.95

# Faixa de uso do kit de referencia do SINAPI (insumo 34472).
BANHOS_DIA_KIT = (4, 5)


def fora_da_faixa_do_kit(pessoas, banhos_por_pessoa_dia=1):
    """-1 se a casa usa menos banhos que o kit foi feito para atender,
    1 se usa mais, 0 se esta dentro da faixa."""
    banhos = pessoas * banhos_por_pessoa_dia
    if banhos < BANHOS_DIA_KIT[0]:
        return -1
    if banhos > BANHOS_DIA_KIT[1]:
        return 1
    return 0


def calor_solar_mensal(demanda_mensal, irradiacao_mensal, temperatura_mensal,
                       coletor):
    """Calor util do aquecedor solar em cada mes (kWh) = f x carga."""
    return [fracao_solar_fchart(demanda_mensal[i], DIAS_MES[i], irradiacao_mensal[m],
                                temperatura_mensal[m], coletor) * demanda_mensal[i]
            for i, m in enumerate(MESES)]


def apoio_eletrico_mensal(demanda_mensal, solar_mensal):
    """Energia que o chuveiro eletrico ainda precisa fornecer (kWh/mes).

    O chuveiro e uma resistencia: praticamente toda a energia eletrica vira
    calor na agua, por isso o apoio eletrico e igual ao calor que falta."""
    return [max(0.0, d - s) for d, s in zip(demanda_mensal, solar_mensal)]


def fracao_solar(demanda_mensal, apoio_mensal):
    total = sum(demanda_mensal)
    return 0.0 if total == 0 else 1.0 - sum(apoio_mensal) / total


# ---------------------------------------------------------------------------
# Custos, retorno e emissoes
# ---------------------------------------------------------------------------

def custo_r(kwh, tarifa_r_kwh):
    return kwh * tarifa_r_kwh


def retorno_simples_anos(investimento_r, economia_anual_r):
    """Payback simples: investimento / economia anual. Sem juros nem
    reajuste de tarifa. Devolve None quando nao ha economia."""
    if investimento_r <= 0:
        return 0.0
    if economia_anual_r <= 0:
        return None
    return investimento_r / economia_anual_r


def emissoes_kg(kwh, fator_kgco2_kwh):
    return kwh * fator_kgco2_kwh


def agua_economizada_litros_ano(minutos_atual, minutos_reduzido, vazao_l_min,
                                pessoas, banhos_por_pessoa_dia=1):
    """Agua que deixa de ser usada por ano ao encurtar o banho."""
    return ((minutos_atual - minutos_reduzido) * vazao_l_min * pessoas
            * banhos_por_pessoa_dia * sum(DIAS_MES))


# ---------------------------------------------------------------------------
# Comparacao das alternativas
# ---------------------------------------------------------------------------

def comparar_alternativas(pessoas, potencia_w, minutos_atual, minutos_reduzido,
                          tarifa_r_kwh, fator_kgco2_kwh, irradiacao_mensal,
                          temperatura_mensal, coletor, custo_solar_r,
                          vida_util_anos, banhos_por_pessoa_dia=1):
    """Calcula as quatro situacoes para o mesmo periodo de 1 ano.

    Devolve um dicionario com uma entrada por situacao. Cada entrada traz o
    consumo eletrico mensal e anual, o custo anual, as emissoes, o
    investimento, a economia e o retorno em relacao a situacao atual."""
    if minutos_reduzido >= minutos_atual:
        raise ValueError("o banho reduzido deve ser mais curto que o atual")

    atual = consumo_chuveiro_mensal(potencia_w, minutos_atual, pessoas,
                                    banhos_por_pessoa_dia)
    reduzido = consumo_chuveiro_mensal(potencia_w, minutos_reduzido, pessoas,
                                       banhos_por_pessoa_dia)
    # A carga termica do banho e igual ao consumo do chuveiro (resistencia).
    solar_atual = calor_solar_mensal(atual, irradiacao_mensal,
                                     temperatura_mensal, coletor)
    solar_reduzido = calor_solar_mensal(reduzido, irradiacao_mensal,
                                        temperatura_mensal, coletor)

    situacoes = {
        "atual": {"nome": "Situação atual (chuveiro elétrico)",
                  "mensal": atual, "investimento": 0.0, "demanda": atual},
        "A": {"nome": "A - Banho mais curto (sem investimento)",
              "mensal": reduzido, "investimento": 0.0, "demanda": reduzido},
        "B": {"nome": "B - Aquecedor solar + chuveiro como apoio",
              "mensal": apoio_eletrico_mensal(atual, solar_atual),
              "investimento": custo_solar_r, "demanda": atual,
              "solar": solar_atual},
        "A+B": {"nome": "A+B - Banho mais curto + aquecedor solar",
                "mensal": apoio_eletrico_mensal(reduzido, solar_reduzido),
                "investimento": custo_solar_r, "demanda": reduzido,
                "solar": solar_reduzido},
    }

    kwh_atual = sum(atual)
    for s in situacoes.values():
        kwh = sum(s["mensal"])
        s["kwh_ano"] = kwh
        s["custo_ano"] = custo_r(kwh, tarifa_r_kwh)
        s["co2_kg_ano"] = emissoes_kg(kwh, fator_kgco2_kwh)
        s["kwh_economizado_ano"] = kwh_atual - kwh
        s["economia_r_ano"] = custo_r(kwh_atual - kwh, tarifa_r_kwh)
        s["co2_evitado_kg_ano"] = emissoes_kg(kwh_atual - kwh, fator_kgco2_kwh)
        s["retorno_anos"] = retorno_simples_anos(s["investimento"],
                                                 s["economia_r_ano"])
        s["economia_liquida_vida_util"] = (s["economia_r_ano"] * vida_util_anos
                                           - s["investimento"])
        s["fracao_solar"] = (fracao_solar(s["demanda"], s["mensal"])
                             if s["investimento"] > 0 else 0.0)
    return situacoes


def coletor_de_parametros(params, **substituicoes):
    """Monta o dicionario do coletor usado pelo f-chart."""
    c = params["coletor_solar"]
    coletor = {
        "area_m2": c["area_m2"]["valor"],
        "fr_ta_n": c["fr_ta_n"]["valor"],
        "fr_ul_w_m2k": c["fr_ul_w_m2k"]["valor"],
        "razao_ta": c["razao_ta"]["valor"],
        "temp_agua_quente_c": c["temp_agua_quente_c"]["valor"],
        "volume_por_area_l_m2": c["volume_reservatorio_l"]["valor"] / c["area_m2"]["valor"],
    }
    coletor.update(substituicoes)
    return coletor


def comparar_com_parametros(params, **substituicoes):
    """Atalho: usa o cenario de referencia de parametros.json, trocando os
    valores informados em 'substituicoes' (ex.: pessoas=3)."""
    c = params["cenario_referencia"]
    base = {
        "pessoas": c["pessoas"],
        "potencia_w": c["potencia_chuveiro_w"],
        "minutos_atual": c["minutos_por_banho"],
        "minutos_reduzido": c["minutos_por_banho_alternativa_a"],
        "tarifa_r_kwh": params["tarifa_b1_r_kwh"]["valor"],
        "fator_kgco2_kwh": params["fator_emissao_kgco2_kwh"]["valor"],
        "irradiacao_mensal": params["irradiacao_kwh_m2_dia"]["valor"],
        "temperatura_mensal": params["temperatura_ar_c"]["valor"],
        "coletor": coletor_de_parametros(params),
        "custo_solar_r": params["custo_aquecedor_solar_r"]["valor"],
        "vida_util_anos": params["vida_util_aquecedor_anos"]["valor"],
        "banhos_por_pessoa_dia": c["banhos_por_pessoa_dia"],
    }
    base.update(substituicoes)
    return comparar_alternativas(**base)


# ---------------------------------------------------------------------------
# Casas em que cada morador toma banho de um jeito
# ---------------------------------------------------------------------------

def banhos_da_casa(moradores):
    """Lista com a duracao (min) de cada banho do dia, para todos os moradores.

    'moradores' e uma lista de dicionarios com 'banhos_dia' e 'minutos'
    (ou 'banhos', uma lista com a duracao de cada banho)."""
    banhos = []
    for m in moradores:
        if "banhos" in m:
            banhos.extend(b["minutos"] if isinstance(b, dict) else b for b in m["banhos"])
        else:
            banhos.extend([m["minutos"]] * m["banhos_dia"])
    if not banhos or any(b <= 0 for b in banhos):
        raise ValueError("informe ao menos um banho, com duracao positiva")
    return banhos


def minutos_com_meta(banhos, meta_minutos):
    """Minutos por dia se nenhum banho passar da meta (alternativa A)."""
    return sum(min(b, meta_minutos) for b in banhos)


def comparar_casa(params, banhos, meta_minutos, **substituicoes):
    """Compara as alternativas para uma lista de banhos diarios.

    O consumo so depende do total de minutos de chuveiro por dia, entao a
    casa entra no calculo como 1 'pessoa' com esse total. Devolve tambem os
    minutos por dia antes e depois da meta."""
    atual = sum(banhos)
    reduzido = minutos_com_meta(banhos, meta_minutos)
    if reduzido >= atual:
        raise ValueError("nenhum banho passa da meta: a alternativa A nao muda nada")
    r = comparar_com_parametros(params, pessoas=1, banhos_por_pessoa_dia=1,
                                minutos_atual=atual, minutos_reduzido=reduzido,
                                **substituicoes)
    r["minutos_dia"] = {"atual": atual, "A": reduzido}
    return r
