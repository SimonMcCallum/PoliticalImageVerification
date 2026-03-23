"""Geographic aggregation model for verification statistics.

Privacy-first: only aggregate counts are stored, never individual IPs.
"""

import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VerificationGeoStat(Base):
    __tablename__ = "verification_geo_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    verification_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "date", "region", "country", name="uq_geo_stat_date_region_country"
        ),
    )
