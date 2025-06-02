import requests
import json
import datetime
import time
import os
import tkinter as tk
from tkinter import *
from datetime import datetime
from dotenv import load_dotenv

def convertTime(timeStr):
    dt = datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%m/%d/%y - %I:%M%p').lstrip('0').replace(' 0', ' ')

def getWeather(city):
    # Requires openweathermap api key here
    load_dotenv()
    apiKey = os.getenv("API_KEY")
    outStr = ""
    if city == '':
        city = "Philadelphia"
    # Current Weather
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&units=imperial')
        response.raise_for_status()
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = round(data['main']['temp'], 1)
        feelsTemp = round(data['main']['feels_like'], 1)
        hiTemp = round(data['main']['temp_max'], 1)
        loTemp = round(data['main']['temp_min'], 1)
        wind = round(data['wind']['speed'], 1)
        outStr = f"The current weather in {city} is {weather} with a temperature of {temperature}°F\nFeels like {feelsTemp}°F.\n(LO: {loTemp}°F | HI: {hiTemp}°F | Wind: {wind} mph)"
        if 'rain' in data:
            rain = data['rain']['1h']
            outStr = outStr + f"\nRainfall in last hour: Honeybee! {rain} inches of rain in the last hour!"
        else:
            outStr = outStr + f"\nRainfall in last hour: No rain for my honeybee :("
        
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            outStr = f"Sorry, could not find current weather data for {city}."
        else:
            outStr = f"Sorry, an error occurred while fetching the current weather data. Please try again later. Error: "
            outStr = outStr + str(error)
    # Forecast
    try:
        fResponse = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apiKey}&units=imperial')
        fResponse.raise_for_status()
        fData = fResponse.json()

        rainTimes = []
        for item in fData['list']:
            if 'rain' in item.keys():
                timestamp = convertTime(item['dt_txt'])
                rainTimes.append(timestamp)
        
        fStart = convertTime(fData['list'][0]['dt_txt'])
        fEnd = convertTime(fData['list'][-1]['dt_txt'])
        outStr = outStr + f"\n\nNext time(s) its going to rain from {fStart} to {fEnd} in {city}: " 

        if len(rainTimes) == 0:
            outStr = outStr + f"\nNo rain in the forecast yet honeybee :("

        else:
            # display forecast time frame here as well
            for item in rainTimes:
                outStr = outStr + "\n" + item

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            outStr = outStr + f"\nSorry, could not find forecast data for {city}."
        else:
            outStr = outStr + f"\nSorry, an error occurred retrieving forecast data. Error: "
            outStr = outStr + str(error)

    return outStr

def getCategory():
    outStr = ""
    try:
        catResponse = requests.get(f'https://v2.jokeapi.dev/categories?format=json&lang=en')
        catResponse.raise_for_status
        catData = catResponse.json()
        categories = catData['categories']
        outStr = outStr + f"Categories available are "
        for item in categories[:-2]:
            outStr = outStr + item + ", " 
        outStr = outStr[:-1]
    except requests.exceptions.HTTPError as error:
        outStr = "Sorry, an error occured retrieving category. Error: "
        outStr = outStr + str(error)
    
    return outStr

def getJoke(category):
    outStr = ""
    if category == '':
        category = "Any"
    try:
        categoriesStr = getCategory()
        if "Sorry" in categoriesStr: 
            outStr = categoriesStr
            return outStr
        else:
            if category.lower() in categoriesStr.lower():
                jResponse = requests.get(f'https://v2.jokeapi.dev/joke/{category}?format=json&type=single&lang=en')
                jResponse.raise_for_status()
                jData = jResponse.json()
                if jData['error'] == True:
                    outStr = "Sorry, an error occured retrieving joke"
                    return outStr
                joke = jData['joke']
                outStr = outStr + joke
            else:
                outStr = outStr + "This category is not an option :/"
                   
    except requests.exceptions.HTTPError as error:
        outStr = outStr + "Sorry, an error occured retrieving joke. Error: "
        outStr = outStr + str(error)

    return outStr

# GUI 

def weather():
    def get_city():
        city = city_entry.get()
        result = getWeather(city)
        output_text.delete("1.0", END)
        output_text.insert(END, result)
        output_text.tag_configure('center', justify='center')
        output_text.tag_add('center', '1.0', 'end')

    weather_frame = tk.Frame(root, background="#f6da85")
    weather_frame.pack(fill="both", expand=True)

    city_label = tk.Label(weather_frame, text="Enter City:", background="#f6da85")
    city_label.pack(pady=(50,10))

    city_entry = tk.Entry(weather_frame, background="white")
    city_entry.pack(pady=10)

    get_weather_button = tk.Button(weather_frame, text="Get Weather", background="black", foreground="#f6da85", command=get_city)
    get_weather_button.pack(padx=10, pady=10)

    back_button = tk.Button(weather_frame, text="Back", background="black", foreground="#f6da85", command=lambda:[weather_frame.pack_forget(), start()])
    back_button.pack(padx=10, pady=10)

    output_text = Text(weather_frame, wrap=WORD, yscrollcommand=True, background="#f6da85", font=("Arial", 9))
    scrollbar = Scrollbar(weather_frame, command=output_text.yview)
    output_text.configure(yscrollcommand=scrollbar.set)

    output_text.pack(side=LEFT, fill=BOTH, expand=True, pady=10)
    scrollbar.pack(side=RIGHT, fill=Y)
    

