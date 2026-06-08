# Relatorio Tecnico - Sistema Inteligente de Monitoramento Espacial

## Global Solution - FIAP 2026

---

## 1. Introducao

Este relatorio documenta o desenvolvimento de um sistema inteligente de monitoramento para controle operacional de uma missao espacial experimental. O sistema foi construido em Python e utiliza dados simulados de telemetria para interpretar o estado da missao, classificar situacoes operacionais, gerar alertas automaticos e fornecer recomendacoes tecnicas.

O objetivo e demonstrar a aplicacao pratica de conceitos de programacao, estruturas de dados, logica computacional e analise preditiva em um cenario realista de operacao espacial.

---

## 2. Base de Dados - Justificativa e Construcao

### 2.1 Formato e Estrutura

A base de dados foi construida em formato CSV com 100 registros de telemetria, cobrindo 4 dias de operacao (01 a 04 de junho de 2026) com leituras horarias.

O formato CSV foi escolhido por ser simples, leve e amplamente suportado por ferramentas de analise de dados, alem de ser um dos formatos recomendados pelo enunciado.

### 2.2 Variaveis da Base

| Variavel | Tipo | Descricao |
|----------|------|-----------|
| timestamp | datetime | Data e hora da leitura |
| suporte_vida | binario (0/1) | Modulo de suporte a vida |
| energia | binario (0/1) | Modulo de energia |
| comunicacao | binario (0/1) | Modulo de comunicacao |
| habitat | binario (0/1) | Modulo de habitat |
| laboratorio | binario (0/1) | Modulo de laboratorio |
| armazenamento | binario (0/1) | Modulo de armazenamento |
| geracao_solar_kwh | float | Geracao de energia solar em kWh |
| geracao_eolica_kwh | float | Geracao de energia eolica em kWh |
| consumo_kwh | float | Consumo total em kWh |
| reserva_energia_pct | int | Reserva energetica em percentual |
| temperatura_interna_c | float | Temperatura interna em Celsius |
| temperatura_externa_c | float | Temperatura externa em Celsius |
| radiacao_uv | float | Nivel de radiacao ultravioleta |
| qualidade_comunicacao_pct | int | Qualidade do sinal em percentual |
| velocidade_vento_kmh | float | Velocidade do vento em km/h |
| evento | string | Descricao do evento registrado |
| severidade | string | Classificacao: normal, alerta ou critico |

### 2.3 Justificativa dos Valores

Os valores foram definidos para refletir um cenario realista:

- Geracao solar segue ciclo diurno (pico ao meio-dia, zero a noite)
- Geracao eolica e mais constante mas varia com a velocidade do vento
- Consumo varia conforme modulos ativos (maior durante o dia com laboratorio ligado)
- Reserva energetica reflete o balanco entre geracao e consumo acumulado
- Temperatura externa simula ambiente hostil (-43 a -61 graus Celsius)
- Temperatura interna se mantem na faixa habitavel (18 a 24 graus) exceto em falhas

### 2.4 Cenarios Criticos Simulados

A base contem eventos criticos realistas distribuidos ao longo dos 4 dias:

1. Queda noturna de energia (dia 2, madrugada) - reserva cai para 27%
2. Falha de comunicacao (dia 1 e dia 4) - qualidade cai para 10-15%
3. Falha de habitat (dia 3, madrugada) - temperatura interna cai para 17.5 graus
4. Pico de radiacao (dia 3, tarde) - radiacao UV atinge 9.0

### 2.5 Inconsistencia Proposital

No registro de 2026-06-03 as 13:00, a radiacao UV esta em 6.5 (acima do limiar de alerta) mas a severidade esta marcada como "normal" e o evento diz "sensores reportam normal". O registro seguinte (14:00) detecta radiacao alta de 8.5. Essa inconsistencia simula uma falha de sensor ou erro de classificacao, testando a capacidade do sistema de identificar anomalias.

---

## 3. Estruturas de Dados Aplicadas

### 3.1 Lista

Utilizada para armazenar series temporais de geracao solar, consumo e reserva energetica. Permite acesso sequencial e indexado aos dados ao longo do tempo.

```python
lista_geracao_solar = df['geracao_solar_kwh'].tolist()
```

### 3.2 Fila (FIFO)

Implementada com lista simples para organizar alertas pendentes por ordem de chegada. O primeiro alerta a entrar e o primeiro a ser processado.

```python
fila_alertas = []
fila_alertas.append(alerta)       # enfileira (final)
fila_alertas.pop(0)               # desenfileira (inicio)
```

### 3.3 Pilha (LIFO)

Utilizada para registrar eventos criticos. O ultimo evento adicionado e o primeiro a ser consultado, permitindo acesso rapido ao evento mais recente.

```python
pilha_criticos = []
pilha_criticos.append(evento)     # empilha
pilha_criticos[-1]                # consulta topo
```

### 3.4 Dicionario (Tabela Hash)

Armazena o status de cada modulo por nome, permitindo acesso direto em O(1). Cada chave e o nome do modulo e o valor contem percentual operacional, total de falhas e classificacao.

```python
status_modulos = {
    'suporte_vida': {'operacional_pct': 100.0, 'total_falhas': 0, 'status': 'NORMAL'},
    ...
}
```

### 3.5 Hierarquia (Dicionario Aninhado)

Representa a organizacao logica da missao em subsistemas:

- Energia: solar, eolica, baterias
- Habitat: oxigenio, temperatura, comunicacao

### 3.6 Matriz (Lista de Listas)

Representa leituras de 24 horas x 6 variaveis em formato tabular, facilitando a analise cruzada entre tempo e grandezas medidas.

