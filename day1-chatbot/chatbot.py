from test_model import response 
from memory_setup import add, search


def get_response(user_input):
    ##user_input = user_input.lower().strip()

    result = ""

    relevant_memories = search(user_input, "user")
    if relevant_memories:
        memory_context = "Relevant facts about the user:\n"
        for mem in relevant_memories['results']:
            memory_context += f"- {mem['memory']}\n"
        memory_context += "User query:\n" + user_input
        result = response(memory_context)
    else:
        result = response(user_input)
    
    add(user_input, "user")
    return result

def start_chat():
    print("Chatbot ready. Type quit to exit.")
    
    # Core loop
    while True:
        try:
            # Capture user input
            user_input = input("You: ")
            
            # Check for termination keywords
            if user_input.lower().strip() in ["exit", "quit"]:
                print("Closing Chatbot.")
                break
                
            # Process and display response
            response = get_response(user_input)
            print(f"Chatbot: {response}")
            
        except (KeyboardInterrupt, EOFError):
            print("\n" + EOFError)
            break

if __name__ == "__main__":
    start_chat()