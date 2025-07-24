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
    Column("uploader", String),
    Column("uploaded_at", DateTime(timezone=True), server_default=func.now()),
    Column("schedule_date", Date, nullable=True),
    Column("delivered", Boolean, default=False),
)

summaries = Table(
    "summaries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("newsletter_id", Integer, ForeignKey("newsletters.id"), unique=True),
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
