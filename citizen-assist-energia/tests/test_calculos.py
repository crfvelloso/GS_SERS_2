"""Testes dos cálculos de energia.

Uso:
    python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

import calculos as calc  # noqa: E402


class TestConceitos(unittest.TestCase):
    def test_energia_potencia_vezes_tempo(self):
        # 5500 W por 10 minutos = 5,5 kW x 1/6 h = 0,9167 kWh
        self.assertAlmostEqual(calc.energia_kwh(5500, 10 / 60), 0.91667, places=4)

    def test_energia_rejeita_negativos(self):
        with self.assertRaises(ValueError):
            calc.energia_kwh(-1, 1)

    def test_consumo_anual_do_cenario(self):
        # 4 pessoas x 10 min x 5,5 kW x 365 dias = 1338,33 kWh
        mensal = calc.consumo_chuveiro_mensal(5500, 10, 4)
        self.assertEqual(len(mensal), 12)
        self.assertAlmostEqual(sum(mensal), 1338.333, places=2)
        self.assertAlmostEqual(mensal[1], 5.5 * (40 / 60) * 28, places=6)

    def test_consumo_rejeita_zero_pessoas(self):
        with self.assertRaises(ValueError):
            calc.consumo_chuveiro_mensal(5500, 10, 0)

    def test_elevacao_de_temperatura(self):
        # dT = 5500 / (0,05 kg/s x 4186) = 26,28 graus
        self.assertAlmostEqual(calc.elevacao_temperatura_c(5500, 3.0), 26.278, places=2)

    def test_energia_bate_com_calor_da_agua(self):
        # 120 L/dia aquecidos 26,28 graus = 3,667 kWh, o mesmo que 4 banhos de 10 min
        dt = calc.elevacao_temperatura_c(5500, 3.0)
        calor_kwh = 120 * 4.186 * dt / 3600
        self.assertAlmostEqual(calor_kwh, calc.energia_kwh(5500, 40 / 60), places=3)


class TestSolar(unittest.TestCase):
    def setUp(self):
        self.coletor = {"area_m2": 2.0, "fr_ta_n": 0.70, "fr_ul_w_m2k": 5.5,
                        "razao_ta": 0.94, "temp_agua_quente_c": 45,
                        "volume_por_area_l_m2": 100}

    def test_fchart_mes_calculado_a_mao(self):
        # Junho em Sao Paulo: carga 110 kWh, H = 3,2578 kWh/m2/dia, Ta = 16,3 C
        # X = 2 x 5,5 x 83,7 x 2.592.000 / 396.000.000 = 6,0265
        #     x (100/75)^-0,25 = 0,93060 -> 5,6083
        #     x (11,6 + 53,1 + 62,918 - 37,816)/83,7 = 1,0729 -> 6,0172
        # Y = 2 x 0,70 x 0,94 x 3,2578 x 3,6e6 x 30 / 3,96e8 = 1,1696
        # f = 1,029Y - 0,065X - 0,245Y^2 + 0,0018X^2 + 0,0215Y^3 = 0,5766
        f = calc.fracao_solar_fchart(110.0, 30, 3.2578, 16.3, self.coletor)
        self.assertAlmostEqual(f, 0.5766, places=3)

    def test_mais_sol_aumenta_a_fracao(self):
        pouco = calc.fracao_solar_fchart(110.0, 30, 3.0, 20, self.coletor)
        muito = calc.fracao_solar_fchart(110.0, 30, 5.5, 20, self.coletor)
        self.assertLess(pouco, muito)

    def test_carga_menor_aumenta_a_fracao(self):
        grande = calc.fracao_solar_fchart(150.0, 30, 4.5, 20, self.coletor)
        pequena = calc.fracao_solar_fchart(60.0, 30, 4.5, 20, self.coletor)
        self.assertLess(grande, pequena)

    def test_fracao_tem_limite(self):
        f = calc.fracao_solar_fchart(5.0, 30, 6.0, 25, self.coletor)
        self.assertEqual(f, calc.FRACAO_SOLAR_MAXIMA)
        self.assertEqual(calc.fracao_solar_fchart(0, 30, 6.0, 25, self.coletor), 0.0)

    def test_faixa_do_kit(self):
        self.assertEqual(calc.fora_da_faixa_do_kit(2), -1)
        self.assertEqual(calc.fora_da_faixa_do_kit(4), 0)
        self.assertEqual(calc.fora_da_faixa_do_kit(3, 2), 1)

    def test_apoio_nunca_negativo(self):
        self.assertEqual(calc.apoio_eletrico_mensal([10, 10], [15, 4]), [0.0, 6])

    def test_fracao_solar(self):
        self.assertAlmostEqual(calc.fracao_solar([100, 100], [0, 50]), 0.75)
        self.assertEqual(calc.fracao_solar([0, 0], [0, 0]), 0.0)


class TestCustos(unittest.TestCase):
    def test_retorno_simples(self):
        self.assertAlmostEqual(calc.retorno_simples_anos(3000, 1000), 3.0)
        self.assertEqual(calc.retorno_simples_anos(0, 500), 0.0)
        self.assertIsNone(calc.retorno_simples_anos(3000, 0))

    def test_agua_economizada(self):
        # 3 min x 3 L/min x 4 pessoas x 365 dias = 13.140 L
        self.assertEqual(calc.agua_economizada_litros_ano(10, 7, 3.0, 4), 13140)


class TestComparacao(unittest.TestCase):
    def setUp(self):
        self.params = calc.carregar_parametros()
        self.r = calc.comparar_com_parametros(self.params)

    def test_mesmo_periodo_e_mesma_necessidade(self):
        self.assertEqual(self.r["B"]["demanda"], self.r["atual"]["demanda"])
        self.assertEqual(len(self.r["B"]["mensal"]), 12)

    def test_ordem_das_alternativas(self):
        kwh = {k: self.r[k]["kwh_ano"] for k in self.r}
        self.assertLess(kwh["A"], kwh["atual"])
        self.assertLess(kwh["B"], kwh["atual"])
        self.assertLessEqual(kwh["A+B"], min(kwh["A"], kwh["B"]))

    def test_alternativa_a_economiza_30_por_cento(self):
        self.assertAlmostEqual(self.r["A"]["kwh_economizado_ano"] / self.r["atual"]["kwh_ano"],
                               0.3, places=6)

    def test_custo_usa_a_tarifa(self):
        tarifa = self.params["tarifa_b1_r_kwh"]["valor"]
        self.assertAlmostEqual(self.r["atual"]["custo_ano"], self.r["atual"]["kwh_ano"] * tarifa)

    def test_emissoes_usam_o_fator_mcti(self):
        self.assertAlmostEqual(self.r["atual"]["co2_kg_ano"],
                               self.r["atual"]["kwh_ano"] * 0.0461)

    def test_fracao_solar_entre_0_e_1(self):
        self.assertTrue(0 < self.r["B"]["fracao_solar"] < 1)

    def test_banho_reduzido_precisa_ser_menor(self):
        with self.assertRaises(ValueError):
            calc.comparar_com_parametros(self.params, minutos_reduzido=12)


class TestCasaComHabitosDiferentes(unittest.TestCase):
    def setUp(self):
        self.params = calc.carregar_parametros()
        # Um morador com 2 banhos de 10 min, um com 1 de 15 min, um com 1 de 10 min
        self.casa = [{"banhos_dia": 2, "minutos": 10},
                     {"banhos": [{"periodo": "noite", "minutos": 15}]},
                     {"banhos": [10]}]

    def test_lista_de_banhos(self):
        self.assertEqual(calc.banhos_da_casa(self.casa), [10, 10, 15, 10])

    def test_meta_corta_so_os_banhos_longos(self):
        self.assertEqual(calc.minutos_com_meta([10, 10, 15, 10], 7), 28)
        self.assertEqual(calc.minutos_com_meta([5, 12], 7), 12)

    def test_consumo_da_casa(self):
        # 45 min/dia x 5,5 kW x 365 dias = 1.505,6 kWh
        r = calc.comparar_casa(self.params, [10, 10, 15, 10], 7)
        self.assertAlmostEqual(r["atual"]["kwh_ano"], 5.5 * 45 / 60 * 365, places=6)
        self.assertEqual(r["minutos_dia"], {"atual": 45, "A": 28})

    def test_casa_igual_a_referencia(self):
        # 4 banhos de 10 min devem dar o mesmo que 4 pessoas x 10 min
        r = calc.comparar_casa(self.params, [10] * 4, 7)
        ref = calc.comparar_com_parametros(self.params)
        for k in ("atual", "A", "B", "A+B"):
            self.assertAlmostEqual(r[k]["kwh_ano"], ref[k]["kwh_ano"], places=6)

    def test_meta_que_nao_muda_nada(self):
        with self.assertRaises(ValueError):
            calc.comparar_casa(self.params, [5, 6], 7)

    def test_banho_invalido(self):
        with self.assertRaises(ValueError):
            calc.banhos_da_casa([{"banhos_dia": 1, "minutos": 0}])


if __name__ == "__main__":
    unittest.main()
