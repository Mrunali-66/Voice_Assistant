import os
from googlesearch import search
from groq import Groq
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve specific environment variables
Username = os.getenv("Username", "User")
Assistantname = os.getenv("Assistantname", "Assistant")
GroqAPIKey = os.getenv("GroqAPIKey")

# Validate API Key
if not GroqAPIKey:
    raise ValueError("Groq API Key is missing. Please check your .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet. *** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.*** *** Just answer the question from the provided data in a professional way. ***"""

# Ensure Data directory exists
os.makedirs('Data', exist_ok=True)

# Initialize chat log
def initialize_chatlog():
    chatlog_path = 'Data/Chatlog.json'
    if not os.path.exists(chatlog_path):
        with open(chatlog_path, 'w') as f:
            json.dump([], f, indent=4)

# Google Search function
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The results for '{query}' are:\n[start]\n"
        
        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Search error: {str(e)}"

# Remove empty lines
def AnswerModified(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Initial system chat configuration
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "I need some information about the current weather."},
    {"role": "assistant", "content": "Hello, How can I help you?"}
]

# Get current date and time information
def Information():
    current_date_time = datetime.datetime.now()
    data = "Please use this real-time information if needed:\n"
    data += f"Today is {current_date_time.strftime('%A')}\n"
    data += f"Date: {current_date_time.strftime('%d')}\n"
    data += f"Month: {current_date_time.strftime('%B')}\n"
    data += f"Year: {current_date_time.strftime('%Y')}\n"
    data += f"Current time is {current_date_time.strftime('%H:%M:%S')}.\n"
    return data

# Real-time search engine function
def RealtimeSearchEngine(prompt):
    global SystemChatBot

    # Load chat log
    chatlog_path = 'Data/Chatlog.json'
    try:
        with open(chatlog_path, 'r') as f:
            messages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = []

    # Add user prompt
    messages.append({"role": "user", "content": prompt})

    # Perform Google search
    search_results = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_results})

    try:
        # Generate response using Groq
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        # Collect response
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean up answer
        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save chat log
        with open(chatlog_path, 'w') as f:
            json.dump(messages, f, indent=4)

        # Remove temporary search results
        SystemChatBot.pop()

        return AnswerModified(Answer=Answer)

    except Exception as e:
        return f"Error generating response: {str(e)}"

# Main execution
if __name__ == '__main__':
    initialize_chatlog()
    while True:
        try:
            prompt = input("Enter your question: ")
            print(RealtimeSearchEngine(prompt))
        except KeyboardInterrupt:
            print("\nExiting the program.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")