import requests
from bs4 import BeautifulSoup
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk

def get_first_google_image(query):
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    images = soup.find_all("img")

    if images:
        first_image_link = images[1].get("src")
        return first_image_link
    else:
        return None

def display_image_in_tkinter(image_url):
    root = tk.Tk()

    response = requests.get(image_url)
    img_data = BytesIO(response.content)
    img = Image.open(img_data)
    if img.width > 300:
        img_ratio = img.width / img.height
        img = img.resize((300, round(300*img_ratio)))
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(root, image=img_tk)
    label.pack()

    root.mainloop()


def showWord(word):
    # Example usage
    search_query = word
    first_image_url = get_first_google_image(search_query)

    if first_image_url:
        print(f"First image URL: {first_image_url}")
        display_image_in_tkinter(first_image_url)
    else:
        print("No images found.")
