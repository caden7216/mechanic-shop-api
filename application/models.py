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


# Junction table for the many-to-many between service tickets and inventory
# parts. One ticket can need many parts, and the same part gets used on many
# tickets.
ticket_inventory = Table(
    "ticket_inventory",
    Base.metadata,
    Column("ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
    Column("inventory_id", ForeignKey("inventory.id"), primary_key=True),
)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # one customer can have many service tickets.
    # cascade means deleting a customer also deletes their tickets, so we do not
    # leave tickets behind pointing at a customer that is gone.
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        back_populates="customer", cascade="all, delete"
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


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # the same part can be used on many tickets
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=ticket_inventory, back_populates="parts"
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

    # the parts used on this ticket
    parts: Mapped[List["Inventory"]] = relationship(
        secondary=ticket_inventory, back_populates="service_tickets"
    )
