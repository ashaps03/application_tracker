from db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class UserJobData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
