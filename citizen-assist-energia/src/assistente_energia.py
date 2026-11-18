"""Citizen Assist AI - módulo de energia (Soluções em Energias Renováveis e
Sustentáveis).

Orienta famílias que usam chuveiro elétrico na área da Enel SP: estima o
gasto do banho, compara duas alternativas (banho mais curto e aquecedor
solar) e mostra recomendações, referências e limitações.

Uso:
    python3 src/assistente_energia.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calculos as calc  # noqa: E402

AVISO = """
==================================================================
 CITIZEN ASSIST AI - Energia no banho
==================================================================
 Protótipo acadêmico. Não é um canal oficial da Enel, da ANEEL ou
 de qualquer órgão público. Os valores são ESTIMATIVAS, não
 garantias de economia. Não pedimos nome, endereço, CPF nem número
 de cliente: só dados do banho, que não são gravados.
==================================================================
"""

MENU = """
------------------------------------------------------------------
 1 - Quanto o chuveiro gasta na minha casa?
 2 - Comparar alternativas para a minha casa
 3 - Ver a análise da família de referência
 4 - Dicas de uso consciente no banho
 5 - Referências usadas
 6 - Limitações das estimativas
 7 - O que significam kWh, potência e tarifa?
 0 - Sair
------------------------------------------------------------------"""


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------

def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def num(valor, casas=1):
    texto = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",")
    return texto.replace("X", ".")


def anos(valor):
    return "não se paga" if valor is None else f"{num(valor)} anos"


# ---------------------------------------------------------------------------
# Entrada de dados com validação
# ---------------------------------------------------------------------------

def perguntar_numero(texto, padrao, minimo, maximo, inteiro=False, casas=2):
    """Lê um número entre minimo e maximo. Enter usa o valor padrão; sem
    padrão (None), a resposta é obrigatória."""
    rotulo = f"{texto}: " if padrao is None else \
        f"{texto} [Enter = {num(padrao, 0 if inteiro else casas)}]: "
    while True:
        try:
            bruto = input(rotulo)
        except EOFError:
            print("\nEntrada encerrada.")
            sys.exit(0)
        bruto = bruto.strip().replace(",", ".")
        if bruto == "":
            if padrao is None:
                print("  Digite uma opção.")
                continue
            return padrao
        try:
            valor = int(bruto) if inteiro else float(bruto)
        except ValueError:
            tipo = "um número inteiro" if inteiro else "um número"
            print(f"  Entrada inválida: '{bruto}' não é {tipo}.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  Valor fora da faixa: use de {num(minimo, 0)} a {num(maximo, 0)}.")


def perguntar_sim_nao(texto):
    while True:
        try:
            r = input(f"{texto} (s/n): ").strip().lower()
        except EOFError:
            print("\nEntrada encerrada.")
            sys.exit(0)
        if r in ("s", "sim"):
            return True
        if r in ("n", "nao", "não"):
            return False
        print("  Responda s para sim ou n para não.")


def coletar_dados_casa(params):
    """Pergunta os dados da casa. Devolve a potência, a tarifa e a lista
    'banhos' com a duração de cada banho do dia, de todos os moradores."""
    c = params["cenario_referencia"]
    tarifa = params["tarifa_b1_r_kwh"]["valor"]
    print("\nResponda sobre a sua casa. Aperte Enter para usar o valor sugerido.")
    print("Palavras difíceis? A opção 7 do menu explica kWh, potência e tarifa.")
    pessoas = perguntar_numero("Quantas pessoas tomam banho na casa?",
                               c["pessoas"], 1, 15, inteiro=True)
    print("\nPotência é quanta energia o chuveiro gasta a cada segundo, em watts (W).")
    print("Onde achar: na etiqueta do chuveiro, na caixa, no manual ou na nota da compra")
    print("(ex.: 127 V 5500 W). Se não encontrar, aperte Enter para usar 5500 W.")
    potencia = perguntar_numero("Potência do chuveiro em watts",
                                c["potencia_chuveiro_w"], 1000, 9000, inteiro=True)
    iguais = pessoas == 1 or perguntar_sim_nao(
        "Todos tomam o mesmo número de banhos, com a mesma duração?")
    banhos = []
    if iguais:
        minutos = perguntar_numero("Duração média de cada banho (minutos)",
                                   c["minutos_por_banho"], 1, 60)
        por_dia = perguntar_numero("Banhos por pessoa por dia",
                                   c["banhos_por_pessoa_dia"], 1, 4, inteiro=True)
        banhos = [minutos] * (pessoas * por_dia)
    else:
        print("Agora, morador por morador (não precisa dizer o nome).")
        for i in range(1, pessoas + 1):
            por_dia = perguntar_numero(f"  Pessoa {i}: quantos banhos por dia?",
                                       1, 1, 4, inteiro=True)
            minutos = perguntar_numero(f"  Pessoa {i}: quantos minutos dura cada banho?",
                                       c["minutos_por_banho"], 1, 60)
            banhos += [minutos] * por_dia
    print("\nTarifa é o preço de cada kWh de energia. O valor sugerido é o da Enel SP")
    print(f"para residências, sem impostos: {reais(tarifa)} por kWh.")
    print("Se não souber, aperte Enter.")
    tarifa_casa = perguntar_numero(
        "Tarifa em R$/kWh", tarifa, 0.10, 3.00, casas=5)
    return {"potencia_w": potencia, "banhos": banhos, "tarifa_r_kwh": tarifa_casa}


# ---------------------------------------------------------------------------
# Opções do menu
# ---------------------------------------------------------------------------

def opcao_consumo(params):
    d = coletar_dados_casa(params)
    minutos_dia = sum(d["banhos"])
    mensal = calc.consumo_chuveiro_mensal(d["potencia_w"], minutos_dia, 1)
    kwh_ano = sum(mensal)
    kwh_mes = kwh_ano / 12
    custo_ano = calc.custo_r(kwh_ano, d["tarifa_r_kwh"])
    print("\n--- Gasto estimado do chuveiro ---")
    print(f"  A casa usa o chuveiro {num(minutos_dia, 0)} minutos por dia "
          f"({len(d['banhos'])} {'banho' if len(d['banhos']) == 1 else 'banhos'}).")
    print(f"  Cada 10 minutos de banho gastam {num(calc.energia_kwh(d['potencia_w'], 10 / 60), 2)} kWh "
          f"({num(d['potencia_w'] / 1000, 1)} kW de potência x 10 min).")
    print("  kWh é a medida de energia que aparece na conta de luz.")
    print(f"  Por mês: cerca de {num(kwh_mes)} kWh, ou {reais(kwh_mes * d['tarifa_r_kwh'])}.")
    print(f"  Por ano: cerca de {num(kwh_ano, 0)} kWh, ou {reais(custo_ano)}.")
    print("  Valores sem ICMS, PIS/COFINS e bandeira tarifária: na conta, o gasto real")
    print("  tende a ser maior.")

    total = perguntar_numero(
        "\nSe quiser comparar com a conta, digite o consumo do mês em kWh "
        "(0 para pular)", 0, 0, 5000, inteiro=True)
    if total > 0:
        parte = kwh_mes / total * 100
        if parte > 100:
            print("  O chuveiro estimado passou do total da conta: confira a")
            print("  potência e os minutos informados.")
        else:
            print(f"  O banho representaria cerca de {num(parte, 0)}% do consumo da conta.")


def imprimir_tabela(resultado):
    print(f"\n  {'Situação':<44}{'kWh/ano':>9}{'Custo/ano':>14}{'Economia/ano':>15}"
          f"{'Investimento':>15}{'Retorno':>14}")
    for chave in ("atual", "A", "B", "A+B"):
        s = resultado[chave]
        retorno = "-" if s["investimento"] == 0 else anos(s["retorno_anos"])
        print(f"  {s['nome']:<44}{num(s['kwh_ano'], 0):>9}{reais(s['custo_ano']):>14}"
              f"{reais(s['economia_r_ano']):>15}{reais(s['investimento']):>15}{retorno:>14}")
    print("\n  Como ler a tabela:")
    print("  - kWh/ano: energia que o chuveiro gasta no ano.")
    print("  - Custo/ano: quanto essa energia custa no ano.")
    print("  - Economia/ano: quanto deixa de pagar por ano, comparado com hoje.")
    print("  - Investimento: quanto precisa gastar antes para começar a economizar.")
    print("  - Retorno: em quantos anos a economia paga o investimento.")


def recomendar(resultado, d, meta, casa_com_telhado, params):
    a, b = resultado["A"], resultado["B"]
    vazao = params["cenario_referencia"]["vazao_chuveiro_l_min"]
    agua = calc.agua_economizada_litros_ano(resultado["minutos_dia"]["atual"],
                                            resultado["minutos_dia"]["A"], vazao, 1)
    print("\n--- O que o Citizen Assist AI recomenda ---")
    agua_txt = (f"{num(agua / 1000, 0)} mil litros" if agua >= 2000
                else f"{num(agua, 0)} litros")
    print(f"1) Comece limitando cada banho a {num(meta, 0)} minutos: não custa nada e")
    print(f"   pode economizar cerca de {reais(a['economia_r_ano'])} por ano "
          f"({num(a['kwh_economizado_ano'], 0)} kWh) e uns {agua_txt} de água.")
    maior = max(d["banhos"])
    if maior > meta:
        kwh_banho = calc.energia_kwh(d["potencia_w"], (maior - meta) / 60)
        print(f"   Exemplo: um banho de {num(maior, 0)} minutos que passa a durar {num(meta, 0)} "
              f"gasta {num(kwh_banho, 2)} kWh a menos,")
        print(f"   cerca de {reais(kwh_banho * d['tarifa_r_kwh'])} por banho.")
    longos = sum(1 for m in d["banhos"] if m > meta)
    if longos < len(d["banhos"]):
        print(f"   Só {longos} dos {len(d['banhos'])} banhos do dia passam da meta: "
              "a mudança é só para eles.")
    faixa_kit = calc.fora_da_faixa_do_kit(len(d["banhos"]))
    if not casa_com_telhado:
        print("2) O aquecedor solar precisa de telhado com sol e permissão para obra.")
        print("   Sem isso (apartamento, casa alugada), o banho mais curto é a melhor opção.")
    elif faixa_kit == -1:
        print("2) O kit solar de referência (200 L, 2 m²) é feito para 4 a 5 banhos por dia.")
        print("   Para a sua casa ele fica grande demais: este cálculo é só indicativo.")
        print(f"   Economia estimada: {reais(b['economia_r_ano'])} por ano, retorno em "
              f"{anos(b['retorno_anos'])}. Peça orçamento de um modelo menor.")
    elif faixa_kit == 1:
        print("2) O kit solar de referência (200 L, 2 m²) é feito para 4 a 5 banhos por dia.")
        print(f"   Com mais banhos, ele cobriria só {num(b['fracao_solar'] * 100, 0)}% da energia.")
        print("   Peça orçamento de um sistema maior; o retorno pode mudar.")
    elif b["retorno_anos"] is not None and b["retorno_anos"] <= 6:
        print(f"2) O aquecedor solar vale um orçamento: custo de referência {reais(b['investimento'])},")
        print(f"   economia estimada de {reais(b['economia_r_ano'])} por ano e retorno em "
              f"{anos(b['retorno_anos'])}.")
        print(f"   Ou seja: em cerca de {anos(b['retorno_anos'])} o que a casa deixa de pagar de luz")
        print("   paga o aquecedor. Depois disso, a economia fica para a família.")
        print(f"   O sol cobriria cerca de {num(b['fracao_solar'] * 100, 0)}% da energia do banho;")
        print("   no inverno o chuveiro ainda completa o aquecimento.")
    else:
        print(f"2) Com esse uso, o aquecedor solar demoraria {anos(b['retorno_anos'])} para se pagar.")
        print("   Priorize o banho mais curto antes de investir.")
    print(f"3) Juntas, as duas medidas reduziriam o gasto do banho de "
          f"{reais(resultado['atual']['custo_ano'])} para {reais(resultado['A+B']['custo_ano'])} por ano.")
    print(f"   Emissão de CO2 evitada: cerca de {num(resultado['A+B']['co2_evitado_kg_ano'], 0)} kg por ano.")


def opcao_comparar(params):
    d = coletar_dados_casa(params)
    maior = max(d["banhos"])
    if maior <= 1:
        print("  Banhos de 1 minuto já são curtíssimos: a alternativa A não se aplica.")
        return
    sugestao = max(1, min(params["cenario_referencia"]["minutos_por_banho_alternativa_a"],
                          maior - 1))
    meta = perguntar_numero("Meta: duração máxima de cada banho na alternativa A (minutos)",
                            sugestao, 1, maior - 0.5)
    casa = perguntar_sim_nao("A casa tem telhado com sol e vocês podem fazer obra nele?")
    resultado = calc.comparar_casa(params, d["banhos"], meta, potencia_w=d["potencia_w"],
                                   tarifa_r_kwh=d["tarifa_r_kwh"])
    print("\n--- Comparação para 1 ano ---")
    imprimir_tabela(resultado)
    recomendar(resultado, d, meta, casa, params)
    comparar_com_conta(resultado)
    print("\nEstimativas, não garantias. Veja a opção 6 para as limitações.")


def opcao_referencia(params):
    c = params["cenario_referencia"]
    resultado = calc.comparar_com_parametros(params)
    print("\n--- Família de referência ---")
    print(f"  {c['pessoas']} pessoas, chuveiro de {c['potencia_chuveiro_w']} W, "
          f"banho de {c['minutos_por_banho']} min, tarifa Enel SP B1 sem impostos.")
    print(f"  Alternativa A: banho de {c['minutos_por_banho_alternativa_a']} min.")
    print(f"  Alternativa B: aquecedor solar de 200 L e 2 m², custo SINAPI "
          f"{reais(params['custo_aquecedor_solar_r']['valor'])}.")
    imprimir_tabela(resultado)
    b = resultado["B"]
    print(f"\n  Fração solar estimada (B): {num(b['fracao_solar'] * 100, 0)}% da energia do banho.")
    print("  Análise completa: analise/analise_energetica.md")


def opcao_dicas():
    print("""
