# EV ChargeOps — Gestão e Rateio Inteligente de Recarga de Veículos Elétricos
Enterprise Challenge 2026 — Parceria GoodWe + FIAP (Energy Innovation Lab - Aclimação L1)

---

## 1. Sobre o Projeto
O EV ChargeOps é uma solução voltada para condomínios e ambientes compartilhados com carregadores de veículos elétricos (modelo GoodWe HCA G2). A plataforma resolve o desafio de medir o consumo individual em kWh, estruturar dados de telemetria das sessões e aplicar um modelo de rateio condominial justo, em conformidade com as diretrizes da Resolução Normativa ANEEL nº 1.000/2021.

---

## 2. O Que Foi Desenvolvido na Sprint 2

### Frente 1: Ingestão de Dados e Telemetria
Nesta frente, foi construído o módulo responsável por conectar o sistema à fonte de dados e telemetria:
- Conexão e integração estruturada com a API GoodWe (SEMS Portal).
- Modo simulado (Mock OCPP) para testes locais contínuos sem dependência do carregador físico da bancada estar ativo.
- Captura e normalização de grandezas elétricas em tempo real: Tensão (V), Corrente (A), Potência Ativa (kW), Energia Acumulada (kWh) e identificadores de usuário/sessão (RFID).
- Exportação de dados estruturados em JSON e CSV para alimentar o banco de dados, a lógica de rateio e os algoritmos de Inteligência Artificial do grupo.

### Frente 2: Back-end Core e Motor de Rateio
Nesta frente, foi desenvolvido o núcleo das regras de negócio e faturamento individualizado:
- Implementação da fórmula de rateio híbrido: $\text{Fatura} = (\text{kWh} \times \text{Tarifa}) + \text{Taxa de Manutenção}$
- Processamento das leituras de telemetria contínua.
- Aplicação automática das regras de exceção mapeadas na Sprint 1:
  1. **Sessões Interrompidas Prematuramente**: cobrança proporcional ao volume em kWh medido até o encerramento.
  2. **Isenção de Moradores sem Recarga no Mês**: moradores sem sessões de recarga no período ficam com custo de energia zerado e isentos da taxa fixa de manutenção, conforme a regra de negócio adotada pelo grupo.
  3. **Consolidação por Unidade Residencial**: agrupamento dos consumos associados a uma mesma unidade em um único extrato consolidado.
- Emissão de extratos financeiros detalhados por unidade para prestação de contas no condomínio.

### Frente 3: Modelagem, Persistência e Auditoria (Banco de Dados)
Nesta frente, foi implementado um banco de dados relacional SQLite para armazenar e consultar as informações do EV ChargeOps:
- Criação das tabelas de apartamentos, usuários, identificadores RFID, sessões de recarga, leituras de telemetria, faturas e auditoria.
- Relacionamento entre moradores, apartamentos e identificadores de acesso por meio de chaves estrangeiras.
- Persistência do histórico de sessões, incluindo identificadores externos, horários, status, energia acumulada e origem dos dados.
- Armazenamento das leituras de telemetria, incluindo tensão, corrente, potência, energia, timestamp e status operacional.
- Persistência das faturas mensais consolidadas por apartamento, com consumo, tarifa, custo de energia, taxa de manutenção e valor total.
- Registro de eventos de auditoria para acompanhar operações como cadastro, ingestão de telemetria e geração de faturas.
- Implementação de consultas para listar moradores, sessões, leituras, faturas e eventos de auditoria.
- Criação de índices para auxiliar o desempenho das consultas utilizadas pelo sistema.

### Frente 4: Painel Web do Gestor Predial (Front-end)
Nesta frente, foi desenvolvido um painel web em Streamlit que consome diretamente o banco SQLite, permitindo ao gestor predial acompanhar o faturamento, as sessões e a trilha de auditoria:
- Painel com quatro abas: Visão geral, Faturas, Sessões e telemetria e Auditoria (detalhadas na seção 7).
- Seletor de mês de referência, que atualiza os indicadores e o extrato por apartamento.
- Gráficos interativos de consumo por apartamento, sessões por status e telemetria por sessão (potência, tensão, corrente e energia acumulada).
- Destaque visual das regras de exceção da Sprint 1: sessões interrompidas, sessões com falha, apartamentos isentos e leituras atípicas.
- Exportação do extrato mensal em CSV.
- Identidade visual inspirada na GoodWe, em verde e branco, com efeito glassmorphism e suporte a modo claro e modo escuro.
- Acesso ao banco em modo somente leitura, garantindo que o painel não altere os dados persistidos.

---

## 3. Estrutura dos Arquivos da Sprint 2

