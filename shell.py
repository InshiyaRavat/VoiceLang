import voiceLang
import speech_recognition as sr
import time

# Initialize the recognizer
recognizer = sr.Recognizer()
print("Here's a command guide that will help you test VoiceLang\n\tCOMMAND\t\t\t\t\t\tACTION\t\n     one plus two\t\t\t\t\t 1+2\n     one minus two\t\t\t\t\t 1-2\n     one [into | multiply | multiply by] two\t\t 1x2\n     one divide by two\t\t\t\t\t 1/2\n     open close\t\t\t\t\t\t ()\n     open one plus two close\t\t\t\t (1+2)\n\t[similarly you can do for all other arithematic operations]\n     open one multiply two close divide by three\t (1x2)/3\n\nNOTE: use 'multiply' and 'divide' as command while dealing with parenthesis")
#into recognized as multiply
word_to_symbol = {
    "open" : "(",
    "close" : ")",
    "multiply" : "x",
    "divide" : "/"
}
time.sleep(10)
print("read? let's go!")
while True:
    try:
        # Capture audio from the microphone
        with sr.Microphone() as source:
            print("VoiceLang (say something)>")
            audio = recognizer.listen(source)
        # Recognize speech using Google Speech Recognition
        command = recognizer.recognize_google(audio).lower()
        for word, symbol in word_to_symbol.items():
            command = command.replace(word, symbol)
        print("You said:", command)
        result ,error = voiceLang.run('<stdin>', command)
        if "exit" in command:
            print("Exiting Voicelang.")
            break
        if(error):
            print(error.as_string())
        else:
            print(result)   
    
    except sr.UnknownValueError:
        print("Error: Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")