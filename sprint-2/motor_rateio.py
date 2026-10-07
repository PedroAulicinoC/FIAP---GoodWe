import json
import os

# Abre e carrega o JSON de telemetria da frente 1:
def carregar_sessoes_json(caminho_arquivo="telemetria_sprint2_consolidada.json"):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(diretorio_atual, caminho_arquivo)

    try:
        with open(caminho_completo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        print(f"[OK] {len(dados)} leituras de telemetria carregadas de '{caminho_arquivo}'.")
        return dados
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho_arquivo}' não encontrado no diretório atual.")
        return []

# Aplica a fórmula matemática central do modelo de rateio híbrido para uma unidade:
def calcular_fatura_unidade(kwh_total, tarifa_kwh, taxa_manutencao_unidade):
    custo_energia = kwh_total * tarifa_kwh
    valor_total = custo_energia + taxa_manutencao_unidade

    return {
        "custo_energia": round(custo_energia, 2),
        "taxa_manutencao": round(taxa_manutencao_unidade, 2),
        "valor_total": round(valor_total, 2)
    }

# Processa todas as leituras de telemetria, consolida o consumo por morador e gera o extrato:
def processar_rateio_condominio(sessoes_telemetria, cadastro_unidades, tarifa_kwh, custo_fixo_manutencao_total):
    energia_por_sessao = {} # Guarda a maior energia acumulada (final da recarga) de cada sessão.
    rfid_por_sessao = {}    # Vincula o ID da sessão à Tag RFID do morador.

    # PASSO 1 - Agrupar os pacotes de telemetria por sessão de recarga:
    for leitura in sessoes_telemetria:
        dados_sessao = leitura.get("sessao", {})
        session_id = dados_sessao.get("session_id")
        tag_rfid = dados_sessao.get("tag_rfid")
        kwh = float(dados_sessao.get("energia_acumulada_kwh", 0.0))

        if session_id:
            rfid_por_sessao[session_id] = tag_rfid

            # Caso Excepcional 1 (Sessões Interrompidas):
            # Mantém sempre o maior valor de kWh registrado na sessão. Se a sessão foi interrompida,
            # o último valor capturado representará exatamente a energia entregue até o encerramento.
            if session_id not in energia_por_sessao or kwh > energia_por_sessao[session_id]:
                energia_por_sessao[session_id] = kwh

    # PASSO 2 - Agrupar o consumo total de kWh e contar a quantidade de sessões por Tag RFID/Unidade:
    consumo_por_unidade = {unidade: 0.0 for unidade in cadastro_unidades.keys()}
    sessoes_contabilizadas = {unidade: 0 for unidade in cadastro_unidades.keys()}

    for session_id, kwh_final in energia_por_sessao.items():
        tag_rfid = rfid_por_sessao.get(session_id)
        if tag_rfid in consumo_por_unidade:
            consumo_por_unidade[tag_rfid] += kwh_final
            sessoes_contabilizadas[tag_rfid] += 1

    # PASSO 3 - Identificar as unidades ativas, com pelo menos uma recarga:
    unidades_ativas = [tag for tag, sessoes in sessoes_contabilizadas.items() if sessoes > 0]
    total_unidades_ativas = len(unidades_ativas)

    # Caso Excepcional 2 (Isenção de Moradores sem Recargas):
    taxa_manutencao_por_unidade_ativa = (
        custo_fixo_manutencao_total / total_unidades_ativas
        if total_unidades_ativas > 0
        else 0.0
    )

    # PASSO 4 - Gerar os extratos financeiros individualizados:
    relatorio_faturas = {}

    for tag_rfid, dados_usuario in cadastro_unidades.items():
        kwh_acumulado = consumo_por_unidade.get(tag_rfid, 0.0)
        qtd_sessoes = sessoes_contabilizadas.get(tag_rfid, 0)

        # Se o morador realizou recargas no mês, aplica a taxa proporcional. Caso contrário, a taxa é zero:
        taxa_aplicada = taxa_manutencao_por_unidade_ativa if qtd_sessoes > 0 else 0.0

        # Calcula os valores monetários finais da fatura:
        fatura = calcular_fatura_unidade(kwh_acumulado, tarifa_kwh, taxa_aplicada)

        # Caso Excepcional 3 (Múltiplos Veículos por Unidade):
        # Consolida todos os veículos registrados sob o mesmo morador/apartamento na fatura.
        relatorio_faturas[tag_rfid] = {
            "titular": dados_usuario.get("nome"),
            "apartamento": dados_usuario.get("apartamento"),
            "veiculos_cadastrados": dados_usuario.get("veiculos", []),
            "total_sessoes_realizadas": qtd_sessoes,
            "consumo_kwh_total": round(kwh_acumulado, 2),
            "tarifa_aplicada_kwh": tarifa_kwh,
            "custo_energia_bruto": fatura["custo_energia"],
            "taxa_manutencao_rateada": fatura["taxa_manutencao"],
            "valor_total_fatura": fatura["valor_total"]
        }

    return relatorio_faturas

# Exibe no terminal o extrato de cobrança individual:
def exibir_extrato_unidade(fatura_unidade, tag_rfid):
    print("=" * 60)
    print(f"  EXTRATO DE COBRANÇA - EV CHARGEOPS ({fatura_unidade['apartamento']})")
    print("=" * 60)
    print(f"Titular: {fatura_unidade['titular']}")
    print(f"Tag RFID: {tag_rfid}")
    print(
        f"Veículo(s) registrado(s): {', '.join(fatura_unidade['veiculos_cadastrados']) if fatura_unidade['veiculos_cadastrados'] else 'Nenhum'}")
    print(f"Sessões de recarga no ciclo: {fatura_unidade['total_sessoes_realizadas']}")
    print("-" * 60)
    print(f"Consumo Total de Energia: {fatura_unidade['consumo_kwh_total']} kWh")
    print(f"Tarifa Vigente por kWh:   R$ {fatura_unidade['tarifa_aplicada_kwh']:.2f}")
    print(f"Custo de Energia (kWh):   R$ {fatura_unidade['custo_energia_bruto']:.2f}")
    print(f"Taxa de Manutenção Redes: R$ {fatura_unidade['taxa_manutencao_rateada']:.2f}")
    print("-" * 60)
    print(f"VALOR TOTAL A PAGAR:      R$ {fatura_unidade['valor_total_fatura']:.2f}")
    print("=" * 60)