"""
PROJECT 1 — Context-Aware Chatbot with Memory

Your task is to build a chatbot that can remember useful information from
previous messages and use that memory to answer later questions.

This chatbot should be able to:

1. Build a working chatbot interface
   - You may use Gradio or a simple CLI.
   - The chatbot should accept user input and return an AI response.

2. Maintain conversation history
   - Store both user messages and assistant replies.
   - Use recent conversation history so the chatbot can understand context.

3. Store memory
   - Use JSON, SQLite, or ChromaDB.
   - For the basic version, SQLite or JSON is enough.
   - Each message should be saved with at least:
       role      -> "user" or "assistant"
       content   -> the message text
       timestamp -> when the message was saved

4. Retrieve relevant memory
   - Do not send the entire history to the model every time.
   - Retrieve only useful memory.
   - Basic version: keyword search.
   - Advanced version: semantic search using embeddings / ChromaDB.

5. Use provided files from Moodle
   - Load skills.md as learner profile or background knowledge.
   - Load memory_seed.json as structured starting memory.
   - Add both into the system prompt when helpful.

6. Apply prompt engineering
   - Write a clear system prompt.
   - Tell the model how to use memory.
   - Tell the model not to invent personal facts.
   - Tell the model to say “I don’t know” if memory does not contain the answer.

7. Bonus features
   - Add summarization when the conversation becomes long.
   - Support multiple users with separate memory.
   - Improve latency by limiting how much memory is sent to the model.

Suggested structure:

- setup database / memory file
- load skills.md
- load memory_seed.json
- save_memory()
- search_memory()
- get_recent_history()
- build_messages()
- chat_bot()
- Gradio or CLI interface

Important idea:
main chatbot function should not do everything by itself.
It should coordinate smaller helper functions, similar to the AI pipeline idea:
input -> retrieve memory -> build prompt -> call model -> save response -> return output.
"""

import os
import json
import copy
from groq import Groq
import gradio as gr
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
file = "memory.json"
skills = "skills.md"
seed = "memory_seed.json"

def load_profile():
    try:
        with open(skills, "r") as f:
            return f.read()
    except:
        return ""

def load_memory_seed():
   try:
      with open(seed, "r") as f:
            return f.read()
   except:
      return []

def load_memory():
   try:
      with open(file, "r") as f:
         file_output = json.load(f)
         return file_output
   except:
      return []


def save_memory(memory):
   with open(file, "w") as f:
      json.dump(memory, f)

def search_memory(memory, keyword):
   matches = [item for item in memory if keyword.lower() in item["content"].lower()]
   return matches

def get_recent_history(memory, count):
   return memory[-count:]
    
def build_message(prompt):
   chat_memory = load_memory()
   chat_memory_copy = copy.deepcopy(chat_memory)
   print(chat_memory_copy)
   for item in chat_memory_copy:
      item.pop("timestamp", None)
   print(chat_memory_copy)
   chat_memory_copy = get_recent_history(chat_memory_copy, 6)

   profile_memory = load_profile()
   memory_seed_memory = load_memory_seed()

   chat_memory_copy.append({
        "role": "user",
        "content": prompt
    })

   messages = [
      {
         "role": "system",
         "content": f"User profile:\n{profile_memory}\nUser data:\n{memory_seed_memory}"
      }
   ]
   messages.extend(chat_memory)
   return messages
   

def chat_bot(prompt, history):
   messages = build_message(prompt)

   chat_completion = client.chat.completions.create(
      messages = messages,
      model = "llama-3.1-8b-instant"
   )

   reply = chat_completion.choices[0].message.content
   messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp" : datetime.now(ZoneInfo("Asia/Singapore"))
    })
   save_memory(messages)

   return reply


gr.ChatInterface(
   fn=chat_bot,
   title="Project 1 Chatbot",
   description="zhi wei project 1 chatbot."
).launch()