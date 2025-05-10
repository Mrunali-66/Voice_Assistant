from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieve specific environment variables
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

#Initilize groq client 
client = Groq(api_key=GroqAPIKey)

# Initilize empty list
message = []

# Define a function to add a new event to the memory view
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""


SystemChatBot = [
    {"role": "system", "content" : System}
]

# Attempt to load chat log
try:
    with open(r"Data/Chatlog.json", "r") as f:
        message = load(f)

except FileNotFoundError:
    with open(r"Data/Chatlog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Today is {day},\n Date: {date},\n Month: {month},\n Year: {year}.\n"
    data += f"Current time is {hour}:{minute}:{second}."
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]  # Changed 'not' to keep non-empty lines
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    #This function sends the user's query to chatbot's server and returns AI's response.
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": f"{Query}"})
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content":RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,
            stop=None
        )
        Answer=""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role":"assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f,indent=4)

        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        print("Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
        
