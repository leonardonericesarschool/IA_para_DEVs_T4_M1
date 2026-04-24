"""001_initial_pix_keys

Revision ID: 001
Revises: 
Create Date: 2026-04-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables."""
    # Create enum types
    tipo_chave_enum = postgresql.ENUM("CPF", "CNPJ", "EMAIL", "TELEFONE", name="tipochaveenum")
    tipo_chave_enum.create(op.get_bind(), checkfirst=True)

    status_chave_enum = postgresql.ENUM("CRIADA", "CONFIRMADA", "DELETADA", name="statuschaveenum")
    status_chave_enum.create(op.get_bind(), checkfirst=True)

    # Create pix_keys table
    op.create_table(
        "pix_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo_chave", postgresql.ENUM("CPF", "CNPJ", "EMAIL", "TELEFONE", name="tipochaveenum"), nullable=False),
        sa.Column("valor_chave", sa.String(255), nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("status", postgresql.ENUM("CRIADA", "CONFIRMADA", "DELETADA", name="statuschaveenum"), nullable=False, server_default="CRIADA"),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cliente_id", "tipo_chave", "valor_chave", name="uq_cliente_tipo_valor"),
    )

    # Create indexes
    op.create_index("ix_cliente_id_status", "pix_keys", ["cliente_id", "status"])
    op.create_index("ix_tipo_valor", "pix_keys", ["tipo_chave", "valor_chave"])
    op.create_index("ix_cliente_id", "pix_keys", ["cliente_id"])

    # Create pix_key_audits table
    op.create_table(
        "pix_key_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pix_key_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("acao", sa.String(50), nullable=False),
        sa.Column("resultado", sa.String(20), nullable=False),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["pix_key_id"], ["pix_keys.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes on audit table
    op.create_index("ix_pix_key_id", "pix_key_audits", ["pix_key_id"])
    op.create_index("ix_criado_em", "pix_key_audits", ["criado_em"])


def downgrade() -> None:
    """Drop initial tables."""
    op.drop_index("ix_criado_em", table_name="pix_key_audits")
    op.drop_index("ix_pix_key_id", table_name="pix_key_audits")
    op.drop_table("pix_key_audits")

    op.drop_index("ix_cliente_id", table_name="pix_keys")
    op.drop_index("ix_tipo_valor", table_name="pix_keys")
    op.drop_index("ix_cliente_id_status", table_name="pix_keys")
    op.drop_table("pix_keys")

    # Drop enum types
    sa.Enum("CRIADA", "CONFIRMADA", "DELETADA", name="statuschaveenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum("CPF", "CNPJ", "EMAIL", "TELEFONE", name="tipochaveenum").drop(op.get_bind(), checkfirst=True)
