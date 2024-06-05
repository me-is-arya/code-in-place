import pyttsx3
import speech_recognition as sr
import wikipedia
from fuzzywuzzy import fuzz
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
import os

class Chatbot:
    def __init__(self):
        self.engine = pyttsx3.init("sapi5")
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 150)
        self.recognizer = sr.Recognizer()

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def take_command(self):
        with sr.Microphone() as source:
            self.recognizer.pause_threshold = 2
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=4)
            try:
                query = self.recognizer.recognize_google(audio, language='en-in')
                return query
            except Exception as e:
                return "None"

    def clean_summary(self, summary):
        cleaned_summary = summary.replace('== Content ==', '')
        return cleaned_summary

    def search_answers(self, question):
        try:
            with open('questions.txt', 'r') as q_file, open('answers.txt', 'r') as a_file:
                questions = q_file.readlines()
                answers = a_file.readlines()
                highest_match = -1
                best_answer = None
                for i, q in enumerate(questions):
                    similarity = fuzz.ratio(question.strip().lower(), q.strip().lower())
                    if similarity > highest_match:
                        highest_match = similarity
                        best_answer = answers[i].strip()

                if highest_match >= 75:
                    return best_answer

            return None
        except FileNotFoundError:
            return None

    def chatbot_response(self, user_input):
        response = ""

        if user_input == "text":
            response = "You are now in text mode. How can I assist you? /n"
        elif user_input == "voice":
            response = "Voice mode activated. Listening... /n"
        else:
            answer = self.search_answers(user_input)
            if answer:
                response = answer
            else:
                try:
                    result = wikipedia.summary(user_input, sentences=2)
                    cleaned_result = self.clean_summary(result)
                    response = f"{cleaned_result}\n\nWikipedia Link: {wikipedia.page(user_input).url}"
                except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                    response = "I couldn't find an answer. Can you please rephrase your question?"

        return response

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot GUI")
        self.chatbot = Chatbot()
        self.voice_thread = None 
        def clearHistory():
            f = open('history.txt', 'w')
            f.write('')
            f.close()
        self.greeting_label = ttk.Label(root, text="AURA", font=("Helvetica", 16))
        self.greeting_label.pack()
        self.text_mode_button = ttk.Button(root, text="Text Mode", command=lambda: self.chatbot_response("text"))
        self.text_mode_button.pack()      
        self.voice_mode_button = ttk.Button(root, text="Voice Mode", command=lambda: self.start_voice_mode())
        self.voice_mode_button.pack()     
        self.history_mode_button= ttk.Button(root,text="History", command=lambda: os.startfile('history.txt') )
        self.history_mode_button.pack()
        self.history_mode_button= ttk.Button(root,text="Clear History", command=lambda: clearHistory() )
        self.history_mode_button.pack()
        self.response_text = ScrolledText(root, wrap=tk.WORD, height=20, width=50, font=("Helvetica", 14))
        self.response_text.pack()        
        self.user_input_entry = ttk.Entry(root, width=50, font=("Helvetica", 14))
        self.user_input_entry.pack()

        
    
        self.send_button = ttk.Button(root, text="Send", command=self.send_user_input)
        self.send_button.pack()        
        self.exit_button = ttk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack()

    def start_voice_mode(self):
        self.voice_thread = threading.Thread(target=self.listen_and_respond)
        self.voice_thread.start()
    def start_history(self):
        ('history.txt')


    def listen_and_respond(self):
        self.response_text.insert(tk.END, "Chatbot: Voice mode activated. Listening...\n")
        self.response_text.see(tk.END)

        with sr.Microphone() as source:
            listening = True  
            while listening:
                self.chatbot.speak("Listening...")
                self.chatbot.recognizer.pause_threshold = 3
                self.chatbot.recognizer.adjust_for_ambient_noise(source)
                audio = self.chatbot.recognizer.listen(source, timeout=5)
                try:
                    query = self.chatbot.recognizer.recognize_google(audio, language='en-in')
                    response = self.chatbot.chatbot_response(query)
                    self.response_text.insert(tk.END, f"User (voice): {query}\n")
                    self.response_text.insert(tk.END, "\n")  
                    self.response_text.insert(tk.END, f"Chatbot: {response}\n")
                    self.response_text.insert(tk.END, "\n")  
                    self.response_text.see(tk.END)
                    f = open('history.txt', 'a')
                    f.write('User: ')
                    f.write(query)
                    f.write('\n')
                    f.write('Chatbot: ')
                    f.write(response)
                    f.write('\n')
                    f.write('\n\n')
                    f.close()
                except Exception as e:
                    self.response_text.insert(tk.END, "Chatbot: Say that again, please.\n")
                    self.response_text.insert(tk.END, "\n")

            
                if query.lower() == "exit":
                    listening = False 

    def send_user_input(self):
        user_input = self.user_input_entry.get()
        self.user_input_entry.delete(0, tk.END)
        self.response_text.insert(tk.END, f"User: {user_input}\n")
        self.response_text.insert(tk.END, "\n")  
        response = self.chatbot.chatbot_response(user_input)
        self.response_text.insert(tk.END, f"Chatbot: {response}\n")
        self.response_text.insert(tk.END, "\n")  
        self.response_text.see(tk.END)
        f = open('history.txt', 'a')
        f.write('User: ')
        f.write(user_input)
        f.write('\n')
        f.write('Chatbot: ')
        f.write(response)
        f.write('\n')
        f.write('\n\n')
        f.close()

    def chatbot_response(self, user_input):
        response = self.chatbot.chatbot_response(user_input)
        self.response_text.insert(tk.END, f"Chatbot: {response}\n")
        self.response_text.see(tk.END)

def main():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
