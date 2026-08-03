"""
Tile indexing (34 "playing" tile kinds, flowers are separate/bonus):
  0-8   : Characters (Wan)   1-9
  9-17  : Bamboos (Sou/Tiao) 1-9
  18-26 : Dots (Pin/Tong)    1-9
  27-33 : Honors: East, South, West, North, Red, Green, White
"""
import os
from groq import Groq, APIStatusError, APIConnectionError, APIError
from dotenv import load_dotenv

from prompts import (
    SYSTEM_PROMPT,
    ADVICE_USER_PROMPT,
    build_analyze_user_hand_prompt,
)

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---------------------------------------------------------------------------
# Tile metadata
# ---------------------------------------------------------------------------

HONOR_NAMES = ["East Wind", "South Wind", "West Wind", "North Wind",
               "Red Dragon", "Green Dragon", "White Dragon"]

def build_tile_info():
    info = []
    for k in range(9):
        info.append({"idx": k, "char": chr(0x1F007 + k), "label": f"{k+1} Characters", "suit": "m"})
    for k in range(9):
        info.append({"idx": 9 + k, "char": chr(0x1F010 + k), "label": f"{k+1} Bamboos", "suit": "s"})
    for k in range(9):
        info.append({"idx": 18 + k, "char": chr(0x1F019 + k), "label": f"{k+1} Dots", "suit": "p"})
    for k in range(7):
        info.append({"idx": 27 + k, "char": chr(0x1F000 + k), "label": HONOR_NAMES[k], "suit": "z"})
    return info

TILE_INFO = build_tile_info()  # length 34, index-aligned


def extract_hand_info_for_chatbot(hand, bonus):
    hand_info = ''
    for i in range(34):
        if hand[i] != 0:
            hand_info += f"I have {hand[i]} tiles named {TILE_INFO[i]["label"]}.\n"

    if bonus[0] != 0:
        if bonus[1] != 0:
            if bonus[0] == bonus[1]:
                hand_info += f"I have {bonus[0]} bonus tiles and they all are valid.\n"
            else:
                hand_info += f"I have {bonus[0]} bonus tiles but only {bonus[1]} bonus tiles are valid.\n"
        else:
            hand_info += f"I have {bonus[0]} bonus tiles but none of them are valid.\n"
    else:
        hand_info += f"I have no bonus tiles.\n"

    return hand_info

# ---------------------------------------------------------------------------
# Call chatbot
# ---------------------------------------------------------------------------
def random_advice():
   return chat_bot(build_message(ADVICE_USER_PROMPT, SYSTEM_PROMPT))

def advice_hand(hand, bonus, min_points, allow_7pairs, allow_13orphans, allow_peaceful):
    return chat_bot(build_message(
        build_analyze_user_hand_prompt(
            extract_hand_info_for_chatbot(hand, bonus),
            min_points, allow_7pairs, allow_13orphans, allow_peaceful)), SYSTEM_PROMPT)

# ---------------------------------------------------------------------------
# Chatbot core functions
# ---------------------------------------------------------------------------
def build_message(user_prompt, system_prompt = None):
    if system_prompt == None:
        messages = [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    return messages

def chat_bot(prompt, history = None):
    try:
        chat_completion = client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = prompt,
        )
        return  chat_completion.choices[0].message.content
    except APIStatusError as e:
        return f"API failed with status code {e.status_code}: {e.message}"
    except APIConnectionError:
        return "Failed to connect to the Groq server."
    except APIError as e:
        return f"An general Groq API error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
