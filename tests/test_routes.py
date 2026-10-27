def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_profile(client):
    response = client.post("/profile", data={"name": "Grace", "dietary_goal": "fitness"})
    assert response.status_code == 302  # redirects back to the profile page

    response = client.get("/profile")
    assert b"Grace" in response.data


def test_add_inventory_item(client):
    response = client.post("/inventory", data={"ingredient_name": "rice", "quantity": "2"})
    assert response.status_code == 302

    response = client.get("/inventory")
    assert b"rice" in response.data


def test_set_budget(client):
    response = client.post("/budget", data={"amount": "500", "period": "weekly"})
    assert response.status_code == 302

    response = client.get("/budget")
    assert b"500" in response.data


def test_full_user_journey_returns_a_suggestion(client):
    """profile -> inventory -> budget -> suggestion -> log history, matching the SRS user flow."""

    client.post("/profile", data={"name": "Grace", "dietary_goal": "fitness"})
    client.post("/inventory", data={"ingredient_name": "rice", "quantity": "2"})
    client.post("/inventory", data={"ingredient_name": "tomato", "quantity": "2"})
    client.post("/budget", data={"amount": "500", "period": "weekly"})

    # Add a matching meal directly through the models, as seed.py would.
    from models import db, Meal, MealIngredient, Ingredient

    rice = Ingredient.query.filter_by(name="rice").first()
    tomato = Ingredient.query.filter_by(name="tomato").first()
    meal = Meal(name="Rice and tomato stew", meal_of_day="lunch", estimated_cost=150)
    db.session.add(meal)
    db.session.commit()
    db.session.add(MealIngredient(meal_id=meal.id, ingredient_id=rice.id, quantity=1))
    db.session.add(MealIngredient(meal_id=meal.id, ingredient_id=tomato.id, quantity=1))
    db.session.commit()

    response = client.get("/suggest?meal_of_day=lunch")
    assert response.status_code == 200
    assert b"Rice and tomato stew" in response.data

    response = client.get(f"/history/log/{meal.id}/cooked")
    assert response.status_code == 302

    response = client.get("/history")
    assert b"cooked" in response.data
