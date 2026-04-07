import speech_recognition as sr
import webbrowser
import pyttsx3
from musicLibrary import music
import requests
from openai import OpenAI
import os

# Initialize speech recognition and text-to-speech engine
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Adjust sensitivity
recognizer.pause_threshold = 0.5   # Reduce pause detection time
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech with a male voice and slower speed."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for voice in voices:
        if "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 130)
    engine.say(text)
    engine.runAndWait()

def aiProcess(command):
    """Send user command to OpenAI API and return response."""
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named Jarvis, skilled in general tasks. Give short responses."},
            {"role": "user", "content": command}
        ]
    )

    return completion.choices[0].message.content

def processCommand(command):
    """Process user commands and execute corresponding actions."""
    command = command.lower()
    print(f"Command received: {command}")

    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    
    elif "open linkedin" in command:
        speak("Opening linkedin")
        webbrowser.open("https://www.linkedin.com")

    elif "search" in command:
        query = command.replace("search", "").strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif command.startswith("play"):
        song_name = command.replace("play", "").strip()
        song_library = {key.lower(): value for key, value in music.items()}

        if song_name.lower() in song_library:
            speak(f"Playing {song_name}")
            webbrowser.open(song_library[song_name.lower()])
        else:
            available_songs = ", ".join(music.keys())
            speak(f"Sorry, I couldn't find that song. Try one of these: {available_songs}")

    elif "news" in command:
        """Fetch and read top news headlines."""
        API_KEY = os.getenv("NEWS_API_KEY")
        URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

        try:
            response = requests.get(URL)
            data = response.json()

            if data["status"] == "ok":
                articles = data["articles"]
                speak("Top headlines are:")
                for i, article in enumerate(articles[:5], 1):
                    print(f"{i}. {article['title']}")
                    speak(f"{i}. {article['title']}")
                    print(f"   {article['url']}\n")
            else:
                print("Error fetching news:", data["message"])
        except Exception as e:
            print("Failed to fetch news:", e)

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()

    else:
        """Handle general queries using AI."""
        ans = aiProcess(command)
        speak(ans)

def listen_for_wake_word():
    """Continuously listen for 'Jarvis' and execute commands."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for wake word 'Jarvis'...")

        while True:
            try:
                # Listen for wake word
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=4)
                word = recognizer.recognize_google(audio).lower()

                if "jarvis" in word:
                    speak("Yes?")
                    print("Jarvis activated...")

                    # Listen for command
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
                    command = recognizer.recognize_google(audio)

                    if command:
                        processCommand(command)

            except sr.UnknownValueError:
                print("Could not understand audio. Listening again...")
            except sr.RequestError:
                print("Could not request results. Check internet connection.")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    speak("Initializing Jarvis...")
    listen_for_wake_word()


    
