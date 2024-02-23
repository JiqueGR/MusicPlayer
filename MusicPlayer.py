import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import pygame
import os
import random
import requests
from bs4 import BeautifulSoup
from tkinter import scrolledtext
import sys

def enableLyricsButton(button, window):
    global lyricsWindow

    if lyricsWindow:
        button.config(state=tk.NORMAL)
        window.destroy()
    lyricsWindow = None

def lyricsSearch():
    global formatted_music_name, lyricsButton, lyricsWindow

    lyricsWindow = tk.Tk()
    lyricsWindow.title("Letra")
    lyricsWindow.protocol("WM_DELETE_WINDOW", lambda: enableLyricsButton(lyricsButton, lyricsWindow))
    lyricsWindow.resizable(False, False)
    lyricsButton.config(state=tk.DISABLED)

    try:
        link = "https://www.google.com/search?q=" + formatted_music_name + "lyrics"
        container = "xaAUmb"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Safari/537.36"}
        request = requests.get(link, headers=headers)
        site = BeautifulSoup(request.text, "html.parser")
        postInfo = site.find("div", class_=container)

        lyrics = []
        for div in postInfo:
            spans = div.find_all('span', jsname='YS01Ge')
            for span in spans:
                lyrics.append(span.get_text(separator=' ', strip=True))
                lyrics.append('\n')

        song = " "
        song += ' '.join(lyrics)

        texto_scroll = scrolledtext.ScrolledText(lyricsWindow, wrap=tk.WORD, width=40, height=20)
        texto_scroll.pack(expand=True, fill='both')

        texto_scroll.insert(tk.INSERT, song)
        lyricsWindow.mainloop()

    except:
        try:
            music = formatted_music_name.split(" - ")[0]
            link = "https://www.google.com/search?q=" + music + "lyrics"
            container = "xaAUmb"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Safari/537.36"}
            request = requests.get(link, headers=headers)
            site = BeautifulSoup(request.text, "html.parser")
            postInfo = site.find("div", class_=container)

            lyrics = []
            for div in postInfo:
                spans = div.find_all('span', jsname='YS01Ge')
                for span in spans:
                    lyrics.append(span.get_text(separator=' ', strip=True))
                    lyrics.append('\n')

            song = " "
            song += ' '.join(lyrics)

            texto_scroll = scrolledtext.ScrolledText(lyricsWindow, wrap=tk.WORD, width=40, height=20)
            texto_scroll.pack(expand=True, fill='both')

            texto_scroll.insert(tk.INSERT, song)
            lyricsWindow.mainloop()

        except:
            texto_scroll = scrolledtext.ScrolledText(lyricsWindow, wrap=tk.WORD, width=40, height=20)
            texto_scroll.pack(expand=True, fill='both')

            texto_scroll.insert(tk.INSERT, "Letra indisponível")
            lyricsWindow.mainloop()

def update():
    global currentMin, currentSec, playingFile

    if isPlaying and (currentSec != totalSec or currentMin != totalMin):
        currentSec += 1

    if currentSec == 60:
        currentSec = 0
        currentMin += 1
    if currentSec < 10:
        currentTime.config(text=(currentMin,":0",currentSec))
    else:
        currentTime.config(text=(currentMin,":",currentSec))

    if not pygame.mixer.music.get_busy() and isPlaying:
        if replay:
            currentMin = 0
            currentSec = 0
            progress_bar.stop()
            currentTime.config(text=(currentMin, ":0", currentSec))
            playMusic()
        else:
            nextMusic()

    if progress_bar["value"] >= 99:
        progress_bar.stop()
        progress_bar["value"] = 100

    window.after(1000, update)

def playMusic():
    global audio_duration, totalMin, totalSec, isPlaying, audio_files, current_index, index, playingFile

    if isRandom and not replay:
        if index == count:
            index = 0
        if index == -1:
            index = count - 1
        current_index = queue[index]
        playingFile = os.path.join(music_directory, audio_files[current_index])

    pygame.mixer.init()
    pygame.mixer.music.load(playingFile)
    pygame.mixer.music.play(start=0)
    sound = pygame.mixer.Sound(playingFile)

    audio_duration = pygame.mixer.Sound.get_length(sound)
    totalMin = int(audio_duration) // 60
    totalSec = int(audio_duration % 60)
    totalTime.config(text=(totalMin, ":", totalSec))
    stopPlayButton.config(image=playIcon)
    isPlaying = True
    progress_bar.start(int(audio_duration) * 10)
    totalSeconds = currentSec + (currentMin * 60)
    posicaoAtual = int((totalSeconds * 100) / (int(audio_duration)))
    progress_bar["value"] = posicaoAtual

def stopPlayMusic():
    global isPlaying, audio_duration

    if isPlaying:
        stopPlayButton.config(image=stopIcon)
        isPlaying = False
        pygame.mixer.music.pause()
        posicion = progress_bar["value"]
        progress_bar.stop()
        progress_bar["value"] = posicion

    else:
        stopPlayButton.config(image=playIcon)
        isPlaying = True
        pygame.mixer.music.unpause()
        progress_bar.start(int(audio_duration) * 10)
        totalSeconds = currentSec + (currentMin * 60)
        posicaoAtual = int((totalSeconds * 100) / (int(audio_duration)))
        progress_bar["value"] = posicaoAtual

