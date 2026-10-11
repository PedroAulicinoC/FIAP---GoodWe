# Módulo de Inteligência Artificial e Otimização Energética

Projeto: FIAP - GoodWe
Sprint: 2

## 1. Objetivo

Desenvolver um protótipo para analisar telemetria de recargas de
veículos elétricos, estimar energia acumulada e distribuir a potência
disponível entre veículos.

## 2. Componentes

### detector_anomalias.py

Identifica dados ausentes ou inválidos, medições fora das faixas de
teste e estados Warning ou Fault.

Faixas ilustrativas utilizadas:
- Tensão: 200 a 240 V
- Corrente: 0 a 32 A
- Potência: 0 a 7,4 kW
- Temperatura: -20 a 50 °C

Esses limites não são especificações oficiais da GoodWe.

### previsao_demanda.py

Utiliza regressão linear para estimar a energia acumulada em função
do tempo decorrido da sessão.

A estimativa é experimental e ainda não foi validada para prever
a demanda energética futura real.

### smart_charging.py

Distribui a potência disponível entre veículos, respeitando o limite
total e a potência solicitada por cada veículo.

O algoritmo é demonstrativo e não controla carregadores reais.

## 3. Resultados dos testes

### Detecção de anomalias
- Registros analisados: 24
- Registros com alertas: 2
- Registros sem alertas: 22

### Previsão de energia
- Tempo considerado: 30 minutos
- Energia estimada: 3,435 kWh
- Resultado experimental, sem validação preditiva independente.

### Smart Charging
- Solicitações: 2 kW, 7 kW e 7 kW
- Limite total: 11 kW
- Distribuição: 2 kW, 4,5 kW e 4,5 kW
- Limite respeitado: Sim
- Solicitações respeitadas: Sim

## 4. Limitações

- Os testes utilizam dados simulados.
- As faixas elétricas são ilustrativas.
- A previsão precisa de mais dados históricos e validação.
- O algoritmo não se comunica com carregadores reais.
- O protótipo não substitui proteções ou sistemas certificados.

## 5. Arquivos

- detector_anomalias.py
- previsao_demanda.py
- smart_charging.py
- README_IA.md
