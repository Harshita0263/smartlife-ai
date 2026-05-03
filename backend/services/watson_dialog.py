from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import uuid

API_KEY = "tLq9Hl1vjyv0X2hj0Ms75zqX2hWsRbLQySXIZ6pXg6wv"
URL = "https://api.au-syd.assistant.watson.cloud.ibm.com/instances/1c4ed5df-4a19-47eb-a4ec-eee40f00fb5f"
ASSISTANT_ID = "b9e95d81-e699-4c3d-ad0f-b9eba9981194"
ENVIRONMENT_ID = "e4a7f2a7-3df3-409a-ab4b-357b7543902c"  

authenticator = IAMAuthenticator(API_KEY)

assistant = AssistantV2(
    version='2021-11-27',
    authenticator=authenticator
)

assistant.set_service_url(URL)

session_id = None


def create_session():
    global session_id

    session = assistant.create_session(
        assistant_id=ASSISTANT_ID,
        environment_id=ENVIRONMENT_ID   
    ).get_result()

    session_id = session["session_id"]


def get_response(message):
    global session_id

    if session_id is None:
        create_session()

    try:
        response = assistant.message(
            assistant_id=ASSISTANT_ID,
            environment_id=ENVIRONMENT_ID,   # ⭐ FIX HERE
            session_id=session_id,
            user_id="smartlife-user",
            input={
                'message_type': 'text',
                'text': message
            }
        ).get_result()

        generic = response.get("output", {}).get("generic", [])

        if generic:
            return generic[0].get("text", "No response from Watson")

        return "I didn't understand that."

    except Exception as e:
        print("Watson Error:", e)
        return "Error connecting to Watson"