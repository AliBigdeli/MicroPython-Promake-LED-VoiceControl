# -*- coding: utf-8 -*-
# author: Ali Bigdeli
# email: bigdeli@gmail.com

# importing all libraries needed for sound detection and keyboard control
import speech_recognition as sr
from pynput import keyboard
from pynput.keyboard import Key, Controller
import paho.mqtt.publish as publish

'''
if you dont know the index of your microphone use this code
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(
        index, name))
'''

# creating a class for key combination and execution by speechrecognition

class Recognizer():
    commands_list = {
        'روشن':'on',
        'خاموش':'off',
        'آبی':'blue',
        'سبز':'green',
        'قرمز':'red',
        'نارنجی':'orange',
        'زرد':'yellow'
    }
    
    
    # combinations were needed to call the STT module
    COMBINATIONS = [
        {keyboard.Key.alt_l, keyboard.KeyCode(char='`')},
        {keyboard.Key.alt_l, keyboard.KeyCode(char='~')},
        {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode(192)}
    ]

    # initializing needed objects and variables
    def __init__(self, language="fa-IR"):
        self.current = set()
        self.k = Controller()
        self.r = sr.Recognizer()
        self.language = language

    # if the key combinations declared on top was hit it will be executing self.execute function
    def on_press(self, key):
        # print(key)
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.add(key)
            if any(all(k in self.current for k in COMBO) for COMBO in self.COMBINATIONS):
                self.execute()
                self.current.remove(key)

    # after releasing the keys the holder buffer will be empty again
    def on_release(self, key):
        try:
            self.current.remove(key)
        except KeyError:
            pass

    # executer of the functions i desire such as voice recognizer
    def execute(self):
        text = self.voice_rec()
        # if text == None or text == '':
        #     return
        if text in self.commands_list:
            self.send_msg(self.commands_list[text])
        else:
            return None

    # voice recognition function based on microphone
    def voice_rec(self):
        print("say something...")

        # switing to default laptop microphone in your case use the code in sr.Microphone(0) index
        with sr.Microphone(0) as source:
            # creating file object out of incoming sounds till it stops
            audio = self.r.listen(source)

        try:
            # trying to comunicate with google stt engine to get the data
            text = self.r.recognize_google(audio, language=self.language)
            text = str(text)
            print("You said: " + text)
            return text

        # handeling all exceptions type
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(
                "Could not rquest results from Google Speech Recognition service; {0}".format(e))
            return None

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    def send_msg(self,payload):
        publish.single("promake/led/test", payload,hostname="test.mosquitto.org", port=1883)

if __name__ == '__main__':
    # https://cloud.google.com/speech-to-text/docs/language
    stt = Recognizer(language="fa-IR")
    stt.run()
