import requests

API_KEY = "AIzaSyD5rM-FUo91atUPXhhe7bQJdX2mYPWwqSo"

URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"


def generate_insight(expenses):

    if not expenses:

        return "No expenses recorded yet."

    prompt = f"""

    Analyze these expenses and give short financial advice.

    Expenses:

    {expenses}

    Tell:

    - highest spending category

    - suggestion to save money

    """

    data = {

        "contents": [

            {

                "parts": [

                    {"text": prompt}

                ]

            }

        ]

    }

    response = requests.post(URL, json=data)

    result = response.json()

    print("GEMINI RESPONSE:", result)

    if "candidates" in result:

        return result["candidates"][0]["content"]["parts"][0]["text"]

    if "error" in result:

        return result["error"]["message"]

    return "Insight could not be generated."