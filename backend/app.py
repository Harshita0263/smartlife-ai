from flask import Flask, request, jsonify, send_from_directory, session, redirect, render_template
from flask_cors import CORS
import re
import os
import requests

# Watson services
from services.watson_nlu import analyze_text
from services.watson_dialog import get_response

# Cloudant database
from services.cloudant_service import save_expense, expense_db

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "smartlife_secret"
CORS(app)

# ---------------- IBM APP ID CONFIG ----------------

APPID_CLIENT_ID = os.getenv("APPID_CLIENT_ID")
APPID_SECRET = os.getenv("APPID_SECRET")
APPID_OAUTH_SERVER = os.getenv("APPID_OAUTH_SERVER")
REDIRECT_URI = os.getenv("REDIRECT_URI")


# ---------------- SERVE WEBSITE ----------------

@app.route("/")

def home():

    if "user" in session:

        return render_template("index.html")

    else:

        return render_template("login.html")


@app.route("/dashboard")
def serve_dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


# ---------------- IBM APP ID LOGIN ----------------

@app.route("/login")
def login():

    oauth_url = (
        f"{APPID_OAUTH_SERVER}/authorization?"
        f"client_id={APPID_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid"
    )

    return redirect(oauth_url)


# ---------------- IBM CALLBACK ----------------

@app.route("/callback")
def callback():

    code = request.args.get("code")

    token_url = f"{APPID_OAUTH_SERVER}/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": APPID_CLIENT_ID,
        "client_secret": APPID_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, data=data)

    token_data = response.json()

    if "id_token" not in token_data:
        return "Login failed"

    session["user"] = token_data["id_token"]

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- CURRENT USER ----------------

@app.route("/session-user")
def session_user():

    if "user" in session:
        return jsonify({"user": "Authenticated User"})

    return jsonify({"user": "Guest"})


# ---------------- CHAT ----------------

@app.route("/chat", methods=["POST"])
def chat():

    if "user" not in session:
        return jsonify({"reply": "Please login first."})

    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"reply": "Please type a message."})

    text = user_message.lower()

    # ---------------- NLU ANALYSIS ----------------

    analysis = analyze_text(user_message)

    sentiment = analysis.get("sentiment")
    keywords = analysis.get("keywords")

    print("User:", session["user"])
    print("Sentiment:", sentiment)
    print("Keywords:", keywords)


    # ---------------- EMOTIONAL SUPPORT ----------------

    if sentiment == "negative":

        if "stress" in text or "exam" in text:
            return jsonify({
                "reply": "Exams can feel stressful. Try studying in small sessions with breaks."
            })

        if "sad" in text or "depressed" in text:
            return jsonify({
                "reply": "I'm sorry you're feeling low. Talking to someone you trust can help."
            })

        return jsonify({
            "reply": "It seems like you're having a tough moment. I can help organize tasks or expenses."
        })


    # ---------------- EXPENSE TRACKING ----------------

    if "expense" in text or "spent" in text:

        try:

            amount_match = re.search(r"\d+", text)

            if not amount_match:
                return jsonify({"reply": "Please include an amount."})

            amount = float(amount_match.group())

            category_match = re.search(r"on\s+(\w+)", text)

            if category_match:
                category = category_match.group(1)
            else:
                words = text.split()

                if len(words) >= 4:
                    category = words[-1]
                else:
                    category = "general"

            save_expense(session["user"], amount, category)

            return jsonify({
                "reply": f"Expense of ₹{amount} for {category} saved successfully 💰"
            })

        except:
            return jsonify({
                "reply": "Example: add expense 500 food OR I spent 200 on food"
            })


    # ---------------- STUDY PLANNER ----------------

    if "study" in text or "prepare" in text or "exam" in text:

        days = re.findall(r"\d+", text)

        if days:
            d = int(days[0])
        else:
            d = 5

        tasks = [
            "Understand basic concepts",
            "Study important chapters",
            "Practice numerical problems",
            "Revise difficult topics",
            "Solve previous year questions",
            "Take a mock test",
            "Final revision"
        ]

        plan = "Here is your study plan:\n\n"

        for i in range(d):
            task = tasks[i % len(tasks)]
            plan += f"Day {i+1} – {task}\n"

        return jsonify({"reply": plan})


    # ---------------- WATSON CHATBOT ----------------

    reply = get_response(user_message)

    return jsonify({"reply": reply})


# ---------------- GET EXPENSES ----------------

@app.route("/expenses")
def get_expenses():

    if "user" not in session:
        return jsonify([])

    docs = []

    for doc in expense_db:

        if doc.get("user") == session["user"]:

            docs.append({
                "amount": float(doc.get("amount", 0)),
                "category": doc.get("category", "unknown")
            })

    return jsonify(docs)


# ---------------- INSIGHTS ----------------

@app.route("/insights")
def insights():

    if "user" not in session:
        return jsonify({"insight": "Please login first."})

    docs = []

    for doc in expense_db:

        if doc.get("user") == session["user"]:

            docs.append({
                "amount": float(doc.get("amount", 0)),
                "category": doc.get("category", "unknown")
            })

    if len(docs) == 0:
        return jsonify({"insight": "No expenses added yet."})

    total = sum(e["amount"] for e in docs)

    category_totals = {}

    for e in docs:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    highest_category = max(category_totals, key=category_totals.get)

    insight = f"You spent most on {highest_category}. Total spending is ₹{total}"

    return jsonify({"insight": insight})


# ---------------- PREDICTION ----------------

@app.route("/prediction")
def prediction():

    if "user" not in session:
        return jsonify({"prediction": "Please login first."})

    docs = []

    for doc in expense_db:
        if doc.get("user") == session["user"]:
            docs.append(float(doc.get("amount", 0)))

    if len(docs) == 0:
        return jsonify({"prediction": "Not enough data yet."})

    avg = sum(docs) / len(docs)

    predicted = avg * 1.2

    return jsonify({
        "prediction": f"Your next spending may be around ₹{round(predicted,2)}"
    })


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    print("🚀 SmartLife AI Server Started")

    app.run(host="0.0.0.0", port=port)