# 1. Project Title and Description

This project name is called Mahjong Hand Analyzer.
It helps analyze your mahjong hand and gives options on what to aim for.
It is for people who cannot figure out what to do with their hand.

# 2. Problem Statement

As mahjong is a simple game that can get very complicated, it can be hard to see if your hand is able to win.
Even if your hand meets basic win conditions, but because of special rules/minimum points, it is not considered a win yet.
This app would help you check if your hand is able to win and even if the hand is not a win,
this app would give you advice on which path to take to make your hand a winning hand.

# 3. Technology Stack

- Python
- pythondotenv
- streamlit
- Groq REST API

# 4. Setup Instructions

Follow these instructions to set up a copy of the project on your local machine.

1. Download app.py, mahjong_chatbot.py, prompts.py, .env.example and requirements.txt from the link below.
https://github.com/ChungZhiWei/ai-bootcamp-portfolio/tree/fcfe6d131fad4f3c432654d52096522fa9382a49/capstone
2. Create a folder and put these 5 files inside.
3. Open .env.example and fill the API key. (replace "InsertKeyHere" with your groq API Key)
4. Change ".env.example" name to ".env".
5. Open command prompt and navigate to the folder with these 5 files inside.
6. Create a python environment and activate it. In command prompt, run (python -m venv .venv) and (.venv\Scripts\activate).
7. Install python requirements.txt. In command prompt, run (pip install -r requirements.txt)
8. Run the application. In command prompt, run (streamlit run app.py)

# 5. Usage Examples

You will need to set the mahjong rules at the side bar. Set them as necessary.
After that on the main screen, You will need to key in how many of that tile you have in the box.
There are many boxes with the tile associated with the box displayed above the box.
Example if I have 3 3 bamboos, I need to find the box with 3 bamboos above it and key in 3.
After keying in your hand, You need to check if you have any flower/season/bonus tiles.
In "Total number of bonus tiles held", key in the total number of flower/season/bonus tiles you have.
In "Total number of valid bonus tiles held", key in the total number of flower/season/bonus tiles that would give you points.
After that you can look below and see if your current hand is displayed correctly and your hand and bonus tiles are correct.
Once the information is correct you can hit "Analyze Hand" button.
For example I have 3 5 characters, 1 1 bamboo, 1 2 bamboo, 1 3 bamboo, 3 6 bamboo, 2 5 dots, 1 6 dots, 1 north wind, 1 red dragon, 2 bonus tiles but only 1 is valid.
The output would be as below (settings all enabled with minimum points needed set to 1):
'''
1. HAND ASSESSMENT

Your hand currently has 14 tiles and is one tile away from a legal winning hand.
You already have three complete sets (5 Characters ×3, 6 Bamboos ×3, 1‑2‑3 Bamboos) and a pair (5 Dots ×2).
The remaining three tiles (6 Dots, North Wind, Red Dragon) cannot form a fourth set, so the hand is not a winning hand yet.
2. OPTIONS

Summary (completed hand)	Discard now	Take (tile you need)	Score breakdown*	Total fan
A	Triplet 5 C, Triplet 6 B, Sequence 1‑2‑3 B, Triplet 6 D, Pair 5 D (self‑draw)	North Wind (or Red Dragon – either single honor)	6 Dots (to make a triplet)	– Triplet 5 C (no extra fan) <br> – Triplet 6 B (no extra fan) <br> – Triplet 6 D (no extra fan) <br> – Sequence 1‑2‑3 B (no extra fan) <br> – Pair 5 D (non‑honor) <br> – Self‑draw +1 fan <br> – Valid bonus tile +1 fan	2
B	Same hand as A but discard Red Dragon instead of North Wind (identical result)	Red Dragon	6 Dots	Same as above	2
C	All‑Triplet Hand – Triplet 5 C, Triplet 6 B, Triplet 5 D, Triplet 6 D, Pair North Wind** (self‑draw)	1 Bamboo (break the 1‑2‑3 B sequence)	5 Dots (to turn your pair into a triplet) or 6 Dots (to complete the second triplet)	– Triplet 5 C (+0) <br> – Triplet 6 B (+0) <br> – Triplet 5 D (+0) <br> – Triplet 6 D (+0) <br> – Pair North Wind (+0) <br> – All‑Triplets +2 fan (standard) <br> – Self‑draw +1 fan <br> – Valid bonus tile +1 fan	4
D	Half‑Flush (Bamboo + Honors) – 1‑2‑3 B, 5‑6‑7 B (after drawing 4 B & 7 B), Triplet 6 B, Pair North Wind, plus the existing 5 C triplet as an extra set (requires many changes)	5 Characters (discard one 5 C)	4 Bamboo and 7 Bamboo (to create a second Bamboo sequence) plus a suitable tile for the fourth set (e.g., another 6 B for a triplet)	– Half‑Flush +2 fan <br> – Self‑draw +1 fan (if you draw the needed tiles) <br> – Valid bonus tile +1 fan	Minimum 4 (but requires 3 specific draws, low probability)
E	Seven‑Pairs – Convert the hand into 7 distinct pairs (requires breaking the two triplets)	Two 5 Characters (keep only one) and Two 6 Bamboos (keep only one)	Two 5 Characters, Two 6 Bamboos, plus a matching tile for the North Wind or Red Dragon to make the seventh pair	– Seven‑Pairs +2 fan (standard) <br> – Self‑draw +1 fan (if you draw the needed tile) <br> – Valid bonus tile +1 fan	Minimum 4 (but needs 4 specific tiles, very unlikely)
*Scoring uses the elements you listed plus the common “self‑draw” (+1 fan) and the one valid bonus tile you already hold (+1 fan).
If you win on a discard (calling a tile from another player) you do not get the self‑draw fan.

3. RECOMMENDATION

Go with Option A (or B).

Why it’s the best:

Only one specific tile is needed – a 6 Dots. The probability of drawing that tile from the wall or claiming it from another player is the highest among all options.
It requires discarding a single useless honor (North Wind or Red Dragon), which does not affect the rest of your hand.
The completed hand is legal, closed (you keep all your own tiles), and already gives you 2 fan (self‑draw + bonus), comfortably above the minimum of 1.
It avoids the long‑shot requirements of Options C, D, or E (multiple draws, breaking existing sets, or chasing rare patterns).
What to do right now:

Discard the North Wind (or Red Dragon if you prefer).
If you draw a 6 Dots on your turn, you can declare self‑draw win.
If another player discards a 6 Dots, you can pon it (calling the tile) and then win on that turn as well.
Following this path
'''

# 6. Known Limitations
The application has sometimes only printed halfway and stop. (Token Limit)
If you set the minimum points very high, you may get results that don't make any sense. 
Some bonus may not be included, an example is since I never say its the start of the game, heavenly hand and earthly hand bonus is not recognised by the AI.


# 7. Future Improvements
If I could extend the project I would like to include discarded/revealed tiles so that the AI can check if the options are possible with the remaining tiles.
If have even more time I would like to include the other players discards and revealed tiles to see if the AI can predict what they have/don't have in their hands or what they are looking for.
