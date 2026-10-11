
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# EV ChargeOps - Banco de Dados
# Banco relacional SQLite
# ============================================================

DB_PATH = Path(__file__).resolve().parent / "ev_chargeops.db"


def agora_iso():
    """Retorna a data/hora atual em formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def converter_float(valor):
    """Converte um valor para float, se possível."""
    if valor is None or valor == "":
        return None

    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.criar_tabelas()

    def conectar(self):
        """Abre uma conexão com as chaves estrangeiras ativadas."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def criar_tabelas(self):
        """Cria o esquema inicial caso ele ainda não exista."""
        with self.conectar() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS apartamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT NOT NULL UNIQUE,
                    criado_em TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE,
                    apartamento_id INTEGER NOT NULL,
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY (apartamento_id)
                        REFERENCES apartamentos(id)
                );

                CREATE TABLE IF NOT EXISTS identificadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_rfid TEXT NOT NULL UNIQUE,
                    usuario_id INTEGER NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY (usuario_id)
                        REFERENCES usuarios(id)
                );

                CREATE TABLE IF NOT EXISTS sessoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sessao_externa_id TEXT NOT NULL,
                    carregador_sn TEXT,
                    identificador_id INTEGER,
                    rfid_recebido TEXT,
                    inicio TEXT,
                    fim TEXT,
                    status TEXT,
                    kwh_total REAL NOT NULL DEFAULT 0,
                    origem TEXT NOT NULL DEFAULT 'simulado',
                    payload_json TEXT,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL,
                    UNIQUE (carregador_sn, sessao_externa_id),
                    FOREIGN KEY (identificador_id)
                        REFERENCES identificadores(id)
                );

                CREATE TABLE IF NOT EXISTS leituras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sessao_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    tensao_v REAL,
                    corrente_a REAL,
                    potencia_kw REAL,
                    energia_kwh REAL,
                    status TEXT,
                    payload_json TEXT,
                    criado_em TEXT NOT NULL,
                    UNIQUE (sessao_id, timestamp),
                    FOREIGN KEY (sessao_id)
                        REFERENCES sessoes(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS faturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apartamento_id INTEGER NOT NULL,
                    mes_referencia TEXT NOT NULL,
                    kwh_total REAL NOT NULL DEFAULT 0,
                    tarifa_kwh REAL NOT NULL,
                    custo_energia REAL NOT NULL,
                    taxa_manutencao REAL NOT NULL DEFAULT 0,
                    valor_total REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'calculada',
                    criado_em TEXT NOT NULL,
                    UNIQUE (apartamento_id, mes_referencia),
                    FOREIGN KEY (apartamento_id)
                        REFERENCES apartamentos(id)
                );

                CREATE TABLE IF NOT EXISTS auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    entidade TEXT NOT NULL,
                    entidade_id TEXT,
                    detalhes TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_usuarios_apartamento
                    ON usuarios(apartamento_id);

                CREATE INDEX IF NOT EXISTS idx_identificadores_usuario
                    ON identificadores(usuario_id);

                CREATE INDEX IF NOT EXISTS idx_sessoes_inicio
                    ON sessoes(inicio);

                CREATE INDEX IF NOT EXISTS idx_leituras_sessao_timestamp
                    ON leituras(sessao_id, timestamp);

                CREATE INDEX IF NOT EXISTS idx_faturas_mes
                    ON faturas(mes_referencia);
            """)

    # --------------------------------------------------------
    # AUDITORIA
    # --------------------------------------------------------

    def registrar_evento(
        self, acao, entidade, entidade_id=None, detalhes=None
    ):
        """Registra uma operação relevante no histórico de auditoria."""
        if not isinstance(detalhes, str) and detalhes is not None:
            detalhes = json.dumps(
                detalhes, ensure_ascii=False, default=str
            )

        with self.conectar() as conn:
            conn.execute("""
                INSERT INTO auditoria (
                    data_hora, acao, entidade, entidade_id, detalhes
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                agora_iso(), acao, entidade,
                str(entidade_id) if entidade_id is not None else None,
                detalhes
            ))

    
    def listar_eventos_auditoria(self, limite=100):
        """Lista os eventos mais recentes para consulta do gestor."""
        with self.conectar() as conn:
            rows = conn.execute("""
                SELECT
                    id,
                    data_hora,
                    acao,
                    entidade,
                    entidade_id,
                    detalhes
                FROM auditoria
                ORDER BY id DESC
                LIMIT ?
            """, (limite,)).fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------------
    # CADASTROS
    # --------------------------------------------------------

    def cadastrar_apartamento(self, numero):
        numero = str(numero).strip()

        with self.conectar() as conn:
            conn.execute("""
                INSERT INTO apartamentos (numero, criado_em)
                VALUES (?, ?)
                ON CONFLICT(numero) DO NOTHING
            """, (numero, agora_iso()))

            row = conn.execute(
                "SELECT id FROM apartamentos WHERE numero = ?",
                (numero,)
            ).fetchone()

            apartamento_id = row["id"]

        self.registrar_evento(
            "cadastro_ou_consulta", "apartamentos",
            apartamento_id, {"numero": numero}
        )
        return apartamento_id

    def cadastrar_usuario(self, nome, apartamento_numero, email=None):
        """Cadastra um morador e o vincula a um apartamento."""
        apartamento_id = self.cadastrar_apartamento(apartamento_numero)

        with self.conectar() as conn:
            if email:
                conn.execute("""
                    INSERT INTO usuarios
                        (nome, email, apartamento_id, criado_em)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        nome = excluded.nome,
                        apartamento_id = excluded.apartamento_id
                """, (nome, email, apartamento_id, agora_iso()))

                row = conn.execute(
                    "SELECT id FROM usuarios WHERE email = ?",
                    (email,)
                ).fetchone()
            else:
                conn.execute("""
                    INSERT INTO usuarios
                        (nome, email, apartamento_id, criado_em)
                    VALUES (?, NULL, ?, ?)
                """, (nome, apartamento_id, agora_iso()))

                row = conn.execute(
                    "SELECT last_insert_rowid() AS id"
                ).fetchone()

            usuario_id = row["id"]

        self.registrar_evento(
            "cadastro_ou_atualizacao", "usuarios",
            usuario_id,
            {"nome": nome, "apartamento": str(apartamento_numero)}
        )
        return usuario_id

    def cadastrar_identificador(self, codigo_rfid, usuario_id, ativo=True):
        """Associa um RFID ao cadastro de um usuário."""
        codigo_rfid = str(codigo_rfid).strip()

        with self.conectar() as conn:
            conn.execute("""
                INSERT INTO identificadores
                    (codigo_rfid, usuario_id, ativo, criado_em)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(codigo_rfid) DO UPDATE SET
                    usuario_id = excluded.usuario_id,
                    ativo = excluded.ativo
            """, (
                codigo_rfid, usuario_id, int(ativo), agora_iso()
            ))

            row = conn.execute(
                "SELECT id FROM identificadores WHERE codigo_rfid = ?",
                (codigo_rfid,)
            ).fetchone()

            identificador_id = row["id"]

        self.registrar_evento(
            "cadastro_ou_atualizacao", "identificadores",
            identificador_id,
            {"rfid": codigo_rfid, "usuario_id": usuario_id}
        )
        return identificador_id

    def listar_usuarios(self):
        """Lista os moradores e seus apartamentos."""
        with self.conectar() as conn:
            rows = conn.execute("""
                SELECT
                    u.id,
                    u.nome,
                    u.email,
                    a.numero AS apartamento
                FROM usuarios u
                JOIN apartamentos a ON a.id = u.apartamento_id
                ORDER BY a.numero, u.nome
            """).fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------------
    # INGESTÃO E PERSISTÊNCIA DE TELEMETRIA
    # --------------------------------------------------------

    @staticmethod
    def primeiro_valor(dados, *chaves):
        """Retorna o primeiro campo existente e não vazio."""
        for chave in chaves:
            valor = dados.get(chave)
            if valor is not None and valor != "":
                return valor
        return None

    
    def salvar_telemetria(self, leituras, origem="simulado"):
        """
        Importa leituras no formato JSON do EV ChargeOps.

        Aceita campos aninhados em:
        - leitura["sessao"]
        - leitura["telemetria"]

        Retorna a quantidade de leituras novas inseridas.
        """
        quantidade_inserida = 0

        for leitura in leituras:
            sessao_dados = leitura.get("sessao") or {}
            telemetria = leitura.get("telemetria") or {}

            # Dados gerais
            timestamp = leitura.get("timestamp") or agora_iso()
            carregador_sn = (
                leitura.get("charger_id")
                or leitura.get("charger_sn")
                or ""
            )
            status = leitura.get("status")

            # Dados que ficam dentro de "sessao"
            sessao_externa_id = (
                sessao_dados.get("session_id")
                or leitura.get("session_id")
            )

            rfid = (
                sessao_dados.get("tag_rfid")
                or leitura.get("tag_rfid")
                or leitura.get("rfid")
            )

            energia = converter_float(
                sessao_dados.get("energia_acumulada_kwh")
                or leitura.get("energia_acumulada_kwh")
            )

            if energia is None:
                energia = converter_float(
                    sessao_dados.get("energia_kwh")
                    if sessao_dados.get("energia_kwh") is not None
                    else leitura.get("energia_kwh")
                )

            if not sessao_externa_id:
                raise ValueError(
                    f"Leitura sem session_id. "
                    f"Timestamp: {timestamp}"
                )

            sessao_externa_id = str(sessao_externa_id)

            # Dados que ficam dentro de "telemetria"
            tensao = converter_float(
                telemetria.get("tensao_v")
            )
            corrente = converter_float(
                telemetria.get("corrente_a")
            )
            potencia = converter_float(
                telemetria.get("potencia_kw")
            )

            payload_json = json.dumps(
                leitura,
                ensure_ascii=False,
                default=str
            )

            with self.conectar() as conn:
                identificador = None

                if rfid:
                    identificador = conn.execute("""
                        SELECT id
                        FROM identificadores
                        WHERE codigo_rfid = ?
                          AND ativo = 1
                    """, (str(rfid),)).fetchone()

                identificador_id = (
                    identificador["id"]
                    if identificador else None
                )

                # Cria a sessão ou atualiza a sessão existente.
                conn.execute("""
                    INSERT INTO sessoes (
                        sessao_externa_id,
                        carregador_sn,
                        identificador_id,
                        rfid_recebido,
                        inicio,
                        status,
                        kwh_total,
                        origem,
                        payload_json,
                        criado_em,
                        atualizado_em
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(carregador_sn, sessao_externa_id)
                    DO UPDATE SET
                        identificador_id = COALESCE(
                            excluded.identificador_id,
                            sessoes.identificador_id
                        ),
                        rfid_recebido = COALESCE(
                            excluded.rfid_recebido,
                            sessoes.rfid_recebido
                        ),
                        status = COALESCE(
                            excluded.status,
                            sessoes.status
                        ),
                        kwh_total = MAX(
                            sessoes.kwh_total,
                            excluded.kwh_total
                        ),
                        payload_json = excluded.payload_json,
                        atualizado_em = excluded.atualizado_em
                """, (
                    sessao_externa_id,
                    carregador_sn,
                    identificador_id,
                    str(rfid) if rfid else None,
                    timestamp,
                    status,
                    energia if energia is not None else 0.0,
                    origem,
                    payload_json,
                    agora_iso(),
                    agora_iso()
                ))

                sessao = conn.execute("""
                    SELECT id
                    FROM sessoes
                    WHERE carregador_sn = ?
                      AND sessao_externa_id = ?
                """, (
                    carregador_sn,
                    sessao_externa_id
                )).fetchone()

                sessao_id = sessao["id"]

                # Evita duplicar uma leitura com o mesmo
                # timestamp dentro da mesma sessão.
                cursor = conn.execute("""
                    INSERT INTO leituras (
                        sessao_id,
                        timestamp,
                        tensao_v,
                        corrente_a,
                        potencia_kw,
                        energia_kwh,
                        status,
                        payload_json,
                        criado_em
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(sessao_id, timestamp)
                    DO NOTHING
                """, (
                    sessao_id,
                    timestamp,
                    tensao,
                    corrente,
                    potencia,
                    energia,
                    status,
                    payload_json,
                    agora_iso()
                ))

                quantidade_inserida += cursor.rowcount

                # Registra o fim quando a telemetria informa
                # explicitamente um estado terminal.
                estados_finais = {
                    "finished",
                    "completed",
                    "aborted",
                    "interrupted",
                    "fault",
                    "failed"
                }

                if status and str(status).lower() in estados_finais:
                    conn.execute("""
                        UPDATE sessoes
                        SET fim = ?,
                            atualizado_em = ?
                        WHERE id = ?
                    """, (
                        timestamp,
                        agora_iso(),
                        sessao_id
                    ))

        self.registrar_evento(
            "ingestao_telemetria",
            "leituras",
            None,
            {
                "origem": origem,
                "leituras_recebidas": len(leituras),
                "leituras_novas": quantidade_inserida
            }
        )

        return quantidade_inserida


    # --------------------------------------------------------
    # CONSULTAS
    # --------------------------------------------------------

    def listar_sessoes(self):
        """Lista sessões com o nome do usuário, se houver vínculo."""
        with self.conectar() as conn:
            rows = conn.execute("""
                SELECT
                    s.id,
                    s.sessao_externa_id,
                    s.carregador_sn,
                    s.rfid_recebido,
                    u.nome AS usuario,
                    a.numero AS apartamento,
                    s.inicio,
                    s.fim,
                    s.status,
                    s.kwh_total,
                    s.origem
                FROM sessoes s
                LEFT JOIN identificadores i
                    ON i.id = s.identificador_id
                LEFT JOIN usuarios u ON u.id = i.usuario_id
                LEFT JOIN apartamentos a ON a.id = u.apartamento_id
                ORDER BY s.inicio DESC
            """).fetchall()

        return [dict(row) for row in rows]

    def listar_leituras_sessao(self, sessao_id):
        """Retorna o histórico de medições de uma sessão."""
        with self.conectar() as conn:
            rows = conn.execute("""
                SELECT *
                FROM leituras
                WHERE sessao_id = ?
                ORDER BY timestamp
            """, (sessao_id,)).fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------------
    # FATURAS
    # --------------------------------------------------------

    def salvar_fatura(
        self,
        apartamento_numero,
        mes_referencia,
        kwh_total,
        tarifa_kwh,
        custo_energia,
        taxa_manutencao,
        valor_total
    ):
        """Insere ou atualiza a fatura de um apartamento no mês."""
        with self.conectar() as conn:
            apartamento = conn.execute("""
                SELECT id FROM apartamentos WHERE numero = ?
            """, (str(apartamento_numero),)).fetchone()

            if not apartamento:
                raise ValueError(
                    f"Apartamento {apartamento_numero} não cadastrado."
                )

            apartamento_id = apartamento["id"]

            conn.execute("""
                INSERT INTO faturas (
                    apartamento_id, mes_referencia, kwh_total,
                    tarifa_kwh, custo_energia, taxa_manutencao,
                    valor_total, status, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'calculada', ?)
                ON CONFLICT(apartamento_id, mes_referencia)
                DO UPDATE SET
                    kwh_total = excluded.kwh_total,
                    tarifa_kwh = excluded.tarifa_kwh,
                    custo_energia = excluded.custo_energia,
                    taxa_manutencao = excluded.taxa_manutencao,
                    valor_total = excluded.valor_total,
                    status = 'calculada',
                    criado_em = excluded.criado_em
            """, (
                apartamento_id, mes_referencia, kwh_total,
                tarifa_kwh, custo_energia, taxa_manutencao,
                valor_total, agora_iso()
            ))

            row = conn.execute("""
                SELECT id FROM faturas
                WHERE apartamento_id = ? AND mes_referencia = ?
            """, (apartamento_id, mes_referencia)).fetchone()

            fatura_id = row["id"]

        self.registrar_evento(
            "fatura_salva", "faturas", fatura_id,
            {
                "apartamento": str(apartamento_numero),
                "mes": mes_referencia,
                "valor_total": valor_total
            }
        )
        return fatura_id

    def listar_faturas(self, mes_referencia=None):
        """Lista as faturas, opcionalmente filtradas por mês."""
        with self.conectar() as conn:
            if mes_referencia:
                rows = conn.execute("""
                    SELECT f.*, a.numero AS apartamento
                    FROM faturas f
                    JOIN apartamentos a ON a.id = f.apartamento_id
                    WHERE f.mes_referencia = ?
                    ORDER BY a.numero
                """, (mes_referencia,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT f.*, a.numero AS apartamento
                    FROM faturas f
                    JOIN apartamentos a ON a.id = f.apartamento_id
                    ORDER BY f.mes_referencia DESC, a.numero
                """).fetchall()

        return [dict(row) for row in rows]


if __name__ == "__main__":
    db = Database()
    print(f"Banco inicializado em: {db.db_path}")
    print("Tabelas criadas ou verificadas com sucesso.")
