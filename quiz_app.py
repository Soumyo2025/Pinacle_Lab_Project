import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("🧠 Quiz Platform")
        self.master.geometry("700x600")
        self.master.configure(bg="#f0f0f0")
        self.score = 0
        self.q_index = 0
        self.timer_seconds = 15
        self.timer_id = None

        self.load_quiz("quiz_data.json")

        # Title
        tk.Label(master, text="🧠 Quiz Time!", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=10)

        # Difficulty
        self.difficulty_label = tk.Label(master, text="", font=("Arial", 12, "italic"), bg="#f0f0f0")
        self.difficulty_label.pack()

        # Image
        self.image_label = tk.Label(master, bg="#f0f0f0")
        self.image_label.pack(pady=10)

        # Question
        self.question_label = tk.Label(master, text="", wraplength=600, font=("Arial", 16), bg="#f0f0f0", justify="center")
        self.question_label.pack(pady=10)

        # Options
        self.var = tk.StringVar()
        self.options_frame = tk.Frame(master, bg="#f0f0f0")
        self.options_frame.pack(pady=10)
        self.options = []
        for _ in range(4):
            rb = tk.Radiobutton(self.options_frame, text="", variable=self.var, value="", font=("Arial", 12),
                                bg="#f0f0f0", anchor="w", width=50, justify="left", padx=10)
            rb.pack(pady=5, anchor="w")
            self.options.append(rb)

        # Timer
        self.timer_display = tk.Label(master, text="", font=("Arial", 14, "bold"), fg="blue", bg="#f0f0f0")
        self.timer_display.pack(pady=5)

        # Submit button
        self.submit_btn = tk.Button(master, text="Submit Answer", command=self.check_answer,
                                    font=("Arial", 12), bg="#4caf50", fg="white", width=20)
        self.submit_btn.pack(pady=10)

        # Status
        self.status_label = tk.Label(master, text="", font=("Arial", 12), bg="#f0f0f0")
        self.status_label.pack(pady=5)

        # Score
        self.score_label = tk.Label(master, text="Score: 0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="darkgreen")
        self.score_label.pack(pady=5)

        self.display_question()

    def load_quiz(self, filename):
        with open(filename, "r") as f:
            self.quiz = json.load(f)

    def display_question(self):
        if self.q_index < len(self.quiz):
            self.reset_timer()
            q = self.quiz[self.q_index]
            self.difficulty_label.config(text=f"Difficulty: {q.get('difficulty', 'Unknown')}")
            self.question_label.config(text=f"Q{self.q_index + 1}: {q['question']}")
            self.var.set(None)

            for i, opt in enumerate(q['options']):
                self.options[i].config(text=opt, value=opt)

            self.load_image(q.get("image"))
            self.start_timer()
        else:
            self.end_quiz()

    def load_image(self, path):
        if path:
            try:
                img = Image.open(path)
                img = img.resize((300, 200), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            except Exception as e:
                self.image_label.config(image="", text="Image not found", fg="red")
        else:
            self.image_label.config(image="", text="")

    def start_timer(self):
        self.timer_seconds = 15
        self.update_timer()

    def update_timer(self):
        self.timer_display.config(text=f"⏱️ Time left: {self.timer_seconds} sec")
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            self.status_label.config(text="⏰ Time's up!", fg="orange")
            self.q_index += 1
            self.master.after(1000, self.display_question)

    def reset_timer(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

    def check_answer(self):
        self.reset_timer()
        selected = self.var.get()
        correct = self.quiz[self.q_index]['answer']
        if selected == correct:
            self.score += 1
            self.status_label.config(text="✅ Correct!", fg="green")
        else:
            self.status_label.config(text=f"❌ Wrong! Correct answer: {correct}", fg="red")
        self.score_label.config(text=f"Score: {self.score}")
        self.q_index += 1
        self.master.after(1000, self.display_question)

    def end_quiz(self):
        messagebox.showinfo("Quiz Completed", f"Your final score: {self.score}/{len(self.quiz)}")
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()