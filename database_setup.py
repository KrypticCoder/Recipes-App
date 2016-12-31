from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import *

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(50000))
    ingredients = Column(String(50000))
    instructions = Column(String(50000))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
        }


# class Ingredient(Base):
#     __tablename__ = 'ingredient'

#     id = Column(Integer, primary_key=True)
#     content = Column(String(5000))
#     recipe_id = Column(Integer, ForeignKey('recipe.id'))
#     recipe = relationship(Recipe)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     user = relationship(User)

#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'content': self.content,
#             'recipe': self.recipe,
#             'recipe_id': self.description,
#         }

engine = create_engine('sqlite:///recipes.db')


Base.metadata.create_all(engine)