--- Dicas de uso consciente no banho ---
  * Energia = potência x tempo. Um chuveiro de 5500 W ligado por 10 minutos
    gasta cerca de 0,92 kWh. Cada minuto a menos economiza 0,09 kWh.
  * Use a posição de menor aquecimento nos dias quentes: a água da rede já
    chega mais morna e a potência menor basta.
  * Feche o chuveiro enquanto se ensaboa: a resistência só gasta com a água
    passando.
  * Evite banhos no horário de ponta (fim da tarde e começo da noite) quando
    puder: é quando a rede elétrica está mais carregada.
  * Resistência queimada ou fios aquecendo são risco de choque e incêndio:
    chame um eletricista. Não troque a resistência com o disjuntor ligado.
  * Antes de comprar um aquecedor solar, peça pelo menos dois orçamentos e
    confira a etiqueta do Inmetro (classe A ou B).""")


def opcao_referencias(params):
    print("\n--- Referências (consultadas em 17/11/2026) ---")
    for chave in ("tarifa_b1_r_kwh", "fator_emissao_kgco2_kwh",
                  "irradiacao_kwh_m2_dia", "custo_aquecedor_solar_r",
                  "producao_coletor_referencia_kwh_mes"):
        p = params[chave]
        print(f"  * {p['fonte']}")
        if "url" in p:
            print(f"    {p['url']}")
    print("  * Duffie, J. A.; Beckman, W. A. Solar Engineering of Thermal Processes")
    print("    (método f-chart, capítulo 20).")
    print("  Lista completa em referencias.md")


def opcao_limitacoes():
    print("""
