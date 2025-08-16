import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import threading
import pygame

# Initialize pygame mixer
pygame.mixer.init()

alarm_time = None
alarm_tone = None
alarm_triggered = False
snooze_minutes = 5

def browse_tone():
    global alarm_tone
    alarm_tone = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if alarm_tone:
        tone_label.config(text=f"🎵 {alarm_tone.split('/')[-1]}")
    else:
        tone_label.config(text="No tone selected")

def set_alarm():
    global alarm_time, alarm_triggered
    hour = int(hour_var.get())
    minute = int(minute_var.get())
    now = datetime.now()
    alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if alarm_time < now:
        alarm_time += timedelta(days=1)
    alarm_triggered = False
    status_label.config(text=f"⏰ Alarm set for {alarm_time.strftime('%H:%M')}", fg="green")

def snooze():
    global alarm_time, alarm_triggered
    alarm_time = datetime.now() + timedelta(minutes=snooze_minutes)
    alarm_triggered = False
    stop_alarm()
    status_label.config(text=f"😴 Snoozed for {snooze_minutes} minutes", fg="orange")

def play_alarm():
    if alarm_tone:
        try:
            pygame.mixer.music.load(alarm_tone)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Could not play alarm tone:\n{e}")
    else:
        messagebox.showinfo("Alarm", "⏰ Wake up!")

def stop_alarm():
    pygame.mixer.music.stop()

def check_alarm():
    global alarm_triggered
    while True:
        if alarm_time and not alarm_triggered:
            if datetime.now() >= alarm_time:
                alarm_triggered = True
                play_alarm()
        threading.Event().wait(1)

# GUI setup
root = tk.Tk()
root.title("Alarm Clock")
root.geometry("350x400")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

title = tk.Label(root, text="⏰ Alarm Clock", font=("Arial", 18, "bold"), bg="#f0f0f0")
title.pack(pady=10)

time_frame = tk.Frame(root, bg="#f0f0f0")
time_frame.pack(pady=10)

tk.Label(time_frame, text="Set Time:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5)

hour_var = tk.StringVar(value="07")
minute_var = tk.StringVar(value="00")

hour_menu = tk.OptionMenu(time_frame, hour_var, *[f"{i:02d}" for i in range(24)])
minute_menu = tk.OptionMenu(time_frame, minute_var, *[f"{i:02d}" for i in range(60)])
hour_menu.config(width=3)
minute_menu.config(width=3)

hour_menu.grid(row=0, column=1)
tk.Label(time_frame, text=":", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=2)
minute_menu.grid(row=0, column=3)

tk.Button(root, text="Choose Alarm Tone", command=browse_tone, bg="#2196f3", fg="white", font=("Arial", 10)).pack(pady=10)
tone_label = tk.Label(root, text="No tone selected", font=("Arial", 10), bg="#f0f0f0")
tone_label.pack()

tk.Button(root, text="Set Alarm", command=set_alarm, bg="#4caf50", fg="white", font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="Snooze", command=snooze, bg="#ff9800", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Stop Alarm", command=stop_alarm, bg="#f44336", fg="white", font=("Arial", 12)).pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 12), bg="#f0f0f0")
status_label.pack(pady=10)

# Start alarm checking thread
threading.Thread(target=check_alarm, daemon=True).start()

root.mainloop()