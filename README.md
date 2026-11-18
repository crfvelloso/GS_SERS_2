# Citizen Assist AI — Energia no banho

Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis** para o Citizen Assist AI (Global Solution 2026.2, Ciência da Computação, turma 1CCA).

## Integrantes

| Nome | RM |
| --- | --- |
| Guilherme Figueira Velloso | 568827 |
| José Manfrinato | 571151 |

## Público e problema

**Público:** famílias da Grande São Paulo atendidas pela Enel SP que aquecem a água do banho com chuveiro elétrico.

**Problema:** o chuveiro elétrico é o aparelho de maior potência da casa e o gasto dele passa despercebido. Numa casa de 4 pessoas com chuveiro de 5.500 W e banhos de 10 minutos, são cerca de 1.338 kWh e R$ 1.056 por ano, sem impostos.

**Alternativas comparadas** para a mesma necessidade (água quente para o banho) e o mesmo período (1 ano):

| Alternativa | Economia (R$/ano) | Investimento | Retorno |
| --- | --- | --- | --- |
| A - Banho de 7 minutos | 316,94 | nenhum | imediato |
| B - Aquecedor solar (fonte renovável) com o chuveiro como apoio | 809,72 | R$ 3.359,57 (SINAPI) | 4,1 anos |
| A+B - As duas medidas | 963,53 | R$ 3.359,57 | 3,5 anos |

Valores da família de referência, com a tarifa B1 da Enel SP sem tributos. São estimativas, não garantias. Dados, método, custos, viabilidade e impactos ambientais estão em [`analise/analise_energetica.md`](analise/analise_energetica.md).

## Funcionalidades de energia

O assistente roda no terminal e oferece:

1. **Quanto o chuveiro gasta na minha casa:** calcula kWh e reais por mês e por ano a partir da potência e dos banhos da casa, e mostra a parte da conta que o banho representa. Quando os moradores têm hábitos diferentes, o assistente pergunta os banhos de cada um.
2. **Comparar alternativas para a minha casa:** monta a tabela da situação atual, A, B e A+B com os dados do usuário, explica como ler a tabela e dá uma recomendação que muda conforme a casa (telhado próprio ou não, número de banhos dentro ou fora da faixa do kit solar). Se o usuário informar o consumo da conta de luz, mostra quanto cada alternativa reduz em porcentagem da conta.
3. **Análise da família de referência:** os mesmos números deste README.
4. **Dicas de uso consciente no banho.**
5. **Referências** usadas nos cálculos.
6. **Limitações** das estimativas.
7. **O que significam kWh, potência e tarifa:** explicações simples, com um exemplo de conta.

As explicações das perguntas, a opção 7, a legenda da tabela e a comparação com a conta foram acrescentadas depois dos [testes com usuários](testes_usuarios/registro_testes.md).

O assistente não pede nome, endereço, CPF nem número de cliente, e não grava as respostas. Entradas inválidas (letras, valores fora da faixa, linha vazia) são recusadas com uma mensagem e a pergunta é repetida.

## Como executar

Requisito: Python 3.8 ou mais recente. Não há bibliotecas externas.

Assistente:

```bash
python3 src/assistente_energia.py
```

Testes automáticos dos cálculos (28 testes):

```bash
python3 -m unittest discover -s tests -v
```

Gerar de novo as tabelas, os CSVs e o gráfico da análise a partir de `dados/parametros.json`:

```bash
python3 src/gerar_analise.py
```

No Windows, troque `python3` por `python`.

## Exemplo de uso

Trecho de uma sessão real (opção 2, família de referência, casa alugada):

```
Quantas pessoas tomam banho na casa? [Enter = 4]:
Potência do chuveiro em watts [Enter = 5.500]:
Duração média de cada banho (minutos) [Enter = 10,00]:
...
A casa tem telhado com sol e vocês podem fazer obra nele? (s/n): n

--- O que o Citizen Assist AI recomenda ---
1) Comece limitando cada banho a 7 minutos: não custa nada e
   pode economizar cerca de R$ 316,94 por ano (402 kWh) e uns 13 mil litros de água.
   Exemplo: um banho de 10 minutos que passa a durar 7 gasta 0,28 kWh a menos,
   cerca de R$ 0,22 por banho.
2) O aquecedor solar precisa de telhado com sol e permissão para obra.
   Sem isso (apartamento, casa alugada), o banho mais curto é a melhor opção.
```

## Estrutura do repositório

| Caminho | Conteúdo |
| --- | --- |
| `src/calculos.py` | Cálculos de energia, f-chart, custos, retorno e emissões |
| `src/assistente_energia.py` | Assistente interativo (integração ao Citizen Assist AI) |
| `src/gerar_analise.py` | Gera `analise/resultados.md`, os CSVs e o gráfico |
| `tests/test_calculos.py` | Testes automáticos, incluindo um mês calculado à mão |
| `dados/parametros.json` | Todos os dados, com unidade, origem, período e tipo (real ou estimado) |
| `dados/brutos/` | Arquivos originais baixados da NASA POWER e do MCTI |
| `analise/analise_energetica.md` | Análise completa: dados, método, resultados, comparação, justificativas e limitações |
| `analise/resultados.md` | Tabelas geradas pelo código, inclusive mês a mês e sensibilidade |
| `analise/*.csv`, `analise/grafico_mensal.svg` | Resultados em CSV e gráfico mensal |
| `referencias.md` | Referências com data de consulta |
| `testes_usuarios/` | Roteiro e registro dos testes com 3 usuários, com os ajustes feitos |
| `video/roteiro_video.md` | Roteiro do vídeo de até 3 minutos |
| `entrega.txt` | Arquivo de entrega com nomes, RMs e links |

## Limitações principais

- A tarifa não inclui ICMS, PIS/COFINS nem bandeira tarifária.
- O consumo supõe o chuveiro na potência máxima o banho inteiro.
- O aquecedor solar usa parâmetros típicos de coletor plano e irradiação no plano horizontal.
- O custo do SINAPI é uma média nacional; a instalação numa casa específica pode custar mais.
- O retorno é simples, sem juros, reajuste nem manutenção.

Lista completa em [`analise/analise_energetica.md`](analise/analise_energetica.md#8-limitações).

## Aviso

Protótipo acadêmico. Não é canal oficial da Enel, da ANEEL nem de qualquer órgão público, e não garante economia. Antes de instalar um aquecedor solar, peça orçamentos a instaladores e confira a etiqueta do Inmetro.
