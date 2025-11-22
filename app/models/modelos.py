from sqlalchemy import (
    Column,
    Integer,
    Enum,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    true,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.config import Base
from enum import Enum as PyEnum


class AppointmentState(PyEnum):
    ASIGNADA = "ASIGNADA"
    COMPLETADA = "COMPLETADA"
    PENDIENTE = "PENDIENTE"
    CANCELADA = "CANCELADA"


class Client(Base):
    __tablename__ = "Client"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String(100), nullable=False)
    fullSurname = Column(String(100), nullable=False)
    identified = Column(String(50), unique=True, nullable=False)
    clientState = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, onupdate=func.now(), server_default=func.now(), nullable=True
    )

    clientAppointment = relationship("AppointmentScheduling", back_populates="author")
    clientContact = relationship(
        "ClientContact", back_populates="author", cascade="all, delete"
    )


class AppointmentScheduling(Base):
    __tablename__ = "AppointmentScheduling"

    id = Column(Integer, primary_key=True, index=True)
    appointmentDate = Column(DateTime, nullable=False)
    ubicacion = Column(String(50), nullable=False)
    appointmentState = Column(
        Enum(AppointmentState, name="AppointmentState"),
        nullable=False,
        default=AppointmentState.ASIGNADA.value,  # ⚡ usar `.value` !!!
    )
    details = Column(Text)
    clientId = Column(Integer, ForeignKey("Client.id"), nullable=False)
    employedId = Column(Integer, nullable=True)

    author = relationship("Client", back_populates="clientAppointment")


class ClientContact(Base):
    __tablename__ = "ClientContact"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    address = Column(String(50))
    createAt = Column(DateTime, server_default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, onupdate=func.now(), server_default=func.now(), nullable=False
    )
    clientId = Column(Integer, ForeignKey("Client.id"), nullable=False)

    author = relationship("Client", back_populates="clientContact")