### Módulo de Ingestão e Telemetria
- `ingestion_service.py`: módulo principal contendo a classe `GoodWeIngestionService`. Realiza a integração com a fonte de dados, coleta e normalização das leituras operacionais e simulação das sessões.
- `teste_ingestao.py`: script de validação da ingestão, utilizado para testar o monitoramento e registrar amostras.
- `gerar_dataset_sprint2.py`: gerador de massa de dados de teste. Cria séries temporais com três cenários:
  1. **Sessão Normal**: recarga finalizada com sucesso.
  2. **Sessão Interrompida**: encerramento antecipado para testar a regra de rateio proporcional.
  3. **Sessão com Anomalia**: valores elétricos atípicos para testes dos modelos de IA.
- `telemetria_sessoes.json` / `telemetria_sessoes.csv`: arquivos com amostras de telemetria geradas pelo script de teste.
- `telemetria_sprint2_consolidada.json` / `telemetria_sprint2_consolidada.csv`: bases consolidadas utilizadas pelo banco de dados, motor de rateio e demais módulos.

### Módulo do Motor de Rateio e Regras de Negócio
- `motor_rateio.py`: módulo contendo as funções de leitura da telemetria, agrupamento por RFID/unidade, consolidação do consumo em kWh, regras de isenção e cálculo das faturas.
- `teste_rateio.py`: script de integração e validação do motor de rateio. Consome os dados consolidados e emite os extratos financeiros por apartamento.

### Módulo de Banco de Dados, Persistência e Auditoria
- `database.py`: implementa a classe `Database`, responsável pela criação do banco SQLite, definição das tabelas, cadastro de entidades, persistência das sessões e leituras, armazenamento de faturas e registro de eventos de auditoria.
- `popular_banco.py`: popula o banco com dados iniciais de apartamentos, moradores e identificadores RFID.
- `importar_dataset.py`: importa as leituras do arquivo consolidado para o banco de dados, relacionando as sessões aos identificadores cadastrados.
- `gerar_faturamento_mensal.py`: processa a base de telemetria, executa o cálculo de rateio e salva as faturas mensais consolidadas no banco.
- `verificar_banco.py`: consulta as tabelas e apresenta informações para validar a persistência dos dados.
- `testar_auditoria.py`: consulta os registros de auditoria para validar o histórico de eventos do sistema.
- `ev_chargeops.db`: arquivo SQLite criado automaticamente durante a execução, que armazena os dados persistidos.

### Módulo do Painel Web (Front-end)
- `app.py`: aplicação Streamlit com as quatro abas do painel. Lê o `ev_chargeops.db` em modo somente leitura (via consultas SQL com JOINs entre faturas, sessões, identificadores, usuários e apartamentos) e monta indicadores, tabelas e gráficos.
- `glass.py`: tema visual do painel. Contém o CSS do efeito glassmorphism, as paletas dos modos claro e escuro, a paisagem de fundo (SVG embutido, sem arquivos externos) e a função `glass_fig`, que aplica o estilo aos gráficos Plotly.
- `.streamlit/config.toml`: configuração dos temas claro e escuro do Streamlit (cores primária, de fundo e de texto) e desativação da coleta de estatísticas de uso. Deve ficar dentro da pasta `sprint-2`.

---

## 4. Requisitos e Como Executar

### Pré-requisitos
- Python 3.10 ou superior.
- Biblioteca `requests`, necessária para chamadas HTTP à API GoodWe quando o modo simulado não estiver sendo utilizado.
- SQLite, utilizado pelo módulo `sqlite3` da biblioteca padrão do Python.
- Para o painel web: bibliotecas `streamlit` (versão recente, de preferência 1.46 ou superior, para o suporte aos temas claro e escuro), `pandas` e `plotly`.

### Execução

#### 4.1. Acessar a pasta do projeto
Abra o terminal e navegue até a pasta da Sprint 2:

```bash
cd ~/Documents/Projetos/Python/FIAP---GoodWe/sprint-2
```

#### 4.2. Instalar a dependência opcional
```bash
python3 -m pip install requests
```
A instalação pode ser dispensada para os testes que utilizam exclusivamente dados simulados, desde que o módulo não exija a biblioteca ao ser importado.

#### 4.3. Gerar a base de telemetria
```bash
python3 gerar_dataset_sprint2.py
```
Esse comando gera os arquivos consolidados JSON e CSV utilizados nos testes.

#### 4.4. Popular o banco de dados
```bash
python3 popular_banco.py
```
Esse comando cadastra os apartamentos, moradores e identificadores RFID iniciais.

#### 4.5. Importar a telemetria para o banco
```bash
python3 importar_dataset.py
```
O comando importa as sessões e as leituras de telemetria para o arquivo `ev_chargeops.db`.

#### 4.6. Gerar o faturamento mensal
```bash
python3 gerar_faturamento_mensal.py
```
Esse comando processa a base de telemetria, calcula o rateio por apartamento e salva as faturas no banco de dados.