--- Limitações das estimativas ---
  * A tarifa usada (R$ 0,78938/kWh) não inclui ICMS, PIS/COFINS nem
    bandeira tarifária. Na conta real, a economia em reais tende a ser
    maior; com Tarifa Social (baixa renda), pode ser menor.
  * O cálculo usa a potência máxima do chuveiro o tempo todo. Quem usa a
    posição de verão gasta menos que o estimado.
  * O aquecedor solar foi calculado pelo método f-chart com médias mensais
    de sol e temperatura de São Paulo (NASA POWER) e parâmetros típicos de
    coletor plano, não os de um modelo específico. Telhado com sombra ou
    virado para o sul produz menos.
  * O kit de referência é para 4 a 5 banhos por dia. Fora dessa faixa, o
    resultado é só indicativo.
  * O custo do aquecedor (SINAPI) é uma média nacional para casa simples.
    Casas sem encanamento de água quente podem pagar bem mais.
  * O retorno é simples: não considera juros, reajuste da tarifa nem
    manutenção.
  * Nada aqui substitui o orçamento de um instalador ou a conta de luz.""")


def comparar_com_conta(resultado):
    """Mostra a economia de cada alternativa como parte do consumo da conta."""
    total = perguntar_numero(
        "\nQuer comparar com a sua conta? Digite o consumo do mês em kWh, que aparece "
        "na conta de luz (0 para pular)", 0, 0, 5000, inteiro=True)
    if total <= 0:
        return
    banho_mes = resultado["atual"]["kwh_ano"] / 12
    if banho_mes > total:
        print("  O chuveiro estimado passou do total da conta: confira a potência e os")
        print("  minutos informados.")
        return
    print(f"  Hoje o banho representaria cerca de {num(banho_mes / total * 100, 0)}% "
          f"dos {num(total, 0)} kWh da conta.")
    for chave in ("A", "B", "A+B"):
        s = resultado[chave]
        menos = s["kwh_economizado_ano"] / 12
        print(f"  {s['nome'].split(' (')[0]}: {num(menos, 0)} kWh a menos por mês, "
              f"cerca de {num(menos / total * 100, 0)}% da conta.")


def opcao_glossario():
    print("""
