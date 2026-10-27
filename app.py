from datetime import date
from flask import Flask, render_template, request, redirect, url_for

from models import db, User, Ingredient, Inventory, Budget, Meal, MealHistory
from services import suggest_meals
from ai_service import get_ai_reply, AIUnavailableError
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Make sure the database tables exist, whether we're running locally
# with `python app.py` or being started by a production server like
# gunicorn (which doesn't go through the __main__ block below).
with app.app_context():
    db.create_all()

# For now there's no login system, so we just work with a single
# demo user. This keeps things simple while the rest of the app
# is being built - a real login can be added later.
DEMO_USER_ID = 1


@app.route("/")
def home():
    return render_template("index.html")


# ---- Profile ----

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = User.query.get(DEMO_USER_ID)

    if request.method == "POST":
        name = request.form["name"]
        dietary_goal = request.form.get("dietary_goal", "none")

        if user is None:
            user = User(id=DEMO_USER_ID, name=name, dietary_goal=dietary_goal)
            db.session.add(user)
        else:
            user.name = name
            user.dietary_goal = dietary_goal

        db.session.commit()
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ---- Inventory ----

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        ingredient_name = request.form["ingredient_name"]
        quantity = float(request.form.get("quantity", 1))

        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if ingredient is None:
            ingredient = Ingredient(name=ingredient_name, unit="unit")
            db.session.add(ingredient)
            db.session.commit()

        item = Inventory(user_id=DEMO_USER_ID, ingredient_id=ingredient.id, quantity=quantity)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("inventory"))

    items = Inventory.query.filter_by(user_id=DEMO_USER_ID).all()
    return render_template("inventory.html", items=items)


# ---- Budget ----

@app.route("/budget", methods=["GET", "POST"])
def budget():
    current_budget = Budget.query.filter_by(user_id=DEMO_USER_ID).first()

    if request.method == "POST":
        amount = float(request.form["amount"])
        period = request.form.get("period", "weekly")

        if current_budget is None:
            current_budget = Budget(user_id=DEMO_USER_ID, amount=amount, period=period)
            db.session.add(current_budget)
        else:
            current_budget.amount = amount
            current_budget.period = period

        db.session.commit()
        return redirect(url_for("budget"))

    return render_template("budget.html", budget=current_budget)


# ---- Meal suggestions ----

@app.route("/suggest")
def suggest():
    meal_of_day = request.args.get("meal_of_day", "lunch")

    current_budget = Budget.query.filter_by(user_id=DEMO_USER_ID).first()
    budget_amount = current_budget.amount if current_budget else 0

    results = suggest_meals(DEMO_USER_ID, meal_of_day, budget_amount)
    return render_template("suggest.html", meals=results, meal_of_day=meal_of_day)


@app.route("/history/log/<int:meal_id>/<status>")
def log_history(meal_id, status):
    entry = MealHistory(user_id=DEMO_USER_ID, meal_id=meal_id, date=date.today(), status=status)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for("history"))


@app.route("/history")
def history():
    entries = MealHistory.query.filter_by(user_id=DEMO_USER_ID).order_by(MealHistory.date.desc()).all()
    return render_template("history.html", entries=entries)


# ---- AI chatbox ----

def fallback_reply(meal_of_day, budget_amount):
    """Used when the AI service can't be reached - built from the rule-based matcher."""
    meals = suggest_meals(DEMO_USER_ID, meal_of_day, budget_amount)

    if not meals:
        return (
            "(AI unavailable) I couldn't reach the AI service right now, and I don't "
            "have a matching meal in your inventory and budget either. Try adding more ingredients."
        )

    meal_names = ", ".join(meal.name for meal in meals)
    return f"(AI unavailable, showing rule-based suggestions instead) You could make: {meal_names}."


@app.route("/chat", methods=["GET", "POST"])
def chat():
    reply = None

    if request.method == "POST":
        message = request.form["message"]
        meal_of_day = request.form.get("meal_of_day", "lunch")

        user = User.query.get(DEMO_USER_ID)
        dietary_goal = user.dietary_goal if user else None

        inventory_names = [
            item.ingredient.name for item in Inventory.query.filter_by(user_id=DEMO_USER_ID).all()
        ]

        current_budget = Budget.query.filter_by(user_id=DEMO_USER_ID).first()
        budget_amount = current_budget.amount if current_budget else 0

        try:
            reply = get_ai_reply(message, dietary_goal, inventory_names, budget_amount)
        except AIUnavailableError:
            reply = fallback_reply(meal_of_day, budget_amount)

    return render_template("chat.html", reply=reply)


if __name__ == "__main__":
    app.run(debug=True)