def nextMusic():
    global current_index, currentMin, currentSec, playingFile, replay, index, lyricsWindow

    replay = False
    replayButton.config(image=replayIcon)
    currentMin = 0
    currentSec = 0
    progress_bar.stop()
    currentTime.config(text=(currentMin, ":0", currentSec))

    if audio_files:
        current_index = (current_index + 1) % len(audio_files)
        next_file = os.path.join(music_directory, audio_files[current_index])
        playingFile = next_file
        index += 1
        playMusic()
        updateDisplay()

        if lyricsWindow != None:
            enableLyricsButton(lyricsButton, lyricsWindow)

def previousMusic():
    global current_index, currentMin, currentSec, playingFile, replay, index, lyricsWindow

    replay = False
    replayButton.config(image=replayIcon)
    currentMin = 0
    currentSec = 0
    progress_bar.stop()
    currentTime.config(text=(currentMin, ":0", currentSec))

    if audio_files:
        current_index = (current_index - 1) % len(audio_files)
        previous_file = os.path.join(music_directory, audio_files[current_index])
        playingFile = previous_file
        index -= 1
        playMusic()
        updateDisplay()

        if lyricsWindow:
            enableLyricsButton(lyricsButton, lyricsWindow)

def setVolume(volume):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(float(volume))

def updateDisplay():
    global current_index, formatted_music_name, icons_files

    try:
        formatted_music_name = os.path.splitext(audio_files[current_index])[0]
        music_name_label.config(text=formatted_music_name)
    except:
        pass

    if icons_files:
        formatted_music_name_jpg = formatted_music_name + ".jpg"
        if formatted_music_name_jpg in icons_files:

            icon_file = os.path.join(music_directory, formatted_music_name + ".jpg")
            img = Image.open(icon_file).resize((150, 150))
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img
        else:
            img = Image.open("Buttons/music.png").resize((150, 150))
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img

    window.update_idletasks()

    inicialPosition = music_name_label.winfo_x()
    finalPosicion = inicialPosition + music_name_label.winfo_width()
    distance = finalPosicion - inicialPosition
    center = int(distance / 2)

    music_name_label.place(x=200-center, y=175)

def setReplay():
    global replay, replayButton, replayIcon, replayIconTriggered

    replay = not replay
    if replay:
        replayButton.config(image=replayIconTriggered)
    else:
        replayButton.config(image=replayIcon)


def setRandom():
    global isRandom, count, queue, index, randomButton, randomIcon, randomIconTriggered

    isRandom = not isRandom
    if isRandom:
        index = 0
        queue = list(range(count))
        random.shuffle(queue)
        queue.remove(current_index)
        queue.insert(0, current_index)
        randomButton.config(image=randomIconTriggered)
    else:
        index = 0
        queue = []
        randomButton.config(image=randomIcon)

def on_progress_click(event):
    global audio_duration, playingFile, currentMin, currentSec, currentTime

    audio_duration = int(audio_duration)

    click = event.x
    percent_clicked = (click / progress_bar.winfo_width()) * 100
    value_clicked = (percent_clicked / 100) * progress_bar['maximum']
    progress_bar["value"] = value_clicked

    audioPosicion = int((audio_duration * value_clicked) / 100)
    pygame.mixer.init()
    pygame.mixer.music.load(playingFile)
    pygame.mixer.music.play(start=int(audioPosicion))

    currentMin = int(audioPosicion) // 60
    currentSec = int(audioPosicion % 60)
    if currentSec < 10:
        currentTime.config(text=(currentMin, ":0", currentSec))
    else:
        currentTime.config(text=(currentMin, ":", currentSec))

def fileExplorerMusics():
    global music_directory, audio_files, count, playingFile, icons_files, formatted_music_name
    global current_index, index, currentSec, currentMin, totalSec, totalMin

    music_directory = filedialog.askdirectory(title="Selecione o diretório de músicas")

    if music_directory:
        current_index = 0
        index = 0
        currentSec = 0
        currentMin = 0

        try:
            audio_files = [file for file in os.listdir(music_directory) if file.endswith(('.mp3', '.wav', '.ogg'))]
            count = len(audio_files)
            playingFile = os.path.join(music_directory, audio_files[0])
            playMusic()
            formatted_music_name = os.path.splitext(audio_files[current_index])[0]

            icons_files = [file for file in os.listdir(music_directory) if file.endswith(('.jpg', '.png', '.jpeg'))]

            if icons_files:
                updateDisplay()
                replayButton.config(state=tk.NORMAL)
                randomButton.config(state=tk.NORMAL)
                lyricsButton.config(state=tk.NORMAL)

            else:
                lyricsButton.config(state=tk.DISABLED)
                img = Image.open("Buttons/music.png").resize((150, 150))
                img = ImageTk.PhotoImage(img)
                image_label.config(image=img)
                image_label.image = img
                updateDisplay()

        except:
            audio_files = ""
            playingFile = ""
            enableLyricsButton(lyricsButton, lyricsWindow)
            replayButton.config(state=tk.DISABLED)
            randomButton.config(state=tk.DISABLED)
            lyricsButton.config(state=tk.DISABLED)
            img = Image.open("Buttons/music.png").resize((150, 150))
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img
            current_index = 0
            index = 0
            currentSec = 0
            currentMin = 0
            totalSec = 0
            totalMin = 0
            totalTime.config(text=(totalMin, ":", totalSec))
            music_name_label.config(text="")
            pygame.mixer.music.pause()

