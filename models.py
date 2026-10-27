"""
Database models for MealMuse.

These classes map directly onto the tables we designed in the
database design section of the SRS document (User, Ingredient,
Inventory, Budget, PriceList, Meal, MealIngredient, Recipe,
MealHistory).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    dietary_goal = db.Column(db.String(50))  # e.g. "fitness", "weight loss", "general health"


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    unit = db.Column(db.String(20))  # e.g. "kg", "piece", "litre"


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    quantity = db.Column(db.Float, default=0)

    ingredient = db.relationship("Ingredient")


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20), default="weekly")  # "weekly" or "monthly"


class PriceList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100))  # which market/location the price is from


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steps = db.Column(db.Text)
    prep_time = db.Column(db.Integer)  # minutes
    difficulty = db.Column(db.String(20))  # "easy", "medium", "hard"


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    meal_of_day = db.Column(db.String(20))  # "breakfast", "lunch", "supper"
    estimated_cost = db.Column(db.Float, default=0)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))

    recipe = db.relationship("Recipe")


class MealIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meal.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    quantity = db.Column(db.Float, default=0)

    ingredient = db.relationship("Ingredient")


class MealHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey("meal.id"), nullable=False)
    date = db.Column(db.Date)
    status = db.Column(db.String(20))  # "suggested", "cooked", "skipped"
