import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import re
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from flask import Flask, jsonify, request
from typing import List, Union





model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2,
    # other params...
)

# from langchain.chat_models import init_chat_model

# model = init_chat_model("google_genai:gemini-2.5-flash-lite")




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
    
fake_prob_model = joblib.load("fake_prob_model.pkl")
cleaner_pipeline = joblib.load("cleaner_pipeline.pkl")

class State(TypedDict):
    response: str
    query: str
    claim:str
    web_result:list[str]
    probability:str
    context: List[Union[HumanMessage, SystemMessage]]

from langchain_tavily import TavilySearch
search_tool = TavilySearch(max_results=4)

model.bind_tools([search_tool])

def extract_claim(state):
    prompt = f"""
    Extract ONE factual claim ONLY IF it is:

    - About public facts, news, events, or statements
    - Can be verified using external sources

    DO NOT extract claims for:
    - personal statements (e.g., "my name is...")
    - opinions
    - casual chat
    - introductions

    If the text is NOT a verifiable public claim, return: NO_CLAIM

    Text: "{state["query"].content}"

    Output:
    """
    claim = model.invoke(prompt)
    state["claim"] = claim.content.strip()
    return state

def route_after_claim(state):
    claim = state["claim"]
    # reject personal patterns
    if any(x in claim for x in ["my name", "i am", "i live", "my age"]):
        return "normal_chat"

    if claim == "NO_CLAIM":
        return "normal_chat"

    return "get_probability"

def normal_chat(state):
    context_text = "\n".join([
        f"{type(msg).__name__}: {msg.content}"
        for msg in state["context"][-8:]  # last 4 messages only
    ])
    prompt = f"""You are a helpful assistant for general questions and casual conversation.
        -Answer the user's query based on the conversation context.
        -use search tool when needed to answer the user's query. 
        -If the user asks for information that is not present in the conversation context, use the search tool to find relevant information and include it in your response.
        -Provide clean an straightforward answers without unnecessary elaboration.
        don't hallucinate
        Context:{context_text}
        User Query: {state["query"]}"""
    state["response"] = model.invoke(prompt)

    return state

def get_probability(state):
    x = pd.Series([state["claim"]])
    x = cleaner_pipeline.transform(x)
    prob = fake_prob_model.predict_proba(x)
    state["probability"] = f"{prob[0][0]}"
    return state;

def search(state):
    search_text = f"{state['claim']} tell about this"
    response = search_tool.invoke(search_text)
    state['web_result'] =  response["results"]
    return state

def result(state):
    context_text = "\n".join([
        f"{type(msg).__name__}: {msg.content}"
        for msg in state["context"][-8:]  # last 4 messages only
    ])
    
    prompt = f"""
    Conversation:{context_text}
    Claim:{state["claim"]}
    web Result : {state["web_result"]}
    fake probability : {state["probability"]}
    Verdict: REAL / FAKE / UNCERTAIN
    Explanation: Provide a brief explanation for the verdict based on the web results and probability.
    Don't include probability in the explanation, just use it as a factor in your reasoning.
    Don't just rely on the probability, use the web results to make a more informed decision. If the web results strongly support the claim, it is likely REAL. If they strongly contradict the claim, it is likely FAKE. If the web results are inconclusive or mixed, it is UNCERTAIN.
    
    Sources:
    - list sources
    """
    result = model.invoke(prompt)
    state["response"] = result
    return state

from langgraph.graph import StateGraph
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

workflow = StateGraph(State)

workflow = StateGraph(State)

workflow.add_node("extract_claim", extract_claim)
workflow.add_node("get_probability", get_probability)
workflow.add_node("search", search)
workflow.add_node("result", result)
workflow.add_node("normal_chat", normal_chat)

workflow.set_entry_point("extract_claim")

# Conditional routing
workflow.add_conditional_edges(
    "extract_claim",
    route_after_claim,
    {
        "normal_chat": "normal_chat",
        "get_probability": "get_probability"
    }
)

# Continue pipeline
workflow.add_edge("get_probability", "search")
workflow.add_edge("search", "result")

graph = workflow.compile()

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/check', methods=["POST"])
def query():
    request_data = request.get_json()

    parsed = []

    # convert old messages
    for msg in request_data.get("context", []):
        if msg["role"] == "user":
            parsed.append(HumanMessage(content=msg["content"]))
        else:
            parsed.append(AIMessage(content=msg["content"]))

    # add current user message
    current_msg = HumanMessage(content=request_data["message"])
    print('....................................................................................................')
    print(parsed)
    print()
    print('..........................................///////////////////////..........................................................')
    response = graph.invoke({
        "query": current_msg,  # current user message
        "context": parsed     # previous messages
    })
    print(response["response"].content)
    return jsonify({"response": response["response"].content})

if __name__ == "__main__":
    app.run(debug=True)