--- O que significam as palavras ---
  * Potência (W, watt): quanta energia o aparelho gasta a cada segundo.
    Um chuveiro de 5500 W gasta energia cerca de 600 vezes mais rápido que uma
    lâmpada de 9 W. Fica na etiqueta do chuveiro, na caixa ou no manual.
  * kW (quilowatt): 1.000 W. Um chuveiro de 5500 W tem 5,5 kW.
  * kWh (quilowatt-hora): a energia gasta. É a medida que aparece na conta
    de luz. Um aparelho de 1 kW ligado por 1 hora gasta 1 kWh.
    Exemplo: chuveiro de 5,5 kW ligado por 10 minutos (1/6 de hora)
    gasta 5,5 x 1/6 = 0,92 kWh.
  * Tarifa: o preço de cada kWh. Na Enel SP, sem impostos, cerca de
    R$ 0,79 por kWh. Então 0,92 kWh custam uns R$ 0,72.
  * Aquecedor solar: placa no telhado que usa o calor do sol para
    esquentar a água do banho, guardada numa caixa térmica (reservatório).
  * Retorno: em quantos anos o dinheiro economizado na conta paga o que
    foi gasto para comprar e instalar um equipamento.""")


def main():
    params = calc.carregar_parametros()
    print(AVISO)
    acoes = {
        1: lambda: opcao_consumo(params),
        2: lambda: opcao_comparar(params),
        3: lambda: opcao_referencia(params),
        4: opcao_dicas,
        5: lambda: opcao_referencias(params),
        6: opcao_limitacoes,
        7: opcao_glossario,
    }
    while True:
        print(MENU)
        opcao = perguntar_numero("Escolha uma opção", None, 0, 7, inteiro=True)
        if opcao == 0:
            print("Até logo! Lembre: são estimativas, confira sempre a sua conta.")
            return
        acoes[opcao]()


if __name__ == "__main__":
    main()
