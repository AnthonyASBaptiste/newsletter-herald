from sqlalchemy import (
    Table, Column, Integer, String, Boolean, Date, DateTime,
    Float, Text, ForeignKey
)
from sqlalchemy.sql import func
from db.setup import metadata

newsletters = Table(
    "newsletters",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String),
    Column("drive_file_id", String, nullable=True),
    Column("drive_web_view_link", String, nullable=True),
    Column("thumbnail_drive_id", String, nullable=True),
    Column("uploader", String),
    Column("uploaded_at", DateTime(timezone=True), server_default=func.now()),
    Column("schedule_date", Date, nullable=True),
    Column("tags", Text, nullable=True),
    Column("delivered", Boolean, default=False),
    Column("status", String, default="draft"),
    Column("target_sunday", Date, nullable=True),
)

summaries = Table(
    "summaries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("newsletter_id", Integer, ForeignKey("newsletters.id"), unique=True),
    Column("title", String, nullable=True),
    Column("summary", Text),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

model_usage = Table(
    "model_usage",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("summary_id", Integer, ForeignKey("summaries.id")),
    Column("model", String),
    Column("tokens", Integer),
    Column("cost_usd_estimate", Float),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

subscribers = Table(
    "subscribers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("phone", String, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

delivery_logs = Table(
    "delivery_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("newsletter_id", Integer, ForeignKey("newsletters.id")),
    Column("recipient", String, nullable=False),
    Column("status", String, nullable=False),
    Column("error_message", Text, nullable=True),
    Column("timestamp", DateTime(timezone=True), server_default=func.now()),
)

agent_notifications = Table(
    "agent_notifications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_type", String, nullable=False),
    Column("payload", Text, nullable=False), # JSON payload
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

upload_logs = Table(
    "upload_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String, nullable=False),
    Column("uploader", String, nullable=False),
    Column("status", String, nullable=False), # "success", "failed"
    Column("error_message", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

