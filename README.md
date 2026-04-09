# 📰 Fake News Detection Chatbot

A full-stack AI-powered chatbot that detects whether a given claim is **REAL**, **FAKE**, or **UNCERTAIN** using a combination of:

* 🤖 Large Language Models (LLMs)
* 🔍 Web Search (Tavily API)
* 📊 Machine Learning (Logistic Regression)

---

## 🚀 Features

* 🧠 **Automatic Claim Extraction**
* 🔀 **Smart Routing**

  * Normal chat → behaves like a chatbot
  * News/claims → fact-check pipeline
* 🌐 **Real-time Web Search Integration**
* 📊 **Fake Probability Prediction (ML Model)**
* 💬 **Conversational Context Support**
* ⚡ Fast API using Flask
* 🎨 Clean React Chat UI

---

## 🏗️ Architecture

```
User Input
   ↓
Extract Claim
   ↓
 ┌───────────────┐
 │               │
NO_CLAIM     VALID CLAIM
 │               │
Chat Mode     ML Model → Web Search → LLM Verdict
```

---

## 🧠 Tech Stack

### 🔹 Backend

* Python
* Flask
* LangGraph
* LangChain
* Groq API (LLM)
* Tavily Search API
* Scikit-learn (Logistic Regression)

### 🔹 Frontend

* React.js
* Tailwind CSS

---

## 📂 Project Structure

```
chat_bot/
│
├── backend/
│   ├── app.py
│   ├── fake_prob_model.pkl
│   ├── cleaner_pipeline.pkl
│   ├── Fake.csv
│   └── True.csv
│
├── frontend/
│   ├── src/
│   └── package.json
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 🔹 1. Clone the Repository

```
git clone <your-repo-url>
cd chat_bot
```

---

### 🔹 2. Backend Setup

```
cd backend
pip install -r requirements.txt
```

#### Add API Keys:

```
export GROQ_API_KEY=your_key
export TAVILY_API_KEY=your_key
```

---

### 🔹 3. Run Backend

```
python app.py
```

---

### 🔹 4. Frontend Setup

```
cd frontend
npm install
npm run dev
```

---

## 🔌 API Endpoint

### POST `/check`

#### Request:

```json
{
  "message": "Is XYZ true?",
  "context": [
    { "role": "user", "content": "previous message" }
  ]
}
```

#### Response:

```json
{
  "response": "Verdict: REAL\nExplanation: ..."
}
```

---

## 🧪 Example

### Input:

```
"India won the 2023 World Cup"
```

### Output:

```
Verdict: FAKE  
Explanation: Web sources contradict the claim...
```

---

## 🧠 How It Works

1. Extracts a **verifiable claim** from user input
2. If no claim → behaves like normal chatbot
3. If claim exists:

   * Predicts fake probability (ML model)
   * Fetches web results
   * LLM analyzes evidence
4. Generates final verdict

---

## ⚠️ Limitations

* Depends on quality of web sources
* ML model trained on limited dataset
* May misclassify vague or ambiguous claims

---

## 🔮 Future Improvements

* ✅ Better claim classification (multi-class)
* ✅ Confidence scoring
* ✅ UI enhancements (chat bubbles, loading states)
* ✅ Caching API responses
* ✅ Deployment (Docker / Cloud)

---

## 👨‍💻 Author

**Radhe Chaudhary**

---

## ⭐ Contribute

Feel free to fork, improve, and submit PRs!

---

## 📜 License

MIT License