---

## 4. Regras de Negocio e Logica do Sistema

### 4.1 Classificacao Operacional

O sistema classifica cada registro em tres niveis:

- NORMAL: todos os parametros dentro da faixa aceitavel
- ALERTA: parametros proximos de limites criticos, requer atencao
- CRITICO: risco iminente a seguranca da tripulacao ou missao

### 4.2 Expressao Booleana Principal

```
CRITICO = (suporte_vida == 0) OR (energia == 0 AND reserva < 30) OR (comunicacao == 0 AND qualidade < 20)
ALERTA  = (reserva < 40) OR (NOT comunicacao AND qualidade < 50) OR (radiacao > 7)
NORMAL  = NOT CRITICO AND NOT ALERTA
```

### 4.3 Regras Detalhadas

Regra 1 - Sistemas Vitais (AND + OR):
Se o suporte a vida esta offline OU se a energia falhou com reserva abaixo de 30%, o estado e CRITICO. Justificativa: sem suporte a vida ou energia minima, a tripulacao esta em perigo imediato.

Regra 2 - Comunicacao (AND + NOT):
Se a comunicacao esta offline E a qualidade do sinal NAO esta acima de 20%, o estado e CRITICO. Se a qualidade esta entre 20% e 50%, e ALERTA. Justificativa: isolamento total de comunicacao impede pedir socorro.

Regra 3 - Energia e Radiacao (OR):
Se a reserva esta abaixo de 40% OU a radiacao ultrapassa 7.0, o estado e ALERTA. Justificativa: ambas sao condicoes que podem escalar rapidamente para criticas.

Regra 4 - Habitat (AND + NOT):
Se o habitat esta offline E a temperatura interna NAO esta entre 18 e 25 graus, o estado e CRITICO. Justificativa: temperatura fora da faixa segura com aquecimento desligado ameaca a sobrevivencia.

### 4.4 Alertas Automaticos

O sistema gera alertas priorizados por severidade:

- CRITICA: acoes de sobrevivencia imediata (restaurar suporte a vida, ativar emergencia)
- ALTA: acoes de contencao (desligar modulos nao essenciais, redirecionar energia)
- MEDIA: acoes de manutencao (tentar reconexao, recolher equipamentos)

Cada alerta inclui uma recomendacao especifica de acao, permitindo resposta rapida e informada.

---

## 5. Analise e Previsao de Dados

### 5.1 Metodo Utilizado

Regressao Linear (sklearn - LinearRegression)

### 5.2 Variavel Analisada

Reserva energetica (%) - escolhida por ser o indicador mais critico para a continuidade da missao.

### 5.3 Metodologia

1. Selecionar as ultimas 24 leituras de reserva energetica
2. Definir X = horas (0 a 23) e y = valores de reserva
3. Treinar o modelo de regressao linear
4. Projetar os valores para as proximas 6 horas
5. Tomar decisao baseada na projecao

### 5.4 Resultado

O modelo gera uma equacao linear (y = a + b*x) que indica a tendencia da reserva. O coeficiente b indica se a reserva esta subindo ou caindo e a que taxa por hora.

### 5.5 Influencia na Decisao

A previsao alimenta diretamente o sistema de recomendacoes:

- Previsao < 30% em 6h: recomenda ativar modo economia imediatamente
- Previsao < 50% em 6h: recomenda monitorar consumo
- Previsao >= 50% em 6h: confirma niveis adequados

Isso permite acao preventiva antes que a crise ocorra.

---

## 6. Deteccao de Inconsistencias

O sistema percorre todos os registros verificando se os dados sao coerentes entre si. No caso implementado, verifica se registros com radiacao acima de 6.0 estao classificados com severidade adequada.

A inconsistencia detectada (radiacao alta com severidade "normal") demonstra que o sistema e capaz de identificar falhas de sensor ou erros de classificacao, gerando recomendacao de recalibracao.

---

## 7. Decisoes Tecnicas

### 7.1 Linguagem e Bibliotecas

- Python 3: linguagem principal
- Pandas: leitura e manipulacao do CSV
- NumPy: formatacao de arrays para sklearn
- Scikit-learn: modelo de regressao linear

A logica computacional, as regras de negocio e as estruturas de dados foram implementadas manualmente, sem depender de bibliotecas para essas funcoes.

### 7.2 Organizacao do Codigo

O codigo esta organizado em funcoes com responsabilidades claras:

- diagnosticar_registro(): aplica as regras logicas a um registro
- gerar_recomendacao(): produz recomendacoes baseadas no diagnostico
- Secoes sequenciais para leitura, organizacao, analise e relatorio

### 7.3 Formato de Saida

A saida e exibida diretamente no terminal, formatada com separadores visuais e organizacao clara por secao, priorizando informacoes criticas.

---

## 8. Conclusao

O sistema desenvolvido demonstra que e possivel construir uma ferramenta de monitoramento funcional aplicando conceitos fundamentais de computacao: estruturas de dados adequadas ao problema, logica booleana para tomada de decisao, e tecnicas simples de previsao para antecipar crises.

A principal contribuicao do projeto e a integracao entre interpretacao de dados, classificacao automatica e recomendacoes acionaveis. O sistema nao apenas detecta problemas — ele orienta a resposta, priorizando acoes por criticidade.

Em um cenario real de missao espacial, a diferenca entre reagir a uma crise e antecipa-la pode significar a sobrevivencia da tripulacao. Este projeto simula essa capacidade em escala educacional, aplicando de forma pratica os conteudos das tres primeiras fases do curso.
