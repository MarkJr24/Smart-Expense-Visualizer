import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

def train_model(csv_path="data/expenses.csv"):
    df = pd.read_csv(csv_path)
    df = df[df['Note'].notna()]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['Note'])
    y = df['Category']

    model = MultinomialNB()
    model.fit(X, y)

    joblib.dump(model, "ml/category_model.pkl")
    joblib.dump(vectorizer, "ml/vectorizer.pkl")
