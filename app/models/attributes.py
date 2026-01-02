"""Attribute models (Emotion, Texture, Shape)."""

from dataclasses import dataclass
from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


@dataclass
class Emotion(db.Model):
    """Emotion attribute for dishes."""

    __tablename__ = "emotion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


@dataclass
class Texture(db.Model):
    """Texture attribute for dishes."""

    __tablename__ = "texture"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


@dataclass
class Shape(db.Model):
    """Shape attribute for dishes."""

    __tablename__ = "shape"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


# Association tables for many-to-many relationships
emotion_dish = db.Table(
    "emotion_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("emotion.id")),
)

texture_dish = db.Table(
    "texture_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("texture.id")),
)

shape_dish = db.Table(
    "shape_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("shape.id")),
)
