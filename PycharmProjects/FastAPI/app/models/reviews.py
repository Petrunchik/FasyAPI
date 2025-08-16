from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship, foreign
from datetime import datetime

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True) # Числовое поле, являющееся первичным ключом.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Поле связи с таблицей пользователей.
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True) # Поле связи с таблицей товара.
    comment = Column(Text, nullable=True) # Текстовое поле отзыва о товаре, может быть пустым.
    comment_date = Column(Date, default=datetime.now()) # Поле даты отзыва, по умолчанию заполняется автоматически.
    grade = Column(Float, default=0.0) # Числовое поле оценки товара(рейтинг).
    is_active = Column(Boolean, default=True) # Булево поле, по умолчанию True.
