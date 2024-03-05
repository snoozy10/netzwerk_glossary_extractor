import math
import os
import random
from pathlib import Path

import fitz  # install package PyMuPDF
from tqdm import tqdm  # install package tqdm
import pandas as pd

import playWord

''' CONSTANTS '''
FONT_SIZE = 8.5  # font-size of dictionary entries
MARGIN_MULT = 0.1  # margin offset fraction to page
LEFT_OFFSET = 0.045  # offsetting to cut off irrelevant annotations (e.g. exercise number)
PAGE_START = 3  # skipping title page, info page
PDF_PATH_STR = "B1-Glossary.pdf"  # file in same directory as main.py
FILE_NAME = Path(PDF_PATH_STR).stem


def extract_words():
    if os.path.isfile(PDF_PATH_STR):
        de_lines = []  # German entries from beginning to end of doc, read as rows
        en_lines = []  # English entries from beginning to end of doc, read as rows
        dictionary = []
        ''' PyMuPDF begins '''
        with fitz.open(PDF_PATH_STR) as doc:
            iter_count = 0
            for i in tqdm(range(PAGE_START, doc.page_count)):  # add tqdm for progress bar
                page = doc[i]
                # bounding box details for each reading region. for PyMuPDF, (0, 0) is top left
                origin_x = page.rect.width * (MARGIN_MULT + LEFT_OFFSET)  # offset to cut off annotations
                origin_y = page.rect.height * MARGIN_MULT
                bottom_right_x = page.rect.width * (1 - MARGIN_MULT)
                bottom_right_y = page.rect.height * (1 - MARGIN_MULT)

                # tracking middle of page to separate German and English entries
                page_mid_x = origin_x + (bottom_right_x - origin_x) / 2
                whole_rect = fitz.Rect(origin_x, origin_y, bottom_right_x, bottom_right_y)
                current_clip_rect = whole_rect

                # reading blocks detected and converted to dictionary by PyMuPDF
                # done to be able to read fonts
                # reference: https://pymupdf.readthedocs.io/en/latest/recipes-text.html
                blocks = page.get_text("dict", flags=11, clip=whole_rect)["blocks"]
                for b in blocks:  # iterate through the text blocks
                    for l in b["lines"]:  # iterate through the consecutive texts detected
                        iter_count += 1
                        if l["spans"][0]["size"] > FONT_SIZE:
                            # if the size of the text is greater than 8.5 (dictionary
                            # entry font), skip the entire line
                            continue
                        x0, y0, x1, y1 = l["bbox"]  # else, get next bounding box details
                        if math.floor(current_clip_rect[1]) >= math.floor(y0):  # if trying to read the same line again, skip
                            continue
                        # update bounding box for clipping
                        current_clip_rect[1] = y0
                        current_clip_rect[3] = y1
                        my_line = page.get_text("words", clip=current_clip_rect)
                        germ_words = [word[4] for word in my_line if word[0] < page_mid_x]
                        eng_words = [word[4] for word in my_line if word[0] > page_mid_x]

                        germ_line = " ".join(germ_words)
                        eng_line = " ".join(eng_words)
                        de_lines.append(germ_line)
                        en_lines.append(eng_line)
                assert len(de_lines) == len(en_lines), "Extraction Error: Unequal entries. Mapping not possible"
            print(f"Inner loop entered {iter_count} times")


        # simple one-level parentheses balance checker
        def has_open_parentheses(s):
            if s.rfind("(") > s.rfind(")"):
                return True
            return False


        # combining next-entry to entry if entry is incomplete
        ind = 0
        while ind < len(de_lines)-1:
            # if either entries have open parentheses, or an empty entry, combine
            if has_open_parentheses(de_lines[ind]) or has_open_parentheses(en_lines[ind]) or de_lines[ind].strip() == "" or en_lines[ind].strip() == "":
                de_lines[ind] += " " + de_lines[ind + 1]
                en_lines[ind] += " " + en_lines[ind + 1]
                de_lines.pop(ind + 1)  # remove combined German entry
                en_lines.pop(ind + 1)  # remove combined English entry
                # do not increment index. check again if parentheses was closed
            else:
                # if combination not required, move on to next entry
                ind += 1

        # create a list of dictionary items
        # de-en instead of key:value for future option to add native support
        for i in range(len(de_lines)):
            dict_item = {
                "de": de_lines[i].strip(),
                "en": en_lines[i].strip(),
            }
            dictionary.append(dict_item)

        print(f"Dictionary items including duplicates: {len(dictionary)}")
        # removing duplicates
        # reference: https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        dictionary = [dict(t) for t in {tuple(d.items()) for d in dictionary}]
        print("Dictionary creation completed! Final count: ", len(dictionary))
        print("Saving extracted text to csv...")
        dict_dframe = pd.DataFrame(dictionary)
        dict_dframe.to_csv(FILE_NAME + ".csv")

    else:
        print("File not found. Check file path")


def get_dict_from_csv():
    dataframe = get_dframe_from_csv()
    return dataframe.to_dict('records')


def get_dframe_from_csv():
    filepath = FILE_NAME + ".csv"
    if not os.path.isfile(filepath):
        extract_words()
    dataframe = pd.read_csv(filepath)
    return dataframe


def print_all():
    dictionary = get_dict_from_csv()
    for index, entry in enumerate(dictionary):
        print(f"{index + 1} |  {entry["de"]} :: {entry["en"]}")


def play_random_word():
    dictionary = get_dict_from_csv()
    word = random.choice(dictionary)
    print(word)
    playWord.play_word_de(word["de"])


play_random_word()

'''
POSSIBLE IMPROVEMENTS:
- check file path. create absolute path if seen fit
- check how inner loop entry can be reduced
- convert each item into tuple instead of maintaining two separate lists
- ^this will create more compact code. current version for better readability
'''
