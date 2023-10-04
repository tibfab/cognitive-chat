# Implements the wrappers for the speech APIs.

import sys
import azure.cognitiveservices.speech as speechsdk
import openai

# replace <placeholders> with service access details
# like endpoint key and region
speech_config = speechsdk.SpeechConfig(subscription='<service endpoint key>',
                                       region='<service region>')
speech_config.speech_recognition_language="en-US"
speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
openai.api_key = '<open_ai api key>'

def pretty_print(text1, text2):
    # format print to properly output the conversation
    print(f'\n{text1}>> {text2}')
    
def recognize_from_microphone():
    # transcribes the audio recorded from the microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print('\nSpeak into your microphone.')
    speech_recognition_result = speech_recognizer.recognize_once()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pretty_print('QUESTION', speech_recognition_result.text)
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(f'No match: {speech_recognition_result.no_match_details}')
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print(f'Recognition canceled: {cancellation_details.reason}')
    
    return 'No input'


def get_answer_from_chat_gpt(question):
    # fetches answers form ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'Your name is Aurora.'},
                {'role': 'system', 'content': 'You are a friendly chatbot.'},
                {'role': 'system', 'content': 'Give short answers please.'},
                {'role': 'user', 'content': question}
            ]
        )
        answer = response['choices'][0]['message']['content']
        pretty_print('ANSWER', answer)
        return answer
    except openai.error.RateLimitError:
        message = 'Rate limit reached.  Please try again in 20 seconds.'
        pretty_print('ANSWER', answer)
        return message
    except Exception as error:
        print('An exception occurred:', error)

def synthesize_text_to_speech(text, run_async=False):
    # synthesizes the answer to speech
    # uses the voice as configured at the top
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    if run_async:
        speech_synthesis_result = speech_synthesizer.speak_text_async(text)
    else:    
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print('')
            #print(f'Text synthesized [{text}]')
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print(f'Synthesis canceled: {cancellation_details.reason}')


if __name__ == '__main__':  
    # loop until ctrl-c        
    while True:
        try:
            question = recognize_from_microphone()
            if question is not None:
                answer = get_answer_from_chat_gpt(question)
                synthesize_text_to_speech(answer)
        except KeyboardInterrupt:
            sys.exit()