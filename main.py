import speech_recognition as sr
import webbrowser
from gtts import gTTS
import os
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('CLIENT_ID'),
                                               client_secret=os.getenv('CLIENT_SECRET'),
                                               redirect_uri=os.getenv('REDIRECT_URI'),
                                               scope=scope))

recognizer = sr.Recognizer()

def update_message(text):
    message_label.config(text=text)
    print(text)

def talk():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        update_message("")
        
        text = recognizer.recognize_google(audio, language='es-ES')
        update_message(f'Has dicho: {text}')
        return text.lower()
    except sr.UnknownValueError:
        speak('Lo siento, no te escuché bien. Intenta otra vez."')
        update_message("No se pudo entender el audio.")
    except sr.RequestError as e:
        update_message(f"Error con el servicio de reconocimiento de Google: {e}")
    except sr.WaitTimeoutError:
        speak('No pude captar eso. ¿Podrías repetirlo?')
        update_message("No se detectó audio")

def speak(text):
    tts = gTTS(text=text, lang='es')
    tts.save("output.mp3")
    os.system("mpg123 output.mp3")

def process_voice_command():
    text = talk()
    if text:
        if 'amazon' in text:
            speak('¿Qué quieres comprar en Amazon?')
            search_term = talk()
            webbrowser.open(f'https://www.amazon.es/s?k={search_term}')

        elif 'spotify' in text:
            speak('Abriendo la Aplicacion Spotify.')
            subprocess.Popen(['spotify'])

        elif 'reloj' in text:
            speak('Abriendo el Reloj')
            subprocess.Popen(['gnome-clocks'])

        elif 'bloc de notas' in text:
            speak('Abriendo el Bloc de Notas')
            subprocess.Popen(['gedit'])
        
        elif 'whatsapp' in text:
            speak('Abriendo Whatsapp')
            subprocess.Popen(['whatsapp-for-linux'])

        elif 'reproduce' in text:
            song_name = text.replace('reproduce', '').strip()
            if song_name:
                results = sp.search(q=song_name, type='track', limit=10)
                exact_matches = [track for track in results['tracks']['items'] if track['name'].lower() == song_name.lower()]
                if exact_matches:
                    track = exact_matches[0]
                else:
                    results = sp.search(q=song_name, type='track', limit=10)
                    if results['tracks']['items']:
                        track = results['tracks']['items'][0]
                    else:
                        track = None

                if track:
                    devices = sp.devices()
                    active_device_id = None
                    for device in devices['devices']:
                        if device['is_active']:
                            active_device_id = device['id']
                            break

                    if active_device_id:
                        sp.start_playback(device_id=active_device_id, uris=[track['uri']])
                        speak(f'Reproduciendo {track["name"]} de {track["artists"][0]["name"]}')
                    else:
                        speak('No hay dispositivos activos para reproducir.')
                else:
                    speak('No encontré la canción.')
            else:
                speak('No entendí el nombre de la canción que quieres reproducir.')

        elif 'busca' in text:
            search_term = text.replace('busca', '').strip()
            if search_term:
                speak(f'Buscando {search_term} en Google.')
                webbrowser.open(f'https://www.google.com/search?q={search_term}')
            else:
                speak('No entendí lo que quieres buscar.')
        else:
            speak('No estoy diseñado para realizar esa tarea. ¿Hay algo más en lo que pueda ayudarte?')

root = tk.Tk()
root.title("Asistente de voz")
root.geometry("400x700")

root.after(1000, lambda: speak("Hola, ¿en qué puedo ayudarte?"))

canvas = tk.Canvas(root, width=400, height=800, bg='#ffffff')
canvas.pack(fill="both", expand=True)

titulo = tk.Label(
    text="¿Puedo ayudarte con algo?",
    bg='white',
    fg='#cb6ce6',
    font=("Helvetica", 18, "bold")
)
canvas.create_window(200, 100, window=titulo) 

mic_image = Image.open("assets/img/microphone.png")
mic_image = mic_image.resize((200, 200), Image.LANCZOS)
mic_photo = ImageTk.PhotoImage(mic_image)

mic_image_hover = mic_image.resize((220, 220), Image.LANCZOS)
mic_photo_hover = ImageTk.PhotoImage(mic_image_hover)

def on_enter(event):
    mic_button.config(image=mic_photo_hover)

def on_leave(event):
    mic_button.config(image=mic_photo)

mic_button = tk.Button(root, image=mic_photo, command=process_voice_command, bd=0, highlightthickness=0, bg='#ffffff', activebackground='#ffffff', relief='flat')
canvas.create_window(200, 350, window=mic_button)

mic_button.bind("<Enter>", on_enter)
mic_button.bind("<Leave>", on_leave)

message_label = tk.Label(root, text="Presiona el micrófono \npara poder escucharte", font=("Helvetica", 16), bg='#ffffff', fg='#cb6ce6')
canvas.create_window(200, 600, window=message_label)

root.mainloop()
