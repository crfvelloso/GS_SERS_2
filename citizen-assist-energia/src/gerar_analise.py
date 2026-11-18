"""Gera as tabelas e o gráfico da análise a partir de dados/parametros.json.

Uso:
    python3 src/gerar_analise.py

Saídas (pasta analise/):
    resultados.md          tabelas da comparação e da sensibilidade
    comparacao_anual.csv   uma linha por situação
    mensal.csv             demanda, sol e apoio elétrico mês a mês
    grafico_mensal.svg     demanda do banho x calor do sol
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calculos as calc  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "analise")


def br(valor, casas=2):
    texto = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",")
    return texto.replace("X", ".")


def gerar_svg(meses, demanda, solar, apoio, caminho):
    largura, altura = 760, 360
    esq, dir_, topo, base = 60, 20, 50, 300
    maximo = max(max(demanda), max(solar)) * 1.15
    passo = (largura - esq - dir_) / len(meses)
    barra = passo * 0.36

    def y(v):
        return base - (base - topo) * v / maximo

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
        f'font-family="Arial, sans-serif" font-size="12">',
        f'<rect width="{largura}" height="{altura}" fill="white"/>',
        '<text x="20" y="26" font-size="15" font-weight="bold" fill="#111">'
        'No inverno o sol cobre menos: o chuveiro completa o aquecimento</text>',
    ]
    for marca in range(0, int(maximo) + 1, 20):
        partes.append(f'<line x1="{esq}" y1="{y(marca):.1f}" x2="{largura - dir_}" '
                      f'y2="{y(marca):.1f}" stroke="#ddd"/>')
        partes.append(f'<text x="{esq - 8}" y="{y(marca) + 4:.1f}" text-anchor="end" '
                      f'fill="#444">{marca}</text>')
    partes.append(f'<text x="16" y="{(topo + base) / 2:.0f}" fill="#444" '
                  f'transform="rotate(-90 16 {(topo + base) / 2:.0f})" '
                  f'text-anchor="middle">kWh por mês</text>')
    for i, mes in enumerate(meses):
        x0 = esq + i * passo + passo * 0.12
        partes.append(f'<rect x="{x0:.1f}" y="{y(demanda[i]):.1f}" width="{barra:.1f}" '
                      f'height="{base - y(demanda[i]):.1f}" fill="#555"/>')
        partes.append(f'<rect x="{x0 + barra:.1f}" y="{y(solar[i]):.1f}" width="{barra:.1f}" '
                      f'height="{base - y(solar[i]):.1f}" fill="#e8a317"/>')
        if apoio[i] >= 0.5:
            partes.append(f'<text x="{x0 + barra:.1f}" y="{y(max(demanda[i], solar[i])) - 6:.1f}" '
                          f'text-anchor="middle" font-size="10.5" fill="#b03000">'
                          f'+{apoio[i]:.0f}</text>')
        partes.append(f'<text x="{x0 + barra:.1f}" y="{base + 18}" text-anchor="middle" '
                      f'fill="#222">{mes}</text>')
    partes.append(f'<line x1="{esq}" y1="{base}" x2="{largura - dir_}" y2="{base}" stroke="#222"/>')
    ly = altura - 18
    partes += [
        f'<rect x="{esq}" y="{ly - 10}" width="12" height="12" fill="#555"/>',
        f'<text x="{esq + 18}" y="{ly}" fill="#222">Energia do banho (situação atual)</text>',
        f'<rect x="{esq + 250}" y="{ly - 10}" width="12" height="12" fill="#e8a317"/>',
        f'<text x="{esq + 268}" y="{ly}" fill="#222">Calor útil do aquecedor solar</text>',
        f'<text x="{esq + 480}" y="{ly}" fill="#b03000">+N = kWh do chuveiro como apoio</text>',
        '</svg>',
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(partes) + "\n")


def main():
    params = calc.carregar_parametros()
    os.makedirs(SAIDA, exist_ok=True)
    r = calc.comparar_com_parametros(params)
    c = params["cenario_referencia"]
    irr = params["irradiacao_kwh_m2_dia"]["valor"]
    temp = params["temperatura_ar_c"]["valor"]
    coletor = calc.coletor_de_parametros(params)
    solar = r["B"]["solar"]
    fracoes = [calc.fracao_solar_fchart(r["atual"]["mensal"][i], calc.DIAS_MES[i],
                                        irr[m], temp[m], coletor)
               for i, m in enumerate(calc.MESES)]

    # CSV anual
    with open(os.path.join(SAIDA, "comparacao_anual.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["situacao", "kwh_ano", "custo_r_ano", "economia_r_ano",
                    "investimento_r", "retorno_anos", "fracao_solar",
                    "co2_kg_ano", "co2_evitado_kg_ano", "economia_liquida_15_anos_r"])
        for k in ("atual", "A", "B", "A+B"):
            s = r[k]
            w.writerow([k, round(s["kwh_ano"], 1), round(s["custo_ano"], 2),
                        round(s["economia_r_ano"], 2), round(s["investimento"], 2),
                        "" if s["retorno_anos"] is None or s["investimento"] == 0 else round(s["retorno_anos"], 2),
                        round(s["fracao_solar"], 3), round(s["co2_kg_ano"], 1),
                        round(s["co2_evitado_kg_ano"], 1),
                        round(s["economia_liquida_vida_util"], 2)])

    # CSV mensal
    with open(os.path.join(SAIDA, "mensal.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mes", "dias", "irradiacao_kwh_m2_dia", "demanda_atual_kwh",
                    "calor_solar_kwh", "apoio_eletrico_B_kwh", "demanda_A_kwh",
                    "apoio_eletrico_AB_kwh"])
        for i, m in enumerate(calc.MESES):
            w.writerow([m, calc.DIAS_MES[i], irr[m], round(r["atual"]["mensal"][i], 1),
                        round(solar[i], 1), round(r["B"]["mensal"][i], 1),
                        round(r["A"]["mensal"][i], 1), round(r["A+B"]["mensal"][i], 1)])

    gerar_svg(calc.MESES, r["atual"]["mensal"], solar, r["B"]["mensal"],
              os.path.join(SAIDA, "grafico_mensal.svg"))

    # Sensibilidade: coletor pior, de referencia e melhor x custo baixo e alto
    pc = params["coletor_solar"]
    fr_faixa = pc["fr_ta_n"]["faixa_sensibilidade"]
    ul_faixa = pc["fr_ul_w_m2k"]["faixa_sensibilidade"]
    casos_coletor = [("Pior", fr_faixa[0], ul_faixa[0]),
                     ("Referência", pc["fr_ta_n"]["valor"], pc["fr_ul_w_m2k"]["valor"]),
                     ("Melhor", fr_faixa[1], ul_faixa[1])]
    custos = [params["custo_aquecedor_solar_r"]["valor"],
              params["custo_aquecedor_solar_alto_r"]["valor"]]
    sens = []
    for nome, fr, ul in casos_coletor:
        col = calc.coletor_de_parametros(params, fr_ta_n=fr, fr_ul_w_m2k=ul)
        for custo in custos:
            b = calc.comparar_com_parametros(params, coletor=col,
                                             custo_solar_r=custo)["B"]
            sens.append((nome, fr, ul, custo, b))

    # Conferencia de ordem de grandeza com um coletor comercial
    ref_kwh_mes = params["producao_coletor_referencia_kwh_mes"]["valor"]
    solar_por_m2_mes = sum(solar) / 12 / coletor["area_m2"]

    agua = calc.agua_economizada_litros_ano(c["minutos_por_banho"],
                                            c["minutos_por_banho_alternativa_a"],
                                            c["vazao_chuveiro_l_min"], c["pessoas"])
    dt = calc.elevacao_temperatura_c(c["potencia_chuveiro_w"], c["vazao_chuveiro_l_min"])

    linhas = [
        "# Resultados calculados",
        "",
        "Arquivo gerado por `src/gerar_analise.py` a partir de `dados/parametros.json`. "
        "Não edite à mão: altere os parâmetros e rode o script de novo.",
        "",
        f"Família de referência: {c['pessoas']} pessoas, chuveiro de {c['potencia_chuveiro_w']} W, "
        f"{c['minutos_por_banho']} min por banho, 1 banho por pessoa por dia, 365 dias, "
        f"tarifa B1 Enel SP sem tributos (R$ {br(params['tarifa_b1_r_kwh']['valor'], 5)}/kWh).",
        "",
        "## Comparação anual",
        "",
        "| Situação | Consumo elétrico (kWh/ano) | Custo (R$/ano) | Economia (R$/ano) | "
        "Investimento (R$) | Retorno simples | Fração solar | CO2 (kg/ano) | CO2 evitado (kg/ano) | "
        "Economia líquida em 15 anos (R$) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for k in ("atual", "A", "B", "A+B"):
        s = r[k]
        ret = "-" if s["investimento"] == 0 else f"{br(s['retorno_anos'], 1)} anos"
        fs = "-" if s["investimento"] == 0 else f"{br(s['fracao_solar'] * 100, 0)}%"
        linhas.append(
            f"| {s['nome']} | {br(s['kwh_ano'], 0)} | {br(s['custo_ano'])} | "
            f"{br(s['economia_r_ano'])} | {br(s['investimento'])} | {ret} | {fs} | "
            f"{br(s['co2_kg_ano'], 1)} | {br(s['co2_evitado_kg_ano'], 1)} | "
            f"{br(s['economia_liquida_vida_util'])} |")
    linhas += [
        "",
        f"Água economizada na alternativa A: {br(agua, 0)} litros por ano "
        f"(vazão de {br(c['vazao_chuveiro_l_min'], 1)} L/min).",
        "",
        f"Conferência física: um chuveiro de {c['potencia_chuveiro_w']} W com vazão de "
        f"{br(c['vazao_chuveiro_l_min'], 1)} L/min aquece a água em {br(dt, 1)} °C "
        "(ΔT = P / (ṁ · c)), compatível com um banho morno.",
        "",
        "## Mês a mês (situação atual e alternativa B)",
        "",
        "Fração solar de cada mês calculada pelo método f-chart.",
        "",
        "| Mês | Irradiação (kWh/m²/dia) | Temperatura do ar (°C) | Energia do banho (kWh) | "
        "Fração solar | Calor do sol (kWh) | Apoio do chuveiro em B (kWh) |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, m in enumerate(calc.MESES):
        linhas.append(f"| {m} | {br(irr[m], 2)} | {br(temp[m], 1)} | "
                      f"{br(r['atual']['mensal'][i], 1)} | {br(fracoes[i] * 100, 0)}% | "
                      f"{br(solar[i], 1)} | {br(r['B']['mensal'][i], 1)} |")
    linhas += [
        "",
        "![Energia do banho x calor do aquecedor solar](grafico_mensal.svg)",
        "",
        f"Conferência: o sistema entrega em média {br(solar_por_m2_mes, 1)} kWh por m² por mês. "
        f"Um coletor comercial classe A declara {br(ref_kwh_mes / 1.96, 1)} kWh por m² por mês "
        "nas condições de ensaio do Inmetro. O valor calculado aqui é menor porque usa o clima de "
        "São Paulo mês a mês e só conta o calor que a família de fato usa no banho; a ordem de "
        "grandeza é compatível.",
        "",
        "## Sensibilidade da alternativa B",
        "",
        "| Coletor | FR(τα)n | FR·UL (W/m²·K) | Custo instalado (R$) | Fração solar | "
        "Economia (R$/ano) | Retorno simples |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for nome, fr, ul, custo, b in sens:
        linhas.append(f"| {nome} | {br(fr, 2)} | {br(ul, 1)} | {br(custo)} | "
                      f"{br(b['fracao_solar'] * 100, 0)}% | {br(b['economia_r_ano'])} | "
                      f"{br(b['retorno_anos'], 1)} anos |")
    linhas.append("")
    with open(os.path.join(SAIDA, "resultados.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print("Gerados em analise/: resultados.md, comparacao_anual.csv, mensal.csv, "
          "grafico_mensal.svg")


if __name__ == "__main__":
    main()
