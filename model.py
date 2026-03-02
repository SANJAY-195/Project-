from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training data
descriptions = [
    "hotel food dinner", "bus ticket travel", "electricity bill",
    "movie ticket", "mobile recharge", "groceries shopping",
    "train ticket", "restaurant lunch", "internet bill"
]

categories = [
    "Food", "Travel", "Bills",
    "Entertainment", "Bills", "Food",
    "Travel", "Food", "Bills"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(descriptions)

model = MultinomialNB()
model.fit(X, categories)

def predict_category(text):
    text_vec = vectorizer.transform([text])
    return model.predict(text_vec)[0]
