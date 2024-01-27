# python3.9
from flask import Flask,render_template,request
import pyttsx3
import openai
import threading
import speech_recognition as sr

openai.api_key = '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'
spoken_response_lock = threading.Lock()


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


# text to speech
def speak_text(text):
    engine = pyttsx3.init()
    # rate = engine.getProperty('rate')
    # print(rate)
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()


#text generation wrt the question from the user
def custom_bot(user_message):
    max_tokens=50
    prompt=f"explain {user_message} in {max_tokens} words "

    response = openai.Completion.create(
        engine='gpt-3.5-turbo-instruct',
        prompt=prompt,
        max_tokens=max_tokens
    )
    

    bot_message = response['choices'][0]['text'].strip()

    return bot_message


# speech to text 
def speak_response():
    global spoken_response
    with spoken_response_lock:
        if spoken_response:
            speak_text(spoken_response)


# user input - bot response - text and speech 
@app.route('/get')
def get_response():
    user_input = request.args.get('msg')
    bot_response = custom_bot(user_input)
    #  Store spoken response state
    global spoken_response
    with spoken_response_lock:
        spoken_response = bot_response

        # Thread to speak the response after it's stored
    threading.Thread(target=speak_response).start()

    return bot_response



@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    

    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)

        text = r.recognize_google(audio).lower()
        return text 
        

if __name__ == "__main__":
    app.run()