#### 4.7. Verificar os dados persistidos
```bash
python3 verificar_banco.py
```
Utilize esse script para conferir a quantidade de registros armazenados nas tabelas do banco.

#### 4.8. Consultar as sessões registradas
```bash
python3 -c "from database import Database; db=Database(); print(*db.listar_sessoes(), sep='\n')"
```
O comando apresenta as sessões registradas, seus identificadores, moradores associados, horários, status e energia acumulada.

#### 4.9. Consultar as faturas do mês
```bash
python3 -c "from database import Database; db=Database(); print(*db.listar_faturas('2026-10'), sep='\n')"
```
O comando consulta as faturas de outubro de 2026, incluindo consumo, tarifa, custo de energia, taxa de manutenção e valor total.

Para consultar as faturas sem restringir o mês, utilize:

```bash
python3 -c "from database import Database; db=Database(); print(*db.listar_faturas(), sep='\n')"
```

#### 4.10. Testar a auditoria
```bash
python3 testar_auditoria.py
```
Esse comando apresenta os eventos registrados, como ingestão de telemetria, cadastros e salvamento de faturas.

#### 4.11. Executar os testes das demais frentes
Para testar o monitoramento de telemetria:

```bash
python3 teste_ingestao.py
```

Para testar o motor de rateio:

```bash
python3 teste_rateio.py
```

#### 4.12. Executar o painel web
Com o banco já populado e o faturamento gerado (passos 4.3 a 4.6), instale as dependências do painel e inicie a aplicação:

```bash
python3 -m pip install streamlit pandas plotly
streamlit run app.py
```

O painel abre no navegador em `http://localhost:8501`. Na primeira execução, o Streamlit pode pedir um e-mail para newsletter; basta pressionar Enter para pular.

Para alternar entre os modos claro e escuro, utilize o menu **⋮ → Settings → Theme** no canto superior direito da página (opções: Light, Dark ou Use system setting).

### Ordem recomendada para uma primeira execução completa
```bash
python3 gerar_dataset_sprint2.py
python3 popular_banco.py
python3 importar_dataset.py
python3 gerar_faturamento_mensal.py
python3 verificar_banco.py
python3 testar_auditoria.py
streamlit run app.py
```

> **Importante:** a sequência acima pressupõe um banco novo ou cadastros idempotentes. Se o banco já contém dados, evite executar novamente os scripts de população e importação sem verificar como eles tratam duplicidades. Não apague `ev_chargeops.db` para repetir os testes, pois ele contém os dados persistidos.

---

## 5. Formato dos Dados Coletados (Contrato de Dados)
As saídas geradas seguem uma estrutura padronizada:
- `timestamp`: data e hora da leitura no formato ISO.
- `charger_id`: número de série do carregador GoodWe, por exemplo, GW-HCA-G2-001.
- `status`: estado da operação, como Charging, Aborted, Fault ou Finished.
- `telemetria`: dados elétricos da leitura, como tensão (`tensao_v`), corrente (`corrente_a`), potência (`potencia_kw`), temperatura (`temperatura_c`) e frequência (`frequencia_hz`), quando disponíveis.
- `sessao`: identificadores da transação, tag RFID do morador, tempo decorrido e total de energia entregue em kWh.

---

## 6. Banco de Dados: Estrutura e Auditoria
O banco utiliza SQLite e mantém os dados organizados nas seguintes tabelas:

| Tabela | Finalidade |
|---|---|
| `apartamentos` | Cadastro das unidades residenciais. |
| `usuarios` | Cadastro dos moradores e associação aos apartamentos. |
| `identificadores` | Armazenamento dos códigos RFID vinculados aos usuários. |
| `sessoes` | Registro das sessões de recarga, status, energia acumulada e horários. |
| `leituras` | Histórico das leituras de telemetria de cada sessão. |
| `faturas` | Armazenamento das faturas mensais consolidadas por apartamento. |
| `auditoria` | Registro de eventos importantes para rastreabilidade. |

O banco possui restrições de unicidade para evitar duplicidade de cadastros, sessões e leituras. Também utiliza chaves estrangeiras para manter a integridade dos relacionamentos e índices para auxiliar as consultas mais frequentes.

Os eventos de auditoria permitem acompanhar operações de ingestão, cadastros e salvamento de faturas. As consultas implementadas podem ser utilizadas pelo motor de rateio e pelo painel web do gestor predial.

> **Observação:** os horários de início e término das sessões simuladas ainda precisam de uma validação final para garantir que representem a duração planejada de cada recarga. Esse ponto deve ser revisado antes de considerar o histórico temporal totalmente validado.

---

## 7. Painel Web do Gestor Predial (Front-end)

