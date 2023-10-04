# Implements a Flask web demo
# by the use of the wrappers defined in chat_wrapper.py.

from flask import Flask, render_template, request
import chat_wrapper
import time


# instantiate the Flask application 
app = Flask(__name__)

# define the routes to map
# browser requests to the appropriate speech API calls
@app.route('/')
def start():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template('waiting.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    recognized = chat_wrapper.recognize_from_microphone()
    print(f'Recognized: {recognized}')
    return recognized

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    answer = chat_wrapper.get_answer_from_chat_gpt(data['question'])
    chat_wrapper.synthesize_text_to_speech(answer, run_async=True) # need a none blocking response here
    time.sleep(0.5)
    return answer


if __name__ == '__main__':
    app.run(debug=True)