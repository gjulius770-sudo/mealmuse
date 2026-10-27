"""
This is the "rule-based fallback" matcher described in the SRS
(section 3.3.2). It doesn't call any AI service - it just looks at
what meals the user can afford and can make with what they have.

Later this can be swapped out for a real call to an AI API, with
this function kept as the fallback for when that call fails or
times out.
"""

from models import Meal, MealIngredient, Inventory


def suggest_meals(user_id, meal_of_day, budget_amount):
    """
    Return a list of Meal objects that:
    - match the requested meal of the day (breakfast/lunch/supper)
    - cost no more than the user's budget
    - only use ingredients the user already has in their inventory
    """

    # Ingredients this user currently has at home
    user_ingredient_ids = {
        inv.ingredient_id for inv in Inventory.query.filter_by(user_id=user_id).all()
    }

    candidate_meals = Meal.query.filter_by(meal_of_day=meal_of_day).all()

    suggestions = []
    for meal in candidate_meals:
        if meal.estimated_cost > budget_amount:
            continue

        needed_ingredient_ids = {
            mi.ingredient_id for mi in MealIngredient.query.filter_by(meal_id=meal.id).all()
        }

        # Only suggest it if the user already has every ingredient it needs
        if needed_ingredient_ids.issubset(user_ingredient_ids):
            suggestions.append(meal)

    return suggestions
