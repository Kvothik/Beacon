from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260311_0001"
down_revision = None
branch_labels = None
depends_on = None

PACKET_STATUS_VALUES = ("draft", "generating_pdf", "ready")
SECTION_KEY_VALUES = (
    "photos",
    "support_letters",
    "reflection_letter",
    "certificates_and_education",
    "future_employment",
    "parole_plan",
    "court_and_case_documents",
    "other_miscellaneous",
)
DOCUMENT_SOURCE_VALUES = ("scanner", "upload")
UPLOAD_STATUS_VALUES = ("pending", "uploaded", "failed")
PLATFORM_VALUES = ("ios", "android")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "offenders",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("sid", sa.Text(), nullable=False),
        sa.Column("tdcj_number", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("race", sa.Text(), nullable=True),
        sa.Column("gender", sa.Text(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("current_facility", sa.Text(), nullable=True),
        sa.Column("projected_release_date", sa.Text(), nullable=True),
        sa.Column("parole_eligibility_date", sa.Text(), nullable=True),
        sa.Column("maximum_sentence_date", sa.Text(), nullable=True),
        sa.Column("visitation_eligible", sa.Boolean(), nullable=True),
        sa.Column("visitation_eligible_raw", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False, server_default=sa.text("'Texas Department of Criminal Justice'")),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("sid", "retrieved_at", name="uq_offenders_sid_retrieved_at"),
    )
    op.create_index("ix_offenders_sid", "offenders", ["sid"], unique=False)

    op.create_table(
        "parole_board_offices",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("office_code", sa.Text(), nullable=False, unique=True),
        sa.Column("office_name", sa.Text(), nullable=False),
        sa.Column("address_line_1", sa.Text(), nullable=False),
        sa.Column("address_line_2", sa.Text(), nullable=True),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("postal_code", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "parole_board_unit_mappings",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("unit_name", sa.Text(), nullable=False, unique=True),
        sa.Column("office_id", sa.Uuid(), sa.ForeignKey("parole_board_offices.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "packets",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("offender_id", sa.Uuid(), sa.ForeignKey("offenders.id"), nullable=False),
        sa.Column("parole_board_office_id", sa.Uuid(), sa.ForeignKey("parole_board_offices.id"), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("sender_name", sa.Text(), nullable=True),
        sa.Column("sender_phone", sa.Text(), nullable=True),
        sa.Column("sender_email", sa.Text(), nullable=True),
        sa.Column("sender_relationship", sa.Text(), nullable=True),
        sa.Column("cover_letter_text", sa.Text(), nullable=True),
        sa.Column("final_pdf_storage_key", sa.Text(), nullable=True),
        sa.Column("final_pdf_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(f"status IN {PACKET_STATUS_VALUES}", name="ck_packets_status_allowed"),
    )

    op.create_table(
        "packet_sections",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("packet_id", sa.Uuid(), sa.ForeignKey("packets.id"), nullable=False),
        sa.Column("section_key", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("notes_text", sa.Text(), nullable=True),
        sa.Column("is_populated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("packet_id", "section_key", name="uq_packet_sections_packet_section_key"),
        sa.CheckConstraint(f"section_key IN {SECTION_KEY_VALUES}", name="ck_packet_sections_section_key_allowed"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("packet_id", sa.Uuid(), sa.ForeignKey("packets.id"), nullable=False),
        sa.Column("packet_section_id", sa.Uuid(), sa.ForeignKey("packet_sections.id"), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=True),
        sa.Column("upload_status", sa.Text(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(f"source IN {DOCUMENT_SOURCE_VALUES}", name="ck_documents_source_allowed"),
        sa.CheckConstraint(f"upload_status IN {UPLOAD_STATUS_VALUES}", name="ck_documents_upload_status_allowed"),
    )

    op.create_table(
        "notification_subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column("device_token", sa.Text(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(f"platform IN {PLATFORM_VALUES}", name="ck_notification_subscriptions_platform_allowed"),
    )


def downgrade() -> None:
    op.drop_table("notification_subscriptions")
    op.drop_table("documents")
    op.drop_table("packet_sections")
    op.drop_table("packets")
    op.drop_table("parole_board_unit_mappings")
    op.drop_table("parole_board_offices")
    op.drop_index("ix_offenders_sid", table_name="offenders")
    op.drop_table("offenders")
    op.drop_table("users")
