import pandas as pd
import numpy as np
import joblib
import re
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin

#read the csv 
fake = pd.read_csv('./Fake.csv')
fake["label"] = 0


true = pd.read_csv('./True.csv')
true["label"] = 1

data = pd.concat([fake, true], ignore_index=True)
data = data[['text', 'label']]

# split train_test
train_message, test_message, train_label, test_label = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)


class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X.apply(self.clean_text)
    
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"\d+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

#clean and vecotrize the message
pipeline = Pipeline([
    ("clean", TextCleaner()),
    ("vectorize", TfidfVectorizer(stop_words="english"))
])

#train the model
train_message = pipeline.fit_transform(train_message)
model = LogisticRegression()
model.fit(train_message, train_label)
print("Model Trained Successfully")

#dump the model and the transform pipeline
joblib.dump(model, "fake_prob_model.pkl")
joblib.dump(pipeline, "cleaner_pipeline.pkl")