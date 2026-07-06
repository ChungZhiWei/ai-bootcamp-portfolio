from mem0 import Memory

MODEL = "gemma4:e2b"
OLLAMA = "http://localhost:11434" 

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "path": "./chroma_db"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": OLLAMA
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": MODEL,
            "ollama_base_url": OLLAMA
        }
    }
}

m = Memory.from_config(config)
m.delete_all(user_id="user")

def add(user_input, userID):
    m.add(user_input, user_id=userID, infer=False)

def search(user_input, user_id):
    return m.search(query=user_input, filters={"user_id":user_id})

if __name__ == "__main__":
    add("My name is Alex and I study at DigiPen.", "student1")
    print(search("What is my name?", "student1"))