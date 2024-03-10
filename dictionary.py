import math
import os
import random
import fitz  # install package PyMuPDF
from tqdm import tqdm  # install package tqdm
import pandas as pd


class Dictionary:
    def __init__(self, target_font=8.5, filename_wo_ext="B1-Glossary", starting_page=3, margin=0.1, left_offset=0.045):
        assert target_font > 0, "Font-size cannot be negative"
        assert filename_wo_ext.strip() != "", "Filename cannot be empty"
        assert starting_page >= 0, "Invalid starting page"
        assert 0 <= margin < 0.5, "Invalid margin"
        assert 0 <= left_offset, "Invalid left-offset"

        self.target_font = target_font
        self.filename_wo_ext = filename_wo_ext
        self.starting_page = starting_page
        self.margin = margin
        self.left_offset = left_offset
        self.dict_list = []
        self.populate_dict_from_csv()

    # simple one-level parentheses balance checker
    @staticmethod
    def has_open_parentheses(s):
        if s.rfind("(") > s.rfind(")"):
            return True
        return False

    # if the line starts with a parentheses, it belongs with previous line
    @staticmethod
    def starts_with_parentheses(s):
        if s.find("(") == 0:
            return True
        return False

    @staticmethod
    def combine_lines(self, de_lines, en_lines):
        # combining next-entry to entry if entry is incomplete
        ind = 0
        while ind < len(de_lines) - 1:
            # if either entries have open parentheses, or is an empty entry, combine with next
            if (self.has_open_parentheses(de_lines[ind]) or self.has_open_parentheses(en_lines[ind])
                    or de_lines[ind].strip() == "" or en_lines[ind].strip() == "" or self.starts_with_parentheses(
                        de_lines[ind])
                    or self.starts_with_parentheses(en_lines[ind])):
                de_lines[ind] += " " + de_lines[ind + 1]
                en_lines[ind] += " " + en_lines[ind + 1]
                de_lines.pop(ind + 1)  # remove combined German entry
                en_lines.pop(ind + 1)  # remove combined English entry
                # do not increment index. check again if parentheses was closed
            else:
                # if combination not required, move on to next entry
                ind += 1
        return de_lines, en_lines

    def populate_dict_from_lists(self, de_lines, en_lines):
        # create a list of dictionary items
        # de-en instead of key:value for future option to add native support
        for i in range(len(de_lines)):
            dict_item = {
                "de": de_lines[i].strip(),
                "en": en_lines[i].strip(),
            }
            self.dict_list.append(dict_item)
        print(f"Dictionary items including duplicates: {len(self.dict_list)}")

    def remove_duplicates(self):
        # removing duplicates
        self.dict_list = [dict_item for ind, dict_item in enumerate(self.dict_list) if
                          dict_item not in self.dict_list[:ind]]
        print("Dictionary creation completed! Final count: ", len(self.dict_list))

    def populate_dict_by_extraction(self):
        if not os.path.isfile(self.filename_wo_ext + ".pdf"):
            print("Invalid PDF name. Check path")
        else:
            de_lines = []
            en_lines = []
            filename_pdf = self.filename_wo_ext + ".pdf"
            with fitz.open(filename_pdf) as doc:
                iter_count = 0
                for i in tqdm(range(self.starting_page, doc.page_count)):  # add tqdm for progress bar
                    page = doc[i]
                    # bounding box details for each reading region. for PyMuPDF, (0, 0) is top left
                    origin_x = page.rect.width * (self.margin + self.left_offset)  # offset to cut off annotations
                    origin_y = page.rect.height * self.margin
                    bottom_right_x = page.rect.width * (1 - self.margin)
                    bottom_right_y = page.rect.height * (1 - self.margin)

                    # tracking middle of page to separate German and English entries
                    page_mid_x = origin_x + (bottom_right_x - origin_x) / 2
                    whole_rect = fitz.Rect(origin_x, origin_y, bottom_right_x, bottom_right_y)
                    current_clip_rect = whole_rect

                    # reading blocks detected and converted to dictionary by PyMuPDF
                    # done to be able to read fonts
                    # reference: https://pymupdf.readthedocs.io/en/latest/recipes-text.html
                    blocks = page.get_text("dict", flags=11, clip=whole_rect)["blocks"]
                    for block in blocks:  # iterate through the text blocks
                        for line in block["lines"]:  # iterate through the consecutive texts detected
                            iter_count += 1
                            if line["spans"][0]["size"] > self.target_font:
                                # if the size of the text is greater than 8.5 (dictionary
                                # entry font), skip the entire line
                                continue
                            x0, y0, x1, y1 = line["bbox"]  # else, get next bounding box details
                            if math.floor(current_clip_rect[1]) >= math.floor(y0):  # if trying to read the same line
                                # again, skip
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

            # combining next-entry to entry if entry is incomplete
            de_lines, en_lines = self.combine_lines(self, de_lines, en_lines)
            self.populate_dict_from_lists(de_lines, en_lines)
            self.remove_duplicates()
            self.save_to_csv()

    def save_to_csv(self):
        print("Saving extracted entries to csv...")
        dict_dframe = pd.DataFrame(self.dict_list)
        dict_dframe.to_csv(self.filename_wo_ext + ".csv", index=False)

    def populate_dict_from_csv(self):
        filepath = self.filename_wo_ext + ".csv"
        if not os.path.isfile(filepath):
            self.populate_dict_by_extraction()
        else:
            dataframe = pd.read_csv(filepath)
            self.dict_list = dataframe.to_dict('records')

    def get_random_word(self):
        if self.dict_list is None or len(self.dict_list) == 0:
            print("Cannot fetch word. Dictionary is empty")
        return random.choice(self.dict_list)
