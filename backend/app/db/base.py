import uuid
from datetime import datetime
from typing import Annotated
from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

utcnow = func.timezone("UTC", func.now())

str_256 = Annotated[str, 256]
str_1024 = Annotated[str, 1024]
text = Annotated[str, Text]
float8 = Annotated[float, Float(53)]
int32 = Annotated[int, Integer]
bool_field = Annotated[bool, Boolean]
json_field = Annotated[dict, JSONB]
timestamp = Annotated[datetime, TIMESTAMP(timezone=True)]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256),
        str_1024: String(1024),
        text: Text,
        float8: Float(53),
        int32: Integer,
        bool_field: Boolean,
        json_field: JSONB,
        timestamp: TIMESTAMP(timezone=True),
    }

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=utcnow, onupdate=utcnow
    )
