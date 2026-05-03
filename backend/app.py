from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import os

# Watson services
from services.watson_nlu import analyze_text
from services.watson_dialog import get_response

# Cloudant database
from services.cloudant_service import save_expense, expense_db


# Flask app
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


# ---------------- SERVE WEBSITE ----------------

@app.route("/")
def serve_home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(app.static_folder, "dashboard.html")


# ---------------- CHAT ROUTE ----------------

@app.route('/chat', methods=['POST'])
def chat():

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply": "Please type a message."})

    text = user_message.lower()

    # ---------------- NLU ANALYSIS ----------------
    analysis = analyze_text(user_message)

    sentiment = analysis.get("sentiment")
    keywords = analysis.get("keywords")

    print("User Sentiment:", sentiment)
    print("Keywords:", keywords)

    # ---------------- EMOTIONAL AI SUPPORT ----------------

    if sentiment == "negative":

        if "stress" in text or "exam" in text:
            return jsonify({
                "reply": "I understand exams can feel stressful 😔. Try studying in small sessions and take short breaks. I can also create a study plan for you."
            })

        if "sad" in text or "depressed" in text:
            return jsonify({
                "reply": "I'm sorry you're feeling this way. Taking a short walk or talking to someone you trust can help. I'm here to help you manage tasks and stay organized 💙"
            })

        return jsonify({
            "reply": "It seems like you're having a tough moment. I can help you plan your day, track expenses, or organize tasks."
        })

    # ---------------- EXPENSE DETECTION ----------------

    if "expense" in text:

        try:
            words = user_message.split()

            amount = float(words[2])
            category = words[3]

            save_expense(amount, category)

            return jsonify({
                "reply": f"Expense of ₹{amount} for {category} saved successfully 💰"
            })

        except:
            return jsonify({
                "reply": "Please type like: add expense 500 food"
            })

    # ---------------- STUDY PLANNER ----------------

    if "study plan" in text:

        days = re.findall(r'\d+', text)

        if days:
            d = int(days[0])
        else:
            d = 5

        plan = "Here is your study plan:\n\n"

        for i in range(1, d + 1):
            plan += f"Day {i} – Study important concepts and practice questions.\n"

        return jsonify({"reply": plan})

    # ---------------- WATSON CHATBOT ----------------

    reply = get_response(user_message)

    return jsonify({"reply": reply})


# ---------------- GET EXPENSES ----------------

@app.route('/expenses')
def get_expenses():

    docs = []

    for doc in expense_db:
        docs.append({
            "amount": float(doc.get("amount", 0)),
            "category": doc.get("category", "unknown")
        })

    return jsonify(docs)


# ---------------- SMART INSIGHTS ----------------

@app.route('/insights')
def insights():

    docs = []

    for doc in expense_db:
        docs.append({
            "amount": float(doc.get("amount", 0)),
            "category": doc.get("category", "unknown")
        })

    if len(docs) == 0:
        return jsonify({
            "insight": "No expenses added yet. Start tracking your spending!"
        })

    total = sum(e["amount"] for e in docs)

    category_totals = {}

    for e in docs:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    highest_category = max(category_totals, key=category_totals.get)

    insight = f"You have spent most of your money on {highest_category}. Total spending so far is ₹{total}. Try managing this category to save more."

    return jsonify({"insight": insight})


# ---------------- EXPENSE PREDICTION ----------------

@app.route("/prediction")
def prediction():

    docs = []

    for doc in expense_db:
        amount = float(doc.get("amount", 0))
        docs.append(amount)

    if len(docs) == 0:
        return jsonify({
            "prediction": "Not enough data to predict expenses yet."
        })

    avg = sum(docs) / len(docs)

    predicted = avg * 1.2

    return jsonify({
        "prediction": f"Based on your spending pattern, your next expenses may be around ₹{round(predicted,2)}"
    })


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)