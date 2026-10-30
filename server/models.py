from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import (String, Integer, Numeric, Date, Time, TIMESTAMP,
                        Text, ForeignKey, func)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="client")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now())

    orders: Mapped[List["Order"]] = relationship(
        back_populates="client", cascade="all, delete-orphan")
    cars: Mapped[List["Car"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    order_stages: Mapped[List["OrderStage"]] = relationship(
        back_populates="washer")
    reviews: Mapped[List["Review"]] = relationship(
        back_populates="author")


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"))
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    plate: Mapped[Optional[str]] = mapped_column(String(20))

    user: Mapped["User"] = relationship(back_populates="cars")
    orders: Mapped[List["Order"]] = relationship(back_populates="car")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    items: Mapped[List["OrderServiceItem"]] = relationship(
        back_populates="service")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    car_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cars.id"))
    date: Mapped[Optional[date]] = mapped_column(Date)
    time: Mapped[Optional[time]] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(50), default="draft")

    client: Mapped["User"] = relationship(back_populates="orders")
    car: Mapped[Optional["Car"]] = relationship(back_populates="orders")
    items: Mapped[List["OrderServiceItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan")
    stages: Mapped[List["OrderStage"]] = relationship(
        back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="order", cascade="all, delete-orphan")
    review: Mapped[Optional["Review"]] = relationship(
        back_populates="order", uselist=False,
        cascade="all, delete-orphan")


class OrderServiceItem(Base):
    __tablename__ = "order_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    quantity: Mapped[int] = mapped_column(default=1)
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    service: Mapped["Service"] = relationship(back_populates="items")


class OrderStage(Base):
    __tablename__ = "order_stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"))
    washer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    stage: Mapped[Optional[str]] = mapped_column(String(50))
    date: Mapped[datetime] = mapped_column(TIMESTAMP,
                                            server_default=func.now())

    order: Mapped["Order"] = relationship(back_populates="stages")
    washer: Mapped[Optional["User"]] = relationship(
        back_populates="order_stages")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    date: Mapped[datetime] = mapped_column(TIMESTAMP,
                                            server_default=func.now())

    order: Mapped["Order"] = relationship(back_populates="payments")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"))
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    text: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["Order"] = relationship(back_populates="review")
    author: Mapped[Optional["User"]] = relationship(
        back_populates="reviews")