from models import db, User, Ingredient, Inventory, Meal, MealIngredient
from services import suggest_meals


def _add_ingredient(name):
    ingredient = Ingredient(name=name, unit="unit")
    db.session.add(ingredient)
    db.session.commit()
    return ingredient


def _add_meal(name, meal_of_day, cost, ingredients):
    meal = Meal(name=name, meal_of_day=meal_of_day, estimated_cost=cost)
    db.session.add(meal)
    db.session.commit()

    for ingredient in ingredients:
        db.session.add(MealIngredient(meal_id=meal.id, ingredient_id=ingredient.id, quantity=1))
    db.session.commit()
    return meal


def test_suggests_meal_within_budget_and_inventory(app):
    user = User(name="Grace")
    db.session.add(user)
    db.session.commit()

    rice = _add_ingredient("rice")
    tomato = _add_ingredient("tomato")

    db.session.add(Inventory(user_id=user.id, ingredient_id=rice.id, quantity=1))
    db.session.add(Inventory(user_id=user.id, ingredient_id=tomato.id, quantity=1))
    db.session.commit()

    meal = _add_meal("Rice and tomato", "lunch", cost=100, ingredients=[rice, tomato])

    results = suggest_meals(user.id, "lunch", budget_amount=200)

    assert meal in results


def test_excludes_meal_over_budget(app):
    user = User(name="Grace")
    db.session.add(user)
    db.session.commit()

    rice = _add_ingredient("rice")
    db.session.add(Inventory(user_id=user.id, ingredient_id=rice.id, quantity=1))
    db.session.commit()

    expensive_meal = _add_meal("Fancy rice", "lunch", cost=1000, ingredients=[rice])

    results = suggest_meals(user.id, "lunch", budget_amount=200)

    assert expensive_meal not in results


def test_excludes_meal_missing_ingredients(app):
    user = User(name="Grace")
    db.session.add(user)
    db.session.commit()

    rice = _add_ingredient("rice")
    coconut_milk = _add_ingredient("coconut milk")  # not in the user's inventory

    db.session.add(Inventory(user_id=user.id, ingredient_id=rice.id, quantity=1))
    db.session.commit()

    meal_needing_coconut = _add_meal("Coconut rice", "lunch", cost=100, ingredients=[rice, coconut_milk])

    results = suggest_meals(user.id, "lunch", budget_amount=200)

    assert meal_needing_coconut not in results


def test_only_returns_meals_for_the_requested_meal_of_day(app):
    user = User(name="Grace")
    db.session.add(user)
    db.session.commit()

    egg = _add_ingredient("egg")
    db.session.add(Inventory(user_id=user.id, ingredient_id=egg.id, quantity=1))
    db.session.commit()

    breakfast_meal = _add_meal("Omelette", "breakfast", cost=50, ingredients=[egg])
    _add_meal("Egg fried rice", "supper", cost=50, ingredients=[egg])  # different meal of day

    results = suggest_meals(user.id, "breakfast", budget_amount=200)

    assert results == [breakfast_meal]