### Visão geral
O painel foi construído com **Streamlit**, **pandas** e **Plotly**, em Python, reutilizando o banco SQLite da Sprint 2 sem necessidade de API intermediária. Os dados são consultados diretamente do `ev_chargeops.db` e armazenados em cache por 30 segundos.

Um seletor de **mês de referência** no topo da página controla os indicadores da Visão geral e a tabela de Faturas.

### Abas

| Aba | Conteúdo |
|---|---|
| **Visão geral** | Indicadores (total faturado, energia no mês, sessões registradas com a contagem de interrompidas e apartamentos isentos), gráfico de consumo por apartamento e gráfico de sessões por status. |
| **Faturas** | Extrato por unidade no mês selecionado, com kWh, tarifa, custo de energia, taxa de manutenção, valor total e situação (Isento ou Cobrado). Permite baixar o extrato em CSV. |
| **Sessões e telemetria** | Lista de sessões com morador, apartamento e status, com filtro por status. Ao escolher uma sessão, exibe os gráficos de potência, tensão, corrente e energia acumulada, com avisos para sessões interrompidas (cobrança proporcional) e com falha. |
| **Auditoria** | Trilha dos 1000 eventos mais recentes, com filtros por ação e por entidade. |

### Regras de negócio refletidas no painel
- **Fatura**: exibida conforme a fórmula de rateio híbrido da Frente 2, `(kWh × Tarifa) + Taxa de Manutenção`.
- **Isenção**: apartamentos com valor total igual a zero são classificados como "Isento", em coerência com a regra de moradores sem recarga no mês.
- **Sessão interrompida**: sessões com status `Aborted` recebem um aviso informando a cobrança proporcional ao kWh medido.
- **Leituras atípicas**: o gráfico de telemetria destaca pontos em que a tensão se afasta mais de 15% da mediana da sessão ou a potência supera 1,5 vez a mediana. Trata-se de uma heurística simples para fins de demonstração, que **não substitui** os modelos de Inteligência Artificial do grupo.

### Identidade visual
- Paleta em **verde e branco**, remetendo ao posicionamento sustentável da GoodWe, com tipografia Poppins.
- Efeito **glassmorphism**: cartões translúcidos com desfoque de fundo, bordas suaves e sombras, sobre uma paisagem estilizada (SVG embutido no código).
- **Modo claro e modo escuro**, selecionáveis pelo menu do Streamlit. Os gráficos e o CSS acompanham o tema ativo.

### Configuração do tema
O arquivo `.streamlit/config.toml` define as cores dos dois temas:

```toml
[theme.light]
base = "light"
primaryColor = "#16A34A"
backgroundColor = "#F4FAF6"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F2A1C"

[theme.dark]
base = "dark"
primaryColor = "#16A34A"
backgroundColor = "#07191A"
secondaryBackgroundColor = "#0F2A2A"
textColor = "#FFFFFF"

[browser]
gatherUsageStats = false
```

### Decisões de projeto e cuidados
- **Somente leitura**: o painel abre o banco com `mode=ro`, portanto não consegue alterar nem corromper os dados. Não há botões que executem `popular_banco.py` ou `importar_dataset.py`, evitando o risco de duplicidade descrito na seção 4.
- **Cópia para demonstração**: para apresentações, recomenda-se copiar o banco (por exemplo, `ev_chargeops_demo.db`) e apontar a constante `DB_PATH` do `app.py` para a cópia, preservando o original.
- **Duração das sessões**: o painel não exibe a duração das sessões, pois os horários de início e término ainda aguardam validação (ver observação da seção 6). Há um aviso discreto na aba de sessões.
- **Gráficos**: o número do apartamento é tratado como categoria no eixo X, para que cada barra fique alinhada ao seu apartamento. Os gráficos usam `theme=None` no `st.plotly_chart`, para que o Streamlit não sobrescreva as cores do tema.

### Solução de problemas
- **`KeyError` em alguma coluna**: confira se os nomes usados nas consultas do `app.py` correspondem ao schema atual do banco (tabela `faturas`: `kwh_total`, `tarifa_kwh`, `custo_energia`, `taxa_manutencao`, `valor_total`).
- **Erro em `width="stretch"`**: indica versão antiga do Streamlit. Atualize com `python3 -m pip install -U streamlit` ou troque por `use_container_width=True` em `st.dataframe` e `st.plotly_chart`.
- **Modo claro/escuro não aparece no menu**: atualize o Streamlit e confirme que as seções `[theme.light]` e `[theme.dark]` estão no `.streamlit/config.toml` dentro da pasta `sprint-2`.
- **Gráfico com cores do tema anterior após trocar o modo**: recarregue a página (F5).
- **Banco não encontrado**: execute os scripts de 4.3 a 4.6 antes de iniciar o painel.