def on_main_window_close(window, lyricsWindow):
    window.destroy()
    lyricsWindow.destroy()
    sys.exit()


lyricsWindow = None
current_index = 0
isPlaying = True
audio_duration = 0
totalMin = 0
totalSec = 0
currentMin = 0
currentSec = 0
replay = False
isRandom = False
queue = []
index = 0
playingFile = ""
icons_files = ""
audio_files = ""
music_directory = ""
icons_directory = ""
formatted_music_name = ""
count = 0

window = tk.Tk()
window.title("Music Player")
window.iconbitmap('Buttons/music.ico')
window.geometry(f"{400}x{300}")
window.resizable(False, False)
window.protocol("WM_DELETE_WINDOW", lambda: on_main_window_close(window, lyricsWindow))

totalTime = tk.Label(window, text=(totalMin,":",totalSec), font=("Helvetica", 8))
totalTime.pack(pady=2)
totalTime.place(x=305, y=210)

currentTime = tk.Label(window, text="0:00", font=("Helvetica", 8))
currentTime.pack(pady=2)
currentTime.place(x=55, y=210)

progress_bar = ttk.Progressbar(window, mode='determinate', length=200)
progress_bar.pack(pady=10)
progress_bar.place(x=100, y=210)
progress_bar.bind("<Button-1>", on_progress_click)

buttonFrame = tk.Frame(window)
buttonFrame.pack(side="bottom")

previousIcon = Image.open('Buttons/previousButton.png').resize((30, 30))
previousIcon = ImageTk.PhotoImage(previousIcon)
playIcon = Image.open('Buttons/playButton.png').resize((30, 30))
playIcon = ImageTk.PhotoImage(playIcon)
stopIcon = Image.open('Buttons/stopButton.png').resize((30, 30))
stopIcon = ImageTk.PhotoImage(stopIcon)
nextIcon = Image.open('Buttons/nextButton.png').resize((30, 30))
nextIcon = ImageTk.PhotoImage(nextIcon)
replayIcon = Image.open('Buttons/replayButton.png').resize((20, 20))
replayIcon = ImageTk.PhotoImage(replayIcon)
randomIcon = Image.open('Buttons/randomButton.png').resize((40, 30))
randomIcon = ImageTk.PhotoImage(randomIcon)

replayIconTriggered = Image.open('Buttons/replayButtonTriggered.png').resize((20, 20))
replayIconTriggered = ImageTk.PhotoImage(replayIconTriggered)
randomIconTriggered = Image.open('Buttons/randomButtonTriggered.png').resize((40, 30))
randomIconTriggered = ImageTk.PhotoImage(randomIconTriggered)

replayButton = tk.Button(buttonFrame, image=replayIcon, command=setReplay, relief="flat", bd=0)
replayButton.pack(side="left",  padx=20)
replayButton.config(state=tk.DISABLED)

previousButton = tk.Button(buttonFrame, image=previousIcon, command=previousMusic, relief="flat", bd=0)
previousButton.pack(side="left", padx=10, pady=10)

stopPlayButton = tk.Button(buttonFrame, image=playIcon, command=stopPlayMusic, relief="flat", bd=0)
stopPlayButton.pack(side="left", padx=10, pady=10)

randomButton = tk.Button(buttonFrame, image=randomIcon, command=setRandom, relief="flat", bd=0)
randomButton.pack(side="right",  padx=10)
randomButton.config(state=tk.DISABLED)

nextButton = tk.Button(buttonFrame, image=nextIcon, command=nextMusic, relief="flat", bd=0)
nextButton.pack(side="right", padx=10, pady=10)

pygame.mixer.music.set_endevent(pygame.USEREVENT)

fileExplorerMusicas = tk.Button(window, text="Musicas", command=fileExplorerMusics, width=7)
fileExplorerMusicas.pack(pady=10)
fileExplorerMusicas.place(x=20, y=20)

lyricsButton = tk.Button(window, text="Letra", command=lyricsSearch, width=7)
lyricsButton.pack(pady=10)
lyricsButton.place(x=20, y=50)
lyricsButton.config(state=tk.DISABLED)

image_label = tk.Label(window, image="")
image_label.place(x=125, y=20)

music_name_label = tk.Label(window, text="", font=("Helvetica", 12), anchor="w", justify="left")
music_name_label.place(x=125, y=175)

volumeScale = tk.Scale(window, from_=1.0, to=0.0, orient=tk.VERTICAL, resolution=0.1, command=setVolume)
volumeScale.pack(side="right", padx=10, pady=10)
volumeScale.set(0.1)

window.after(1000, update)
updateDisplay()
window.mainloop()