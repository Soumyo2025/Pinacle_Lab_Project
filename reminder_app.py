import tkinter as tk
from tkinter import messagebox, simpledialog
import calendar
from datetime import datetime
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_reminder(date, text):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('INSERT INTO reminders (date, text) VALUES (?, ?)', (date, text))
    conn.commit()
    conn.close()

def get_reminders(date):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT id, text FROM reminders WHERE date = ?', (date,))
    reminders = c.fetchall()
    conn.close()
    return reminders

def update_reminder(reminder_id, new_text):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('UPDATE reminders SET text = ? WHERE id = ?', (new_text, reminder_id))
    conn.commit()
    conn.close()

def delete_reminder(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()

def get_reminder_date(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT date FROM reminders WHERE id = ?', (reminder_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Main App
class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reminder Calendar")
        self.dark_mode = False

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.header = tk.Label(root, text="", font=("Arial", 16))
        self.header.pack(pady=10)

        self.calendar_frame = tk.Frame(root)
        self.calendar_frame.pack()

        self.toggle_button = tk.Button(root, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.toggle_button.pack(pady=10)

        self.draw_calendar()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.draw_calendar()

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        self.header.config(bg="#333" if self.dark_mode else "#f0f0f0", fg="#fff" if self.dark_mode else "#000")
        self.root.config(bg=self.header["bg"])
        self.calendar_frame.config(bg=self.header["bg"])

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, width=5, bg=self.header["bg"],
                     fg="#fff" if self.dark_mode else "#000").grid(row=0, column=i)

        month_days = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self.calendar_frame, text="", width=5, bg=self.header["bg"]).grid(row=r, column=c)
                else:
                    btn = tk.Button(self.calendar_frame, text=str(day), width=5,
                                    command=lambda d=day: self.open_reminder(d),
                                    bg="#555" if self.dark_mode else "#ddd",
                                    fg="#fff" if self.dark_mode else "#000")
                    btn.grid(row=r, column=c)

    def open_reminder(self, day):
        date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        reminders = get_reminders(date_str)

        popup = tk.Toplevel(self.root)
        popup.title(f"Reminders for {date_str}")
        popup.geometry("400x300")
        popup.configure(bg="#333" if self.dark_mode else "#f0f0f0")

        tk.Label(popup, text=f"Reminders for {date_str}", font=("Arial", 14),
                 bg=popup["bg"], fg="#fff" if self.dark_mode else "#000").pack(pady=10)

        frame = tk.Frame(popup, bg=popup["bg"])
        frame.pack(fill="both", expand=True)

        for r_id, text in reminders:
            row = tk.Frame(frame, bg=popup["bg"])
            row.pack(fill="x", pady=5)

            tk.Label(row, text=text, bg=popup["bg"], fg="#fff" if self.dark_mode else "#000",
                     wraplength=250, justify="left").pack(side="left", padx=5)

            tk.Button(row, text="Edit", command=lambda rid=r_id, t=text: self.edit_reminder(rid, t, popup),
                      bg="#2196f3", fg="white", width=6).pack(side="right", padx=2)
            tk.Button(row, text="Delete", command=lambda rid=r_id: self.delete_reminder(rid, popup),
                      bg="#f44336", fg="white", width=6).pack(side="right", padx=2)

        tk.Button(popup, text="Add New Reminder", command=lambda: self.add_reminder(date_str, popup),
                  bg="#4caf50", fg="white").pack(pady=10)

    def add_reminder(self, date_str, popup):
        text = simpledialog.askstring("New Reminder", "Enter reminder text:", parent=popup)
        if text:
            save_reminder(date_str, text)
            messagebox.showinfo("Saved", "Reminder added successfully!", parent=popup)
            popup.destroy()
            self.open_reminder(int(date_str.split("-")[2]))

    def edit_reminder(self, reminder_id, old_text, popup):
        new_text = simpledialog.askstring("Edit Reminder", "Update text:", initialvalue=old_text, parent=popup)
        if new_text:
            update_reminder(reminder_id, new_text)
            messagebox.showinfo("Updated", "Reminder updated successfully!", parent=popup)
            popup.destroy()
            self.open_reminder(int(datetime.strptime(get_reminder_date(reminder_id), "%Y-%m-%d").day))

    def delete_reminder(self, reminder_id, popup):
        delete_reminder(reminder_id)
        messagebox.showinfo("Deleted", "Reminder deleted successfully!", parent=popup)
        popup.destroy()
        self.open_reminder(int(datetime.strptime(get_reminder_date(reminder_id), "%Y-%m-%d").day))
    
# Run the app
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()