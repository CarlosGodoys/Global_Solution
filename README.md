# Sistema Inteligente de Monitoramento - Missão Espacial

## Global Solution - FIAP 2026

---

## Equipe

| Nome | RM |
|------|------|
| [Nome do Integrante 1] | [RM00000] |
| [Nome do Integrante 2] | [RM00000] |
| [Nome do Integrante 3] | [RM00000] |
| [Nome do Integrante 4] | [RM00000] |
| [Nome do Integrante 5] | [RM00000] |

---

## Resumo do Problema

Missões espaciais modernas dependem de sistemas inteligentes de monitoramento contínuo para garantir a segurança operacional. Este projeto simula um sistema capaz de receber, interpretar e exibir dados de telemetria de uma missão espacial experimental, identificando situações críticas, gerando alertas automáticos e fornecendo recomendações para manter a operação em condições normais ou de crise.

O cenário analisado abrange 4 dias de operação de uma estação espacial, monitorando 6 módulos críticos, geração/consumo de energia, variáveis ambientais e log de eventos.

---

## Estrutura do Repositório

```
Global_Solution/
├── README.md
├── src/
│   ├── sistema.py          # Código principal (executável)
│   └── sistema.ipynb       # Notebook Jupyter (desenvolvimento)
├── data/
│   └── dados.csv           # Dados simulados de telemetria (100 registros)
└── docs/
    ├── relatorio.pdf       # Relatório técnico (4-8 páginas)
    ├── link_video.txt      # Link do vídeo no YouTube
    └── uso_ia.md           # Registro de uso de IA (opcional)
```

---

## Estruturas de Dados Utilizadas

| Estrutura | Aplicação | Justificativa |
|-----------|-----------|---------------|
| **Lista** | Séries temporais (geração solar, consumo, reserva) | Armazena dados sequenciais ao longo do tempo |
| **Fila (FIFO)** | Alertas pendentes por ordem de chegada | Processa alertas na ordem em que ocorreram |
| **Pilha (LIFO)** | Últimos eventos críticos analisados | Acesso rápido ao evento mais recente |
| **Dicionário** | Status dos módulos por nome | Acesso direto O(1) ao estado de cada módulo |
| **Hierarquia** | Organização da missão (energia → solar/eólica/baterias) | Representa a relação entre subsistemas |
| **Matriz** | Leituras por horário × variável (24h × 6 variáveis) | Visão tabular dos dados multidimensionais |

---

## Regras Lógicas Principais

### Expressão Booleana do Diagnóstico

```
CRITICO = (suporte_vida == 0) OR (energia == 0 AND reserva < 30) OR (comunicacao == 0 AND qualidade < 20)
ALERTA  = (reserva < 40) OR (NOT comunicacao AND qualidade < 50) OR (radiacao > 7)
NORMAL  = NOT CRITICO AND NOT ALERTA
```

### Regras Implementadas

| # | Regra | Operadores | Resultado |
|---|-------|-----------|-----------|
| 1 | Suporte à vida OFF ou energia OFF com reserva < 30% | OR, AND | CRÍTICO |
| 2 | Comunicação OFF e qualidade < 20% | AND, NOT | CRÍTICO |
| 3 | Reserva < 40% ou radiação > 7.0 | OR | ALERTA |
| 4 | Habitat OFF e temperatura fora de 18-25°C | AND, NOT | CRÍTICO |

---

## Técnica de Previsão

**Método:** Regressão Linear (sklearn - LinearRegression)

**Variável analisada:** Reserva energética (%)

**Dados utilizados:** Últimas 24 leituras horárias de `reserva_energia_pct`

**Metodologia:**
1. Treina um modelo linear com X = horas (0-23) e y = valores de reserva
2. Gera a equação da reta: `reserva = a + b * hora`
3. Projeta os valores para as próximas 6 horas (horas 24-29)

**Influência na decisão:**
- Previsão < 30% → Alerta urgente: ativar modo economia imediatamente
- Previsão < 50% → Atenção: monitorar consumo
- Previsão ≥ 50% → OK: níveis adequados

---

## Como Executar

### Pré-requisitos

```bash
pip install pandas numpy scikit-learn
```

### Execução

```bash
cd Global_Solution
python src/sistema.py
```

### Notebook (opcional)

Abrir `src/sistema.ipynb` no Jupyter Notebook ou VS Code e executar as células sequencialmente.

---

## Exemplo de Entrada e Saída

### Entrada (registro do CSV):

```
timestamp: 2026-06-02 03:00
suporte_vida: 1, energia: 0, comunicacao: 1, habitat: 1, laboratorio: 0, armazenamento: 1
geracao_solar: 0.0 kWh, geracao_eolica: 8.0 kWh, consumo: 20.5 kWh
reserva_energia: 32%, temperatura_interna: 20.0°C, radiacao_uv: 1.3
qualidade_comunicacao: 78%, evento: "Energia critica - reserva abaixo de 35%"
```

### Saída do sistema:

```
[2026-06-02 03:00] NIVEL: ALERTA
  Alertas: Energia baixa
  Recomendacoes:
    -> [ALTA] Desligar sistemas nao essenciais (laboratorio, armazenamento)
    -> [ALTA] Redirecionar energia para habitat e suporte a vida

PREVISAO: Reserva prevista em 65.2% em 6h. Niveis adequados.
```

---

## Recomendações Geradas pelo Sistema

O sistema gera recomendações automáticas priorizadas por severidade:

| Prioridade | Situação | Ação Recomendada |
|-----------|----------|------------------|
| CRÍTICA | Sistemas vitais comprometidos | Restaurar suporte à vida e energia |
| CRÍTICA | Isolamento de comunicação | Ativar canal de emergência |
| CRÍTICA | Habitat com temperatura fora da faixa | Restaurar aquecimento imediatamente |
| ALTA | Energia baixa | Desligar sistemas não essenciais |
| ALTA | Radiação elevada | Ativar protocolo de proteção radiológica |
| MÉDIA | Comunicação instável | Tentar reconexão via canal secundário |

---

## Inconsistência Proposital nos Dados

O registro de **2026-06-03 às 13:00** apresenta radiação UV = 6.5 (acima do limiar de alerta) mas severidade marcada como "normal" com evento dizendo "sensores reportam normal". O sistema detecta essa anomalia e recomenda recalibração do sensor.

---

## Vídeo de Apresentação

[Link do vídeo no YouTube - Não Listado]

---

## Conclusões e Aprendizados

- A organização de dados em estruturas adequadas (filas, pilhas, dicionários) facilita o processamento e a tomada de decisão em sistemas críticos
- Regras lógicas bem definidas permitem classificação automática de situações operacionais sem intervenção humana
- Técnicas simples de previsão (regressão linear) já permitem antecipar problemas e agir preventivamente
- A detecção de inconsistências nos dados é fundamental para garantir a confiabilidade das decisões do sistema
- Em operações espaciais, a capacidade de reagir rapidamente com base em dados é essencial para a segurança da tripulação
