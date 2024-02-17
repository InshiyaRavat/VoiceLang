import voiceLang

while True:
    text=input("VoiceLang > ")
    result ,error = voiceLang.run('<stdin>', text)

    if(error):
        print(error.as_string())
    else:
        print(result)   