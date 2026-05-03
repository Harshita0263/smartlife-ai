from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions

# ---------------- IBM NLU CONFIG ----------------
API_KEY = "PupsWhcjkCaao_zXm_WlOhSHwm2zWCkrCKZPQS1TucrK"
URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/510d133c-201b-41c0-b134-7c051048c017"

authenticator = IAMAuthenticator(API_KEY)

nlu = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)

nlu.set_service_url(URL)


# ---------------- ANALYZE TEXT ----------------
def analyze_text(text):

    try:

        response = nlu.analyze(
            text=text,
            features=Features(
                sentiment=SentimentOptions(),
                keywords=KeywordsOptions(limit=3)
            )
        ).get_result()

        sentiment = response["sentiment"]["document"]["label"]

        keywords = []

        for k in response["keywords"]:
            keywords.append(k["text"])

        return {
            "sentiment": sentiment,
            "keywords": keywords
        }

    except Exception as e:
        print("NLU Error:", e)

        return {
            "sentiment": "unknown",
            "keywords": []
        }