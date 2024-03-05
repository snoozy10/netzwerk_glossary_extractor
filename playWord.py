import gtts
from io import BytesIO
from pygame import mixer
import time


def play_word_de(word_de):
    tts = gtts.gTTS(word_de, lang="de")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)

    mixer.init()
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp, "mp3")
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(0.5)
