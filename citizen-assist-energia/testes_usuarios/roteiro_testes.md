# Roteiro dos testes com usuários

**Objetivo:** verificar se as orientações de energia do Citizen Assist AI são compreendidas e úteis para quem usa chuveiro elétrico.

## Participantes

- De 3 a 5 pessoas do público escolhido (moram em casa com chuveiro elétrico), de preferência com pouca familiaridade com energia.
- Cada pessoa é identificada só por um código (P1, P2, …). Não anote nome, telefone, endereço, número de cliente nem valores da conta de luz.
- Antes de começar, explique que é um teste de um protótipo acadêmico, que ninguém está sendo avaliado e que a pessoa pode parar quando quiser. Anote o "sim" verbal no registro.

## Preparação

1. Abra um terminal na pasta do projeto e rode `python3 src/assistente_energia.py`.
2. Peça à pessoa que use o assistente sozinha. Só ajude se ela travar por mais de 1 minuto e anote onde travou.

## Situações testadas

| # | Situação | O que pedir | O que observar |
| --- | --- | --- | --- |
| S1 | Gasto do chuveiro | "Descubra quanto o chuveiro da sua casa gasta por mês." | Encontrou a opção 1? Sabia a potência do chuveiro? Entendeu kWh e R$? |
| S2 | Comparação | "Veja o que vale a pena fazer para gastar menos." | Entendeu a tabela? Sabe explicar a diferença entre A e B? |
| S3 | Recomendação | "O assistente recomenda o aquecedor solar para você? Por quê?" | A resposta faz sentido para a situação dela (casa própria, aluguel)? |
| S4 | Limitações | "Esses valores são garantidos?" | Encontrou a opção 6? Entendeu que são estimativas? |
| S5 | Entrada errada | "Digite uma letra quando ele pedir um número." | A mensagem de erro foi clara? |

## Perguntas ao final

1. De 1 a 5, quão fácil foi entender as respostas?
2. De 1 a 5, quão útil foi a orientação para a sua casa?
3. O que ficou confuso?
4. Você mudaria algum hábito depois de usar? Qual?
5. O que você acrescentaria?

## Depois dos testes

- Preencha [`registro_testes.md`](registro_testes.md) com o que foi observado e dito, sem dados pessoais.
- Para cada problema, decida o ajuste, faça a alteração no código ou no texto e anote o que mudou.
