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
-## 6. Integração com o sistema de rateio

O módulo de IA foi integrado ao motor de rateio do projeto EV ChargeOps por meio do arquivo integrador_goodwe.py.

O funcionamento da integração segue estas etapas:

Carregamento dos registros de telemetria em JSON.

Cálculo do consumo e das faturas utilizando motor_rateio.py.

Execução das análises por meio de integracao_ia.py.

Identificação das sessões com anomalias.

Associação dos alertas ao identificador da sessão e à tag RFID.

Inclusão de um status de análise da IA no relatório de faturamento.

As sessões com anomalias recebem o status REVISAR SESSAO. As demais recebem SEM ALERTAS DETECTADOS.

A IA não modifica automaticamente os valores das faturas. Os alertas indicam a necessidade de revisão pelo gestor.

## 7. Resultado do teste integrado

O teste foi executado no Google Colab utilizando 24 registros de telemetria simulada, distribuídos em três sessões.

Apartamento

Consumo

Valor da fatura

Status da IA

42

6,84 kWh

R$ 72,48

Sem alertas detectados

105

1,68 kWh

R$ 68,10

Sem alertas detectados

88

5,26 kWh

R$ 71,14

Revisar sessão

A sessão SES-003-FAULT, associada à tag RFID-APT-88, apresentou registros com alertas de tensão, corrente, potência, temperatura e estado do carregador.

A análise também identificou uma variação brusca de potência nessa sessão.

O resultado completo do teste está registrado no arquivo evidencia_integracao_goodwe.json.

## 8. Limitações da integração

O teste integrado foi realizado no Google Colab com um cadastro provisório de moradores.

A integração ainda precisa ser validada com o cadastro real armazenado no banco de dados SQLite do projeto.

A sinalização de anomalias utiliza regras e limites de teste; não representa um modelo de aprendizado de máquina treinado para classificar falhas.

As previsões de consumo são experimentais e utilizam um histórico limitado.

O Smart Charging é uma simulação de distribuição de potência, sem comunicação com carregadores reais.

Os alertas não comprovam erros de faturamento e devem ser avaliados antes de qualquer decisão de cobrança.

## 9. Arquivos adicionais

executar_ia.py: execução independente do módulo de IA.

integracao_ia.py: execução conjunta das análises de anomalias, previsão e Smart Charging.

integrador_goodwe.py: integração entre o motor de rateio e os resultados da IA.

evidencia_integracao_goodwe.json: evidência dos resultados obtidos no teste integrado.
## 10. Como executar a integração final

Na pasta sprint-2, execute os comandos:

python popular_banco.py
python modulo_ia/executar_integracao_final.py
