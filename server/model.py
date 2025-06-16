from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from sqlalchemy import ForeignKey
from flask_login import UserMixin


class UserJobData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    firebase_uid = db.Column(db.String(128), nullable=False)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="jobs")

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    # Optional: if you want easy access to their jobs
    jobs = relationship("UserJobData", back_populates="user")