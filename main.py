import playWord

from dictionary import Dictionary

dictionary = Dictionary(filename_wo_ext="B1-Glossary")
word = dictionary.get_random_word()
print(f"{word["de"]} :: {word["en"]}")
playWord.play_word(word, "de")
playWord.play_word(word, "en")

'''
POSSIBLE IMPROVEMENTS:
- Work more with file path. create absolute path if seen fit
- Reduce inner loop entries
'''
