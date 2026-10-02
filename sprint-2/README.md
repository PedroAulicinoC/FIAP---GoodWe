# EV ChargeOps — Gestão e Rateio Inteligente de Recarga de Veículos Elétricos
Enterprise Challenge 2026 — Parceria GoodWe + FIAP (Energy Innovation Lab - Aclimação L1)

---

## 1. Sobre o Projeto
O EV ChargeOps é uma solução voltada para condomínios e ambientes compartilhados com carregadores de veículos elétricos (modelo GoodWe HCA G2). A plataforma resolve o desafio de medir o consumo individual em kWh, estruturar dados de telemetria das sessões e aplicar um modelo de rateio condominial justo, em conformidade com as diretrizes da Resolução Normativa ANEEL nº 1.000/2021.

---

## 2. O Que Foi Desenvolvido na Sprint 2 (Frente 1: Ingestão de Dados)
Nesta sprint, foi construído o módulo responsável por conectar o sistema à fonte de dados e telemetria:
- Conexão e integração estruturada com a API GoodWe (SEMS Portal).
- Modo simulado (Mock OCPP) para testes locais contínuos sem dependência do carregador físico da bancada estar ativo.
- Captura e normalização de grandezas elétricas em tempo real: Tensão (V), Corrente (A), Potência Ativa (kW), Energia Acumulada (kWh) e identificadores de usuário/sessão (RFID).
- Exportação de dados estruturados em JSON e CSV para alimentar o banco de dados, a lógica de rateio e os algoritmos de Inteligência Artificial do grupo.

---

## 3. Estrutura dos Arquivos da Sprint 2

- ingestion_service.py: Módulo principal contendo a classe `GoodWeIngestionService`. Realiza a autenticação, coleta e normalização das leituras operacionais, persistência em arquivos e gerador de sessões completas.
- teste_ingestao.py: Script de validação unitária. Executa um monitoramento contínuo em tempo real (leituras a cada segundo) e grava amostras pontuais.
- gerar_dataset_sprint2.py: Gerador de massa de dados de teste para a equipe. Cria séries temporais completas com três cenários de negócio fundamentais:
  1. Sessão Normal: Recarga estável e finalizada com sucesso.
  2. Sessão Interrompida: Encerramento precoce para testar a regra de rateio proporcional.
  3. Sessão com Anomalia: Pico de corrente, queda de tensão e aquecimento atípico para teste dos modelos de IA/Machine Learning.
- telemetria_sessoes.json / telemetria_sessoes.csv: Arquivos com amostras instantâneas geradas pelo script de teste.
- telemetria_sprint2_consolidada.json / telemetria_sprint2_consolidada.csv: Bases de dados completas com todos os cenários gerados para consumo do banco de dados e do dashboard.

---

## 4. Requisitos e Como Executar

### Pré-requisitos
- Python 3.10 ou superior instalado.
- Biblioteca requests (opcional para modo simulado, necessária para chamadas à API oficial):
  pip install requests

### Execução dos Testes

1. Para testar o monitoramento em tempo real:
   python teste_ingestao.py

2. Para gerar a base de dados consolidada com os cenários para o grupo:
   python gerar_dataset_sprint2.py

---

## 5. Formato dos Dados Coletados (Contrato de Dados)
As saídas geradas seguem o padrão padronizado:
- timestamp: Data e hora da leitura no padrão ISO.
- charger_id: Número de série do carregador GoodWe (ex: GW-HCA-G2-001).
- status: Estado da operação (Charging, Aborted, Fault, Finished).
- telemetria: Dados elétricos instantâneos (tensao_v, corrente_a, potencia_kw, temperatura_c, frequencia_hz).
- sessao: Identificador da transação, tag RFID do morador, tempo decorrido e total de energia entregue em kWh.