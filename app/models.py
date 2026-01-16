from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    to_do_list = relationship("ToDoList", back_populates="user", uselist=False)

    def __init__(self, id, email, username, password):
        super().__init__()
        self.id = id
        self.email = email
        self.username = username
        self.password = password


class ToDoList(db.Model):
    __tablename__ = "to_do_lists"
    id: Mapped[int] = mapped_column(primary_key=True)
    tasks = relationship("Task", back_populates="to_do_list")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="to_do_list", primaryjoin="User.id == ToDoList.user_id")

    def __init__(self, user):
        super().__init__()
        self.user = user


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str] = mapped_column(nullable=False)
    to_do_list_id: Mapped[int] = mapped_column(ForeignKey("to_do_lists.id"))
    to_do_list = relationship("ToDoList", back_populates="tasks", primaryjoin="ToDoList.id == Task.to_do_list_id")

    def __init__(self, task, to_do_list):
        super().__init__()
        self.task = task
        self.to_do_list = to_do_list
