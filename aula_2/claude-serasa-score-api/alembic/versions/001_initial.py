"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabela de auditoria de consultas
    op.create_table(
        "consultas_auditoria",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("cpf_masked", sa.String(20), nullable=False),
        sa.Column(
            "cpf_hash", sa.String(64), nullable=False,
            comment="SHA-256 do CPF — para busca sem expor o dado"
        ),
        sa.Column("usuario_id", sa.String(100), nullable=False),
        sa.Column("realizada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cache_hit", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Float, nullable=False, server_default="0"),
        sa.Column("detalhes", sa.Text, nullable=True),
    )
    op.create_index("ix_consultas_cpf_hash_data", "consultas_auditoria", ["cpf_hash", "realizada_em"])
    op.create_index("ix_consultas_cpf_masked", "consultas_auditoria", ["cpf_masked"])
    op.create_index("ix_consultas_usuario_data", "consultas_auditoria", ["usuario_id", "realizada_em"])

    # Tabela de API keys
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("key_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("usuario_id", sa.String(100), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ultimo_uso_em", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_api_keys_usuario_id", "api_keys", ["usuario_id"])


def downgrade() -> None:
    op.drop_table("api_keys")
    op.drop_table("consultas_auditoria")