def jokes():
    def get_input():
        input_text = input_entry.get()
        output_label.config(text=getJoke(input_text), wraplength=500)

    jokes_frame = tk.Frame(root, background="#f6da85")
    jokes_frame.pack(fill="both", expand=True)

    category_label = tk.Label(jokes_frame, text=getCategory(), background="#f6da85")
    category_label.pack(pady=(50,10))

    input_label = tk.Label(jokes_frame, text="Enter Category:", background="#f6da85")
    input_label.pack(pady=10)

    input_entry = tk.Entry(jokes_frame, background="white")
    input_entry.pack(pady=10)

    get_input_button = tk.Button(jokes_frame, text="Get Joke", background="black", foreground="#f6da85", command=get_input)
    get_input_button.pack(padx=10, pady=10)
    
    back_button = tk.Button(jokes_frame, text="Back", background="black", foreground="#f6da85", command=lambda:[jokes_frame.pack_forget(), start()])
    back_button.pack(padx=10, pady=10)

    output_label = tk.Label(jokes_frame, background="#f6da85")
    output_label.pack(pady=10)
    

def letter(): 
    letter_frame = tk.Frame(root, background="#f6da85")
    letter_frame.pack(fill="both", expand=True)

    back_button = tk.Button(letter_frame, text="Back", background="black", foreground="#f6da85", command=lambda:[letter_frame.pack_forget(), start()])
    back_button.pack(pady=(50,10))

    letter_text = Text(letter_frame, wrap=WORD, yscrollcommand=True, background="#f6da85", font=("Arial", 9))
    scrollbar = Scrollbar(letter_frame, troughcolor="#f6da85", command=letter_text.yview)
    letter_text.configure(yscrollcommand=scrollbar.set)

    letterStr = "Honeybee,\n\nHappy Birthday - Andrew"
    letter_text.insert(END, letterStr)
    letter_text.tag_configure('center', justify='center')
    letter_text.tag_add('center', '1.0', 'end')

    letter_text.pack(side=LEFT, fill=BOTH, expand=True, pady=10)
    scrollbar.pack(side=RIGHT, fill=Y)
    
def manual():
    manual_frame = tk.Frame(root, background="#f6da85")
    manual_frame.pack(fill="both", expand=True)

    back_button = tk.Button(manual_frame, text="Back", background="black", foreground="#f6da85", command=lambda:[manual_frame.pack_forget(), start()])
    back_button.pack(pady=(50,10))

    manual_text = Text(manual_frame, wrap=WORD, yscrollcommand=True, background="#f6da85", font=("Arial", 9))
    scrollbar = Scrollbar(manual_frame, troughcolor="#f6da85", command=manual_text.yview)
    manual_text.configure(yscrollcommand=scrollbar.set)

    manualStr = "Hello Honeybee :)\nThis is just a guide to answer any questions or point you in the right direction.\n\nWeather:\nThis section of the hub allows you to get the current weather and forecast for up to three days.\nThe default is set to Philadelphia, but this can be changed.\nYou can search any city in the entire world.\nFuture rain times are listed in three hour intervals so if there is a gap larger than three hours there is a gap in rainfall.\n\nJokes:\nThis section of the hub allows you to access a library of thousands of jokes.\nThe default category is set to any.\nThe joke library will be updated around the holiday's for themed jokes too.\n\nLetter:\nHBD\n\nExit:\nWorks the same as clicking the 'X' on the window or stopping the program.\n\nDeveloper Notes:\nFor any questions, bugs, feedback, or application addidtions, please contact Andrew Seibert\n\nandrew.seibert@temple.edu | 215-776-4303"
    manual_text.insert(END, manualStr)
    manual_text.tag_configure('center', justify='center')
    manual_text.tag_add('center', '1.0', 'end')

    manual_text.pack(side=LEFT, fill=BOTH, expand=True, pady=10)
    scrollbar.pack(side=RIGHT, fill=Y)

def start():
    start_frame = tk.Frame(root, background="#f6da85")
    start_frame.pack(fill="both", expand=True)

    honeyBeeAscii = "Welcome to the Honeybee Hub!\n   __\n _/__)\n(: \_\_\}-\n   \__)"

    welcome_label = tk.Label(start_frame, text=honeyBeeAscii, font=("bold", 16), background="#f6da85", foreground="black")
    welcome_label.pack(pady=(50,10))

    weather_button = tk.Button(start_frame, text="Weather", background="black", foreground="#f6da85", command=lambda:[start_frame.pack_forget(), weather()])
    weather_button.pack(pady=10)

    jokes_button = tk.Button(start_frame, text="Jokes", background="black", foreground="#f6da85", command=lambda:[start_frame.pack_forget(), jokes()])
    jokes_button.pack(pady=10)

    letter_button = tk.Button(start_frame, text="Letter", background="black", foreground="#f6da85", command=lambda:[start_frame.pack_forget(), letter()])
    letter_button.pack(pady=10)

    manual_button = tk.Button(start_frame, text="Hub Manual", background="black", foreground="#f6da85", command=lambda:[start_frame.pack_forget(), manual()])
    manual_button.pack(pady=10)

    exit_button = tk.Button(start_frame, text="Exit", background="black", foreground="#f6da85", command=root.destroy)
    exit_button.pack(pady=10)

    author_label = tk.Label(start_frame, text="to: Honeybee\nfrom: Andrew", background="#f6da85", foreground="black")
    author_label.pack(pady=10)

root = tk.Tk()
root.attributes('-fullscreen', True)
root.title("HoneyBee Hub")
start()
root.mainloop() 