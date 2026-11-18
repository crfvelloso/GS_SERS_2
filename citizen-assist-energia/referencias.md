# Referências

Todas as páginas foram consultadas em 17/11/2026. Os arquivos baixados estão em `dados/brutos/`.

## Dados usados nos cálculos

1. ENEL DISTRIBUIÇÃO SÃO PAULO. **Tarifa de Energia Elétrica.** Tarifas da Resolução Homologatória ANEEL nº 3.596/2026, de 30/06/2026, válidas a partir de 04/07/2026. Disponível em: <https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html>.
   - Usado: B1 residencial, TUSD R$ 472,42/MWh + TE R$ 316,96/MWh = R$ 0,78938/kWh. Tarifa Branca B1: ponta R$ 1.480,30/MWh e fora ponta R$ 669,24/MWh (TUSD + TE).
2. BRASIL. Ministério da Ciência, Tecnologia e Inovação. SIRENE. **Fatores de emissão de CO₂ pela geração de energia elétrica no Sistema Interligado Nacional – Inventários Corporativos.** Disponível em: <https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao>. Arquivo: `dados/brutos/mcti_fator_emissao_inventarios.xlsx`.
   - Usado: fator médio anual de 2025, 0,0461 tCO₂/MWh; fatores mensais de 2025 (0,0215 a 0,0778 tCO₂/MWh).
3. NASA. **POWER Project – Climatology API v2.10.1.** Parâmetros ALLSKY_SFC_SW_DWN e T2M, ponto −23,55; −46,63 (São Paulo), climatologia de janeiro de 2001 a dezembro de 2025. Disponível em: <https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN,T2M&community=RE&longitude=-46.63&latitude=-23.55&format=JSON>. Arquivo: `dados/brutos/nasa_power_sao_paulo_climatologia.json`.
4. CAIXA ECONÔMICA FEDERAL; IBGE. **SINAPI – Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil.** Composição 103517 (aquecedor solar compacto, fornecimento e instalação, R$ 3.359,57, referência 09/2026, não desonerado) e insumo 34472 (kit com reservatório de 200 L e placa de 2,0 m², R$ 3.240,00). Consulta pelo espelho público Orçamentor: <https://orcamentor.com/composicao/103517/> e <https://orcamentor.com/insumo/34472/>.
5. KOMECO. **Coletor solar linha Maxime Prime – ficha técnica.** Disponível em: <https://www.komeco.com.br/arquivos/datasheet/aquecimento-solar/coletor-solar/datasheet-coletor-solar-linha-maxime-prime.pdf>.
   - Usado só para conferência: coletor classe A de 1,96 m², 165,2 kWh/mês nas condições de ensaio do Inmetro.

## Método

6. DUFFIE, J. A.; BECKMAN, W. A. **Solar Engineering of Thermal Processes.** 4. ed. Hoboken: Wiley, 2013. Capítulo 20 (método f-chart): correlação para sistemas a líquido, correções de volume de armazenamento e de aquecimento de água de consumo, e valores típicos de FR(τα)n, FR·UL e (τα)/(τα)n.

## Contexto do produto

7. TELHANORTE. **Chuveiro Elétrico Lorenzetti Advanced Multitemperatura 127V 5500W** (ficha do produto). Disponível em: <https://www.telhanorte.com.br/chuveiro-eletrico-multitemperatura-advanced-5500w-127v-branco-lorenzetti-585556/p>.
   - Usado: potência nominal de 5.500 W, adotada na família de referência como exemplo de chuveiro comum.
