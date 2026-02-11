import pyrebase

firebase_config = {
    "apiKey": "your-api-key",
    "authDomain": "your-project.firebaseapp.com",
    "databaseURL": "https://your-project.firebaseio.com",
    "projectId": "your-project-id",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "sender-id",
    "appId": "app-id"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

def upload_expense_to_firebase(expense):
    db.child("expenses").push(expense)
