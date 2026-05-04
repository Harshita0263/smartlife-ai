from cloudant.client import Cloudant

USERNAME = "apikey-v2-2rthdp2yoab9qiuuryhk6q7gl473xcepkpxt5b5cd337"
PASSWORD = "d3eb526b611929872d8436e5c882974d"
URL = "https://apikey-v2-2rthdp2yoab9qiuuryhk6q7gl473xcepkpxt5b5cd337:d3eb526b611929872d8436e5c882974d@1ddb04c1-9d7a-4d04-9748-7e1b4301e585-bluemix.cloudantnosqldb.appdomain.cloud"

client = Cloudant(USERNAME, PASSWORD, url=URL, connect=True)

expense_db = client["smartlife_expenses"]
task_db = client["smartlife_tasks"]


def save_expense(user, amount, category):

    data = {
        "user": user,
        "amount": amount,
        "category": category
    }

    expense_db.create_document(data)


def save_task(task):

    data = {
        "task": task
    }

    task_db.create_document(data)