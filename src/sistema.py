# Sistema Inteligente de Monitoramento - Missão Espacial
# Global Solution - FIAP 2026
# Carlos Henrique De Godoy Santos - RM: 569735
# Natália Souza Carvalho - RM: 569068

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ============================================================
# LEITURA DOS DADOS
# ============================================================
df = pd.read_csv('data/dados.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f'Total de registros: {len(df)}')
print(df.head(10))
print()

# Informacoes gerais do dataset
df.info()
print()

# ============================================================
# 1. STATUS DOS MODULOS CRITICOS (BINARIO)
# ============================================================
modulos = ['suporte_vida', 'energia', 'comunicacao', 'habitat', 'laboratorio', 'armazenamento']

# Dicionario de status dos modulos (tabela hash)
status_modulos = {}
for mod in modulos:
    total_falhas = (df[mod] == 0).sum()

    if total_falhas > 5:
        status = 'CRITICO'
    elif total_falhas > 0:
        status = 'ALERTA'
    else:
        status = 'NORMAL'

    status_modulos[mod] = {
        'operacional_pct': (df[mod] == 1).mean() * 100,
        'total_falhas': total_falhas,
        'status': status
    }

print('=' * 60)
print(f'{"MODULO":<18} {"OPERACIONAL %":<16} {"FALHAS":<10} {"STATUS"}')
print('=' * 60)
for mod, info in status_modulos.items():
    print(f'{mod:<18} {info["operacional_pct"]:>10.1f}%     {info["total_falhas"]:>4}      {info["status"]}')
print('=' * 60)
print()

# ============================================================
# 2. ORGANIZACAO DOS DADOS EM ESTRUTURAS
# ============================================================

# LISTA - Serie temporal de geracao e consumo
lista_geracao_solar = df['geracao_solar_kwh'].tolist()
lista_consumo = df['consumo_kwh'].tolist()
lista_reserva = df['reserva_energia_pct'].tolist()

print('LISTA - Ultimas 6 leituras de geracao solar:', lista_geracao_solar[-6:])
print('LISTA - Ultimas 6 leituras de consumo:', lista_consumo[-6:])
print()

# FILA - Alertas pendentes por ordem de chegada (FIFO com lista simples)
fila_alertas = []

alertas_df = df[df['severidade'].isin(['alerta', 'critico'])].copy()
for _, row in alertas_df.iterrows():
    # Enfileirar: adiciona no final da fila
    fila_alertas.append({
        'timestamp': str(row['timestamp']),
        'evento': row['evento'],
        'severidade': row['severidade']
    })

print(f'FILA DE ALERTAS - Total pendentes: {len(fila_alertas)}')
print('Proximo alerta a processar (frente da fila):', fila_alertas[0] if fila_alertas else 'Nenhum')
print()

# Desenfileirar: remove do inicio (FIFO - primeiro a entrar, primeiro a sair)
alerta_processado = fila_alertas.pop(0)
print(f'Alerta processado: {alerta_processado["evento"]}')
print(f'Alertas restantes na fila: {len(fila_alertas)}')
print()

# PILHA - Ultimos eventos criticos analisados
pilha_criticos = []

criticos_df = df[df['severidade'] == 'critico']
for _, row in criticos_df.iterrows():
    pilha_criticos.append({
        'timestamp': str(row['timestamp']),
        'evento': row['evento']
    })

print(f'PILHA DE EVENTOS CRITICOS - Total: {len(pilha_criticos)}')
print('Ultimo evento critico (topo da pilha):', pilha_criticos[-1] if pilha_criticos else 'Nenhum')
print()

# HIERARQUIA - Representacao da missao
hierarquia_missao = {
    'energia': {
        'solar': df['geracao_solar_kwh'].mean(),
        'eolica': df['geracao_eolica_kwh'].mean(),
        'baterias_reserva_pct': df['reserva_energia_pct'].mean()
    },
    'habitat': {
        'oxigenio': status_modulos['suporte_vida']['status'],
        'temperatura_media_c': df['temperatura_interna_c'].mean(),
        'comunicacao': status_modulos['comunicacao']['status']
    }
}

print('HIERARQUIA DA MISSAO:')
for sistema, sub in hierarquia_missao.items():
    print(f'  {sistema.upper()}:')
    for chave, valor in sub.items():
        if isinstance(valor, float):
            print(f'    {chave}: {valor:.2f}')
        else:
            print(f'    {chave}: {valor}')
print()

# MATRIZ - Leituras por horario e variavel (primeiras 24h)
variaveis_matriz = ['geracao_solar_kwh', 'geracao_eolica_kwh', 'consumo_kwh', 'reserva_energia_pct', 'temperatura_interna_c', 'radiacao_uv']
matriz = df[variaveis_matriz].head(24).values.tolist()

print(f'MATRIZ (24 horarios x {len(variaveis_matriz)} variaveis):')
print(f'Colunas: {variaveis_matriz}')
print(f'Dimensoes: {len(matriz)} linhas x {len(matriz[0])} colunas')
print('Primeiras 3 linhas:')
for i, linha in enumerate(matriz[:3]):
    print(f'  Hora {i:02d}: {[round(v, 1) for v in linha]}')
print()

# ============================================================
# 3. REGRAS LOGICAS DE DIAGNOSTICO
# ============================================================

def diagnosticar_registro(row):
    """
    Aplica regras logicas para classificar o estado operacional.
    
    Expressao booleana principal:
    CRITICO = (suporte_vida == 0) OR (energia == 0 AND reserva < 30) OR (comunicacao == 0 AND qualidade < 20)
    ALERTA = (reserva < 40) OR (NOT comunicacao AND qualidade < 50) OR (radiacao > 7)
    NORMAL = NOT CRITICO AND NOT ALERTA
    """
    alertas = []
    nivel = 'NORMAL'
    
    # REGRA 1 (AND + OR): Suporte a vida comprometido OU energia falhou com reserva critica
    if row['suporte_vida'] == 0 or (row['energia'] == 0 and row['reserva_energia_pct'] < 30):
        nivel = 'CRITICO'
        alertas.append('Sistemas vitais comprometidos')
    
    # REGRA 2 (AND + NOT): Comunicacao offline E qualidade abaixo do minimo
    if row['comunicacao'] == 0 and not (row['qualidade_comunicacao_pct'] > 20):
        nivel = 'CRITICO'
        alertas.append('Isolamento total de comunicacao')
    elif row['comunicacao'] == 0 and row['qualidade_comunicacao_pct'] <= 50:
        if nivel != 'CRITICO':
            nivel = 'ALERTA'
        alertas.append('Comunicacao instavel')
    
    # REGRA 3 (OR): Reserva energetica baixa OU radiacao elevada
    if row['reserva_energia_pct'] < 40 or row['radiacao_uv'] > 7.0:
        if nivel == 'NORMAL':
            nivel = 'ALERTA'
        alertas.append('Energia baixa' if row['reserva_energia_pct'] < 40 else 'Radiacao elevada')
    
    # REGRA 4 (AND + NOT): Habitat offline E temperatura fora da faixa segura
    if row['habitat'] == 0 and not (18.0 <= row['temperatura_interna_c'] <= 25.0):
        nivel = 'CRITICO'
        alertas.append('Habitat critico - temperatura fora da faixa segura')
    elif row['habitat'] == 0:
        if nivel == 'NORMAL':
            nivel = 'ALERTA'
        alertas.append('Modulo habitat offline')
    
    return nivel, alertas


# Aplicar diagnostico a todos os registros
diagnosticos = df.apply(diagnosticar_registro, axis=1)
df['nivel_diagnostico'] = [d[0] for d in diagnosticos]
df['alertas_gerados'] = [d[1] for d in diagnosticos]

print('DISTRIBUICAO DE DIAGNOSTICOS:')
print(df['nivel_diagnostico'].value_counts())
print()

# ============================================================
# 4. ALERTAS AUTOMATICOS
# ============================================================

def gerar_recomendacao(nivel, alertas, row):
    """Gera recomendacoes automaticas baseadas no diagnostico."""
    recomendacoes = []
    
    if 'Sistemas vitais comprometidos' in alertas:
        recomendacoes.append('[CRITICA] Prioridade maxima: restaurar suporte a vida e energia')
    
    if 'Isolamento total de comunicacao' in alertas:
        recomendacoes.append('[CRITICA] Ativar canal de emergencia e protocolo de reconexao')
    
    if 'Energia baixa' in alertas:
        recomendacoes.append('[ALTA] Desligar sistemas nao essenciais (laboratorio, armazenamento)')
        recomendacoes.append('[ALTA] Redirecionar energia para habitat e suporte a vida')
    
    if 'Radiacao elevada' in alertas:
        recomendacoes.append('[ALTA] Ativar protocolo de protecao radiologica')
        recomendacoes.append('[MEDIA] Recolher equipamentos externos')
    
    if 'Habitat critico' in ' '.join(alertas):
        recomendacoes.append('[CRITICA] Restaurar aquecimento imediatamente')
        recomendacoes.append('[ALTA] Tripulacao deve usar trajes termicos')
    
    if 'Comunicacao instavel' in alertas:
        recomendacoes.append('[MEDIA] Tentar reconexao via canal secundario')
    
    if not recomendacoes:
        recomendacoes.append('[INFO] Sistema operando dentro dos parametros normais')
    
    return recomendacoes


# Exibir alertas criticos e suas recomendacoes
print('=' * 70)
print('ALERTAS AUTOMATICOS DO SISTEMA')
print('=' * 70)

registros_criticos = df[df['nivel_diagnostico'] == 'CRITICO'].head(10)
for _, row in registros_criticos.iterrows():
    print(f'\n[{row["timestamp"]}] NIVEL: {row["nivel_diagnostico"]}')
    print(f'  Evento: {row["evento"]}')
    print(f'  Alertas: {", ".join(row["alertas_gerados"])}')
    recomendacoes = gerar_recomendacao(row['nivel_diagnostico'], row['alertas_gerados'], row)
    print('  Recomendacoes:')
    for rec in recomendacoes:
        print(f'    -> {rec}')
print('\n' + '=' * 70)
print()

# ============================================================
# 5. ANALISE E PREVISAO DE DADOS (Regressao Linear - sklearn)
# ============================================================

# Ultimas 24 leituras de reserva energetica
ultimas_24 = df['reserva_energia_pct'].tail(24).tolist()

# X = horas (0 a 23), y = reserva
X = np.array(range(len(ultimas_24))).reshape(-1, 1)
y = np.array(ultimas_24)

# Treinar modelo de regressao linear
modelo = LinearRegression()
modelo.fit(X, y)

# Coeficientes: y = a + b*x
a = modelo.intercept_
b = modelo.coef_[0]

print('PREVISAO DE RESERVA ENERGETICA (Regressao Linear - sklearn)')
print(f'Equacao: reserva = {a:.2f} + ({b:.4f}) * hora')
print(f'Tendencia: {"SUBINDO" if b > 0 else "CAINDO"} ({b:.4f}% por hora)')
print()

# Previsao para as proximas 6 horas
horas_futuras = np.array(range(24, 30)).reshape(-1, 1)
previsoes = modelo.predict(horas_futuras)

print('Previsao para as proximas 6 horas:')
for i, prev in enumerate(previsoes):
    print(f'  Hora +{i + 1}: {prev:.1f}%')

print()

# Decisao baseada na previsao
previsao_6h = previsoes[-1]
if previsao_6h < 30:
    print(f'>>> ALERTA: Reserva prevista em {previsao_6h:.1f}% em 6h. Ativar modo economia AGORA.')
elif previsao_6h < 50:
    print(f'>>> ATENCAO: Reserva prevista em {previsao_6h:.1f}% em 6h. Monitorar consumo.')
else:
    print(f'>>> OK: Reserva prevista em {previsao_6h:.1f}% em 6h. Niveis adequados.')
print()

# ============================================================
# 6. DETECCAO DE INCONSISTENCIA NOS DADOS
# ============================================================

print('VERIFICACAO DE INCONSISTENCIAS:')
print('-' * 50)

inconsistencias = []
for idx, row in df.iterrows():
    # Radiacao > 6.0 deveria gerar ao menos um alerta
    if row['radiacao_uv'] > 6.0 and row['severidade'] == 'normal':
        inconsistencias.append({
            'timestamp': str(row['timestamp']),
            'radiacao': row['radiacao_uv'],
            'severidade_registrada': row['severidade'],
            'evento': row['evento']
        })

if inconsistencias:
    print(f'Encontradas {len(inconsistencias)} inconsistencia(s):')
    for inc in inconsistencias:
        print(f'  [{inc["timestamp"]}] Radiacao={inc["radiacao"]} mas severidade="{inc["severidade_registrada"]}"')
        print(f'    Evento: {inc["evento"]}')
    print()
    print('DIAGNOSTICO: Falha no sensor de radiacao ou erro de classificacao.')
    print('RECOMENDACAO: Recalibrar sensor e revisar thresholds de alerta.')
else:
    print('Nenhuma inconsistencia detectada.')
print()

# ============================================================
# 7. RESUMO FINAL DA MISSAO
# ============================================================

print('=' * 70)
print('RELATORIO FINAL - SISTEMA DE MONITORAMENTO ESPACIAL')
print('=' * 70)
print(f'Periodo analisado: {df["timestamp"].min()} a {df["timestamp"].max()}')
print(f'Total de registros: {len(df)}')
print(f'Eventos criticos: {(df["nivel_diagnostico"] == "CRITICO").sum()}')
print(f'Eventos em alerta: {(df["nivel_diagnostico"] == "ALERTA").sum()}')
print(f'Eventos normais: {(df["nivel_diagnostico"] == "NORMAL").sum()}')
print(f'Inconsistencias detectadas: {len(inconsistencias)}')
print(f'Previsao de reserva em 6h: {previsao_6h:.1f}%')
print(f'Tendencia energetica: {"Positiva" if b > 0 else "Negativa"}')
print('=' * 70)
