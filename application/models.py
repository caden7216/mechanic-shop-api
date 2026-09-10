# Database models for the mechanic shop.

from datetime import date
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Table, Column, String, Float, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Junction table for the many-to-many between service tickets and mechanics.
# Both columns make up the primary key, so the same mechanic cannot be put on
# the same ticket twice.
service_mechanic = Table(
    "service_mechanic",
    Base.metadata,
    Column("ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
    Column("mechanic_id", ForeignKey("mechanics.id"), primary_key=True),
)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # one customer can have many service tickets
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        back_populates="customer"
    )


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    # a mechanic can work many tickets, through the junction table
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=service_mechanic, back_populates="mechanics"
    )


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(String(300), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    # the customer who owns the car
    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")

    # the mechanics assigned to this ticket
    mechanics: Mapped[List["Mechanic"]] = relationship(
        secondary=service_mechanic, back_populates="service_tickets"
    )
