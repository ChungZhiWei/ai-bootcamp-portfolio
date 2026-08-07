# 1. Project Title and Description

This project name is called Mahjong Hand Analyzer.  
It helps analyze your mahjong hand and gives options on what to aim for.  
It is for people who cannot figure out what to do with their hand.

# 2. Problem Statement

As mahjong is a simple game that can get very complicated, it can be hard to see if your hand is able to win.  
Even if your hand meets basic win conditions, but because of special rules/minimum points, it is not considered a win yet.  
This app would help you check if your hand is able to win and even if the hand is not a win, this app would give you advice on which path to take to make your hand a winning hand.

# 3. Technology Stack

- Python
- pythondotenv
- streamlit
- Groq REST API

# 4. Setup Instructions

Follow these instructions to set up a copy of the project on your local machine.

1. Download app.py, mahjong_chatbot.py, prompts.py, .env.example and requirements.txt.
2. Create a folder and put these 5 files inside.![Model](images/files%20in%20folder.png)  
3. Open .env.example and fill the API key. (replace "InsertKeyHere" with your groq API Key)
4. Change ".env.example" name to ".env".![Model](images/change%20env%20file.png)  
5. Open command prompt and navigate to the folder with these 5 files inside.
6. Create a python environment and activate it. In command prompt, run (python -m venv .venv) and (.venv\Scripts\activate).
7. Install python requirements.txt. In command prompt, run (pip install -r requirements.txt)![Model](images/go%20to%20folder%20and%20create%20env.png)  
8. Run the application. In command prompt, run (streamlit run app.py)![Model](images/run%20app.png)

# 5. Usage Examples

You will need to set the mahjong rules at the side bar. Set them as necessary.![Model](images/Sidebar%20Settings.png)  
After that on the main screen, You will need to key in how many of that tile you have in the box.  
There are many boxes with the tile associated with the box displayed above the box.  
Example if I have 3 3 bamboos, I need to find the box with 3 bamboos above it and key in 3.![Model](images/Key%20in%20tiles.png)  
After keying in your hand, You need to check if you have any flower/season/bonus tiles.  
In "Total number of bonus tiles held", key in the total number of flower/season/bonus tiles you have.  
In "Total number of valid bonus tiles held", key in the total number of flower/season/bonus tiles that would give you points.![Model](images/Key%20in%20bonus%20tiles.png)    
After that you can look below and see if your current hand is displayed correctly and your hand and bonus tiles are correct.![Model](images/Check%20Summary.png)  
Once the information is correct you can hit "Analyze Hand" button.  

# 6. Known Limitations
The application has sometimes only printed halfway and stop. (Token Limit)  
If you set the minimum points very high, you may get results that don't make any sense.   
Some bonus may not be included, an example is since I never say its the start of the game, heavenly hand and earthly hand bonus is not recognised by the AI. 

# 7. Future Improvements
If I could extend the project I would like to include discarded/revealed tiles so that the AI can check if the options are possible with the remaining tiles.  
If have even more time I would like to include the other players discards and revealed tiles to see if the AI can predict what they have/don't have in their hands or what they are looking for.
