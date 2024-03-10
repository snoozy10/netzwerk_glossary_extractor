from tkinter import *
import tkinter as tk
import random

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.minsize(width=350, height=250)
        self.root.title("Flashcard App")
        self.cards = [
            {"question": "What is the capital of France? aksdfkjashdfkjj alksdjf lasdhjf alsdkfjalskdf laskfj lasfdjasdlfj", "answer": "Paris"},
            {"question": "What is 2 + 2?", "answer": "4"},
            # Add more flashcards here
        ]

        self.question_label = tk.Label(root, font=("Arial", 16), wraplength=300)
        self.question_label.pack(pady=20)

        self.answer_button = Button(root, text="Show Answer", relief=FLAT, command=self.show_answer)
        self.answer_button.pack(pady=10, side=BOTTOM)

        self.next_button = Button(root, text="Next Card", relief=FLAT, command=self.show_next_card)
        self.next_button.pack(pady=10, side=BOTTOM)

        self.current_card = None
        self.show_next_card()

    def show_next_card(self):
        self.current_card = random.choice(self.cards)
        self.question_label.config(text=self.current_card["question"])
        self.answer_button.config(state=tk.NORMAL)

    def show_answer(self):
        self.question_label.config(text=f"Answer: {self.current_card['answer']}")
        self.answer_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
