"""Menu and Dish models."""

from __future__ import annotations
from dataclasses import dataclass
import typing as tp
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .attributes import Emotion, Texture, Shape, emotion_dish, texture_dish, shape_dish

if tp.TYPE_CHECKING:
    from .user import User


@dataclass
class Menu(db.Model):
    """Restaurant menu model."""

    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    owner_id: Mapped[tp.Optional[int]] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    owner: Mapped[tp.Optional["User"]] = relationship(back_populates="menus")
    dishes: Mapped[tp.List["Dish"]] = relationship(cascade="all, delete-orphan")


@dataclass
class Dish(db.Model):
    """Dish model with sensory attributes."""

    __tablename__ = "dish"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    section: Mapped[str] = mapped_column(String)

    # Emotions
    emotions: Mapped[tp.List[Emotion]] = relationship(secondary=emotion_dish)

    # Basic tastes
    bitter: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    salty: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    sour: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    sweet: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    umami: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)

    # Other tastes
    fat: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    piquant: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)

    # Textures
    textures: Mapped[tp.List[Texture]] = relationship(secondary=texture_dish)

    # Colors
    color1: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)
    color2: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)
    color3: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)

    # Shapes
    shapes: Mapped[tp.List[Shape]] = relationship(secondary=shape_dish)


class DishBuilder:
    """Builder pattern for creating Dish objects."""

    def __init__(self):
        self._dish = Dish()

    def with_basic_info(
        self, name: str, description: str, section: str
    ) -> "DishBuilder":
        self._dish.name = name
        self._dish.description = description
        self._dish.section = section
        return self

    def with_basic_tastes(
        self,
        sour: int = None,
        sweet: int = None,
        salty: int = None,
        bitter: int = None,
        umami: int = None,
    ) -> "DishBuilder":
        self._dish.sour = sour
        self._dish.sweet = sweet
        self._dish.salty = salty
        self._dish.bitter = bitter
        self._dish.umami = umami
        return self

    def with_other_tastes(
        self, fat: int = None, piquant: int = None, temperature: int = None
    ) -> "DishBuilder":
        self._dish.fat = fat
        self._dish.piquant = piquant
        self._dish.temperature = temperature
        return self

    def with_colors(self, colors: tp.List[str]) -> "DishBuilder":
        for i, color in enumerate(colors[:3]):
            setattr(self._dish, f"color{i+1}", color)
        return self

    def with_emotions(self, emotions: tp.List[Emotion]) -> "DishBuilder":
        self._dish.emotions = emotions
        return self

    def with_textures(self, textures: tp.List[Texture]) -> "DishBuilder":
        self._dish.textures = textures
        return self

    def with_shapes(self, shapes: tp.List[Shape]) -> "DishBuilder":
        self._dish.shapes = shapes
        return self

    def build(self) -> Dish:
        return self._dish
