from googlesearch import search
from groq import Groq
from json import dump, load
import datetime
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")

GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

current_dir = os.path.dirname(os.path.abspath(_file_))
chatlog_path = os.path.join(current_dir, "..", "Data", "ChatLog.json")

try:
    with open(chatlog_path, "r", encoding="utf-8") as f:
        _ = load(f)
except:
    with open(chatlog_path, "w", encoding="utf-8") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(prompt):
    if len(prompt) > 300:
        prompt = prompt[:300]

    try:
        with open(chatlog_path, "r", encoding="utf-8") as f:
            full_log = load(f)
            messages = full_log[-2:] if len(full_log) > 2 else full_log
    except:
        messages = []

    messages.append({"role": "user", "content": prompt})

    search_result = {"role": "system", "content": GoogleSearch(prompt)}
    if len(SystemChatBot) > 5:
        SystemChatBot[:] = SystemChatBot[:3]
    SystemChatBot.append(search_result)

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=True
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(chatlog_path, "w", encoding="utf-8") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

if _name_ == "_main_":
    while True:
        prompt = input("Enter your question: ")
        print(RealtimeSearchEngine(prompt))
