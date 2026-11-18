# Roteiro do vídeo (máximo 3 minutos)

Publicar no YouTube como **não listado**. Gravar a tela com o terminal em fonte grande e o gráfico `analise/grafico_mensal.svg` aberto no navegador.

| Tempo | O que mostrar | O que falar |
| --- | --- | --- |
| 0:00 – 0:20 | Apresentação | Nomes e RMs. "Esta é a contribuição de Soluções em Energias Renováveis e Sustentáveis ao Citizen Assist AI." |
| 0:20 – 0:45 | Público e necessidade | "Nosso público são famílias da área da Enel SP que esquentam a água do banho com chuveiro elétrico. Um chuveiro de 5.500 W ligado 10 minutos gasta 0,92 kWh; numa casa de 4 pessoas, são 1.338 kWh e R$ 1.056 por ano, sem impostos." |
| 0:45 – 1:25 | Análise e comparação | Tabela de `analise/resultados.md` e o gráfico mensal. "Comparamos, para o mesmo ano: A, banho de 7 minutos, sem custo, economiza R$ 317; B, aquecedor solar, fonte renovável, custa R$ 3.360 pelo SINAPI e economiza R$ 810, retorno em cerca de 4 anos. Calculamos a parte do sol mês a mês pelo método f-chart com dados da NASA: 77% no ano, só 58% em junho." |
| 1:25 – 2:20 | Demonstração no assistente | Rodar `python3 src/assistente_energia.py`. Opção 2 com a família de referência e resposta "s" para telhado. Mostrar também a pergunta "Todos tomam o mesmo número de banhos?": respondendo "n", o assistente pergunta os banhos de cada morador. Depois opção 2 de novo respondendo "n" para telhado, para mostrar que a recomendação muda para quem mora de aluguel. Digitar uma letra num campo numérico para mostrar a validação. Mostrar a opção 7, criada depois dos testes com usuários. |
| 2:20 – 2:50 | Recomendações e limitações | Opção 6. "Recomendamos começar pelo banho mais curto, que serve para qualquer casa. O aquecedor solar vale um orçamento para quem tem casa própria com telhado ao sol. Os valores são estimativas: a tarifa não tem impostos, o coletor tem parâmetros típicos e o custo é uma média nacional." |
| 2:50 – 3:00 | Encerramento | "Fontes e cálculos estão no repositório." Mostrar o link do GitHub. |
