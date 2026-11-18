# Registro dos testes com usuários

Testes feitos com o [roteiro](roteiro_testes.md). Cada participante aparece só por um código, sem nome nem dados da conta de luz.

**Data dos testes:** 18/11/2026
**Aplicado por:** Guilherme Figueira Velloso (RM 568827)
**Versão testada:** assistente de 18/11/2026, antes dos ajustes. Os três participantes usaram a mesma versão; os ajustes foram feitos depois, de uma vez.

## Participantes

| Código | Faixa etária | Moradia | Conhecia kWh? | Consentimento verbal |
| --- | --- | --- | --- | --- |
| P1 | 60 a 70 anos | Casa própria | Não: já tinha visto na conta, mas não sabia explicar | Sim |
| P2 | 25 a 30 anos | Apartamento alugado | Em parte: sabia que aparece na conta, mas não como é calculado | Sim |
| P3 | 13 a 15 anos | Apartamento próprio, mora com os pais | Não: nunca tinha ouvido falar | Sim, com autorização dos pais (menor de idade) |

## Resultados por situação

| Participante | Situação | Conseguiu sozinho? | O que aconteceu | Comentário da pessoa |
| --- | --- | --- | --- | --- |
| P1 | S1 - Gasto do chuveiro | Sim, com dúvida | Não sabia onde achar a potência do chuveiro; depois entendeu que fica na etiqueta | Achou interessante descobrir quanto o banho gasta por mês |
| P1 | S2 - Comparação | Sim, com dúvida | Não sabia o que era tarifa por kWh | Gostou de ver que o banho mais curto não custa nada para começar a economizar |
| P1 | S3 - Recomendação | Sim | Entendeu que a primeira recomendação era encurtar o banho e que o aquecedor solar exige telhado com sol e tem custo | Tem casa própria com telhado; acha interessante, mas precisaria ver se compensa financeiramente |
| P1 | S4 - Limitações | Sim | Encontrou a opção 6 e entendeu que os valores são estimativas | Achou bom ter a explicação, porque não se deve confiar em tudo sem conferir |
| P1 | S5 - Entrada errada | Sim | Digitou uma letra sem querer; leu a mensagem de entrada inválida e continuou | Achou a mensagem fácil de entender |
| P2 | S1 - Gasto do chuveiro | Sim | Precisou procurar a potência do chuveiro para preencher | Achou interessante ver o gasto mensal e quanto o banho representa na conta |
| P2 | S2 - Comparação | Sim, com dúvida | Ficou em dúvida sobre a tarifa por kWh; por morar de aluguel, pensou se valeria investir na instalação | Gostou da comparação entre banho mais curto e aquecedor solar |
| P2 | S3 - Recomendação | Sim | O assistente não recomendou o aquecedor solar e indicou o banho mais curto | Concordou: no apartamento alugado não pode fazer obra nem instalar nada no telhado |
| P2 | S4 - Limitações | Sim | Encontrou a opção 6 e entendeu que os valores não incluem impostos e bandeiras | Achou importante a informação |
| P2 | S5 - Entrada errada | Sim | Digitou uma letra; a mensagem pediu um número e ele continuou | Achou a mensagem bem clara |
| P3 | S1 - Gasto do chuveiro | Sim, com ajuda | Não sabia onde achar a potência do chuveiro e perguntou aos pais | Achou legal descobrir quanto dinheiro o banho gasta por mês |
| P3 | S2 - Comparação | Sim, com dúvida | Achou algumas perguntas difíceis; não sabia o que era tarifa por kWh e ficou confuso com os números | Gostou de ver quanto dá para economizar com banhos mais curtos |
| P3 | S3 - Recomendação | Sim | Entendeu que o aquecedor solar exige telhado com sol e autorização; o assistente recomendou encurtar o banho | Concordou: em apartamento não seria fácil, e o banho curto não custa nada |
| P3 | S4 - Limitações | Sim | Encontrou a opção 6 e entendeu que os valores são estimativas | Achou interessante a explicação |
| P3 | S5 - Entrada errada | Sim | Digitou uma letra; entendeu o erro e continuou | Sem dificuldade |

## Perguntas finais

| Participante | Facilidade (1 a 5) | Utilidade (1 a 5) | O que ficou confuso | Mudaria algum hábito? |
| --- | --- | --- | --- | --- |
| P1 | 4 | 5 | As palavras kWh, potência e tarifa; pediu explicações mais simples | Banhos mais curtos, fechar o chuveiro ao se ensaboar e usar a posição mais fria nos dias quentes |
| P2 | 5 | 4 | A tarifa por kWh e alguns cálculos de economia; sugeriu explicações com exemplos e comparação direta com a conta de luz | Banhos mais curtos, fechar o chuveiro ao se ensaboar e usar a posição de menor aquecimento nos dias quentes |
| P3 | 4 | 5 | As palavras kWh, potência e tarifa; pediu explicações mais simples | Banhos mais rápidos, fechar o chuveiro ao se ensaboar e contar aos pais o que aprendeu |

## Problemas observados

| Problema | Apontado por |
| --- | --- |
| Não sabia onde encontrar a potência do chuveiro | P1, P2, P3 |
| Não entendeu o que é a tarifa por kWh | P1, P2, P3 |
| Palavras técnicas (kWh, potência, tarifa) sem explicação simples | P1, P3 |
| Números e cálculos de economia pouco explicados; pediu exemplos | P2, P3 |
| Dúvida se o aquecedor solar compensa financeiramente, mesmo com o retorno mostrado | P1 |
| Quer comparar os resultados diretamente com a conta de luz | P2 |

**Resumo:** os três conseguiram usar todas as opções, e todos entenderam a recomendação e as limitações. A mensagem de erro foi clara para os três. Facilidade média 4,3 e utilidade média 4,7 (de 1 a 5). O ponto fraco comum foi o vocabulário: potência, kWh e tarifa.

## Ajustes realizados

Feitos depois dos três testes, em `src/assistente_energia.py`.

| Problema observado | Quem apontou | Ajuste feito |
| --- | --- | --- |
| Não sabia onde encontrar a potência | P1, P2, P3 | Antes da pergunta, o assistente explica o que é potência, onde achar (etiqueta, caixa, manual ou nota da compra, com exemplo "127 V 5500 W") e que dá para apertar Enter se não encontrar |
| Não entendeu a tarifa por kWh | P1, P2, P3 | Antes da pergunta, explica que tarifa é o preço de cada kWh, mostra o valor da Enel SP e diz que dá para apertar Enter |
| Palavras técnicas sem explicação | P1, P3 | Nova opção 7 no menu, "O que significam kWh, potência e tarifa?", com explicações simples e um exemplo de conta; aviso dessa opção no começo das perguntas; a opção 1 explica que kWh é a medida da conta de luz |
| Números e cálculos de economia pouco explicados | P2, P3 | Legenda "Como ler a tabela" embaixo da comparação e um exemplo por banho (quantos kWh e reais um banho mais curto economiza) |
| Dúvida se o aquecedor compensa | P1 | O retorno passou a ser explicado em palavras: "em cerca de X anos o que a casa deixa de pagar de luz paga o aquecedor" |
| Comparar com a conta de luz | P2 | A opção 2 agora pergunta o consumo da conta em kWh e mostra quanto cada alternativa reduz, em kWh por mês e em porcentagem da conta |
