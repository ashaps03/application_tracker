from db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from flask_login import UserMixin


class UserJobData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

class User(UserMixin, db.Model):
    id: Mapped[int]= mapped_column(primary_key=True)
    name: Mapped[str]= mapped_column(String(100), nullable=False)
    email: Mapped[str]= mapped_column(String(250), nullable= False)
    password: Mapped[str]= mapped_column(nullable=False)