"""
Run this once after starting the app for the first time to add some
sample meals so /suggest actually has something to recommend.

    python seed.py
"""

from app import app
from models import db, Ingredient, Meal, MealIngredient, Recipe


def get_or_create_ingredient(name, unit="unit"):
    ingredient = Ingredient.query.filter_by(name=name).first()
    if ingredient is None:
        ingredient = Ingredient(name=name, unit=unit)
        db.session.add(ingredient)
        db.session.commit()
    return ingredient


def add_meal(name, meal_of_day, cost, ingredient_names, steps, prep_time, difficulty):
    recipe = Recipe(steps=steps, prep_time=prep_time, difficulty=difficulty)
    db.session.add(recipe)
    db.session.commit()

    meal = Meal(name=name, meal_of_day=meal_of_day, estimated_cost=cost, recipe_id=recipe.id)
    db.session.add(meal)
    db.session.commit()

    for ingredient_name in ingredient_names:
        ingredient = get_or_create_ingredient(ingredient_name)
        db.session.add(MealIngredient(meal_id=meal.id, ingredient_id=ingredient.id, quantity=1))

    db.session.commit()


with app.app_context():
    db.create_all()

    add_meal(
        name="Plain rice with tomato stew",
        meal_of_day="lunch",
        cost=150,
        ingredient_names=["rice", "tomato", "onion"],
        steps="1. Boil rice. 2. Fry onion and tomato into a stew. 3. Serve rice topped with stew.",
        prep_time=25,
        difficulty="easy",
    )

    add_meal(
        name="Spiced coconut rice",
        meal_of_day="lunch",
        cost=200,
        ingredient_names=["rice", "onion", "coconut milk"],
        steps="1. Fry onion. 2. Add rice and coconut milk, simmer until cooked.",
        prep_time=30,
        difficulty="easy",
    )

    add_meal(
        name="Tomato and onion omelette",
        meal_of_day="breakfast",
        cost=80,
        ingredient_names=["egg", "tomato", "onion"],
        steps="1. Beat eggs. 2. Chop tomato and onion, fry briefly. 3. Add eggs and cook through.",
        prep_time=10,
        difficulty="easy",
    )

    add_meal(
        name="Rice and vegetable stir fry",
        meal_of_day="supper",
        cost=180,
        ingredient_names=["rice", "tomato", "onion"],
        steps="1. Cook rice. 2. Stir-fry tomato and onion. 3. Mix together.",
        prep_time=20,
        difficulty="easy",
    )

    print("Sample meals added.")
