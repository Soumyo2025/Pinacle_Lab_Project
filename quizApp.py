import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from collections import defaultdict
import uuid

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizMaster")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.quizzes = self.load_quizzes()

        # Style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f8f9fa")
        self.style.configure("TButton", padding=6, relief="flat", background="#e9ecef")
        self.style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Quiz.TButton", font=("Segoe UI", 10), padding=10)
        self.style.configure("Option.TButton", width=30, anchor="w", padding=8)
        self.style.configure("Correct.TButton", background="#d4edda")
        self.style.configure("Incorrect.TButton", background="#f8d7da")
        self.style.configure("Highlight.TButton", background="#e2e3e5")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.show_welcome_screen()

    def load_quizzes(self):
        if os.path.exists("quizzes.json"):
            try:
                with open("quizzes.json", "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass

        default_quizzes = {
            "quizzes": [
                {
                    "id": "general_knowledge",
                    "title": "General Knowledge",
                    "description": "Test your knowledge about various topics",
                    "difficulty": "Medium",
                    "category": "General",
                    "questions": [
                        {
                            "text": "What is the capital of France?",
                            "options": ["London", "Berlin", "Paris", "Madrid"],
                            "answer": 2
                        }
                    ]
                }
            ]
        }
        self.save_quizzes(default_quizzes)
        return default_quizzes

    def save_quizzes(self, quizzes_data=None):
        if quizzes_data is None:
            quizzes_data = self.quizzes
        with open("quizzes.json", "w") as f:
            json.dump(quizzes_data, f, indent=4)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_frame()

        header = ttk.Label(self.main_frame, text="QuizMaster", style="Header.TLabel")
        header.pack(pady=(20, 5))
        desc = ttk.Label(self.main_frame, text="Select a quiz to begin:")
        desc.pack()

        container = ttk.Frame(self.main_frame)
        container.pack(pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Group by category
        categories = defaultdict(list)
        for quiz in self.quizzes["quizzes"]:
            category = quiz.get("category", quiz.get("difficulty", "Uncategorized"))
            categories[category].append(quiz)

        for category, quizzes in categories.items():
            cat_label = ttk.Label(scrollable_frame, text=category, style="Header.TLabel")
            cat_label.pack(anchor="w", padx=10, pady=(10, 5))

            for quiz in quizzes:
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill="x", padx=10, pady=5)

                btn = ttk.Button(
                    frame,
                    text=f"{quiz['title']}\n{quiz['description']}\nDifficulty: {quiz['difficulty']}",
                    command=lambda q=quiz: self.start_quiz(q),
                    style="Quiz.TButton"
                )
                btn.pack(side="left", fill="x", expand=True)

                del_btn = ttk.Button(frame, text="Delete", command=lambda q=quiz: self.delete_quiz(q))
                del_btn.pack(side="right", padx=5)

        create_button = ttk.Button(
            self.main_frame,
            text="Create/Insert New Quiz",
            command=self.show_create_quiz_screen,
            style="Quiz.TButton"
        )
        create_button.pack(pady=10)

    def delete_quiz(self, quiz):
        if messagebox.askyesno("Delete Quiz", f"Are you sure you want to delete '{quiz['title']}'?"):
            self.quizzes["quizzes"] = [q for q in self.quizzes["quizzes"] if q["id"] != quiz["id"]]
            self.save_quizzes()
            self.show_welcome_screen()

    def start_quiz(self, quiz):
        self.current_quiz = quiz
        self.current_question = 0
        self.user_answers = [None] * len(quiz["questions"])
        self.score = 0
        self.show_question()

    def show_question(self):
        self.clear_frame()
        question = self.current_quiz["questions"][self.current_question]

        progress = ttk.Label(self.main_frame, text=f"Question {self.current_question + 1} of {len(self.current_quiz['questions'])}")
        progress.pack(pady=10)

        question_label = ttk.Label(self.main_frame, text=question["text"], font=("Segoe UI", 12, "bold"), wraplength=700)
        question_label.pack(pady=5)

        for i, option in enumerate(question["options"]):
            style = "Option.TButton"
            if self.user_answers[self.current_question] is not None:
                if i == question["answer"]:
                    style = "Correct.TButton"
                elif i == self.user_answers[self.current_question]:
                    style = "Incorrect.TButton"

            btn = ttk.Button(
                self.main_frame,
                text=option,
                command=lambda idx=i: self.select_answer(idx),
                style=style
            )
            btn.pack(fill="x", padx=40, pady=4)

        nav = ttk.Frame(self.main_frame)
        nav.pack(pady=20)

        if self.current_question > 0:
            ttk.Button(nav, text="Previous", command=self.prev_question).pack(side="left", padx=10)

        if self.user_answers[self.current_question] is not None:
            if self.current_question < len(self.current_quiz["questions"]) - 1:
                ttk.Button(nav, text="Next", command=self.next_question).pack(side="right", padx=10)
            else:
                ttk.Button(nav, text="Finish Quiz", command=self.show_results).pack(side="right", padx=10)

    def select_answer(self, idx):
        if self.user_answers[self.current_question] is None:
            self.user_answers[self.current_question] = idx
            if idx == self.current_quiz["questions"][self.current_question]["answer"]:
                self.score += 1
            self.show_question()

    def prev_question(self):
        self.current_question -= 1
        self.show_question()

    def next_question(self):
        if self.user_answers[self.current_question] is None:
            messagebox.showwarning("No Answer", "Select an answer first.")
        else:
            self.current_question += 1
            self.show_question()

    def show_results(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Quiz Results", style="Header.TLabel").pack(pady=10)
        ttk.Label(self.main_frame, text=f"Score: {self.score} / {len(self.current_quiz['questions'])}").pack(pady=5)

        for i, q in enumerate(self.current_quiz["questions"]):
            correct = self.user_answers[i] == q["answer"]
            q_frame = ttk.Frame(self.main_frame, relief="solid", borderwidth=1, padding=10)
            q_frame.pack(fill="x", padx=10, pady=5)

            color = "green" if correct else "red"
            ttk.Label(q_frame, text=f"Q{i+1}: {q['text']}", foreground=color, wraplength=600).pack(anchor="w")

            ua = self.user_answers[i]
            user_answer = q["options"][ua] if ua is not None else "No answer"
            ttk.Label(q_frame, text=f"Your answer: {user_answer}").pack(anchor="w")

            if not correct:
                ttk.Label(q_frame, text=f"Correct answer: {q['options'][q['answer']]}", foreground="blue").pack(anchor="w")

        btns = ttk.Frame(self.main_frame)
        btns.pack(pady=15)
        ttk.Button(btns, text="Restart Quiz", command=lambda: self.start_quiz(self.current_quiz)).pack(side="left", padx=10)
        ttk.Button(btns, text="Back to Menu", command=self.show_welcome_screen).pack(side="left", padx=10)

    def show_create_quiz_screen(self):
        self.clear_frame()
        self.new_quiz_questions = []

        header = ttk.Label(self.main_frame, text="Create New Quiz", style="Header.TLabel")
        header.pack(pady=10)

        form = ttk.Frame(self.main_frame)
        form.pack(padx=20, fill="x")

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
        self.quiz_title = ttk.Entry(form)
        self.quiz_title.grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w")
        self.quiz_description = ttk.Entry(form)
        self.quiz_description.grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Difficulty").grid(row=2, column=0, sticky="w")
        self.quiz_difficulty = ttk.Combobox(form, values=["Easy", "Medium", "Hard"])
        self.quiz_difficulty.grid(row=2, column=1, sticky="ew")
        self.quiz_difficulty.set("Easy")

        ttk.Label(form, text="Category").grid(row=3, column=0, sticky="w")
        self.quiz_category = ttk.Entry(form)
        self.quiz_category.grid(row=3, column=1, sticky="ew")

        form.columnconfigure(1, weight=1)

        self.questions_frame = ttk.Frame(self.main_frame)
        self.questions_frame.pack(fill="both", expand=True, padx=20)
        self.add_new_question()

        controls = ttk.Frame(self.main_frame)
        controls.pack(pady=15)
        ttk.Button(controls, text="Add Question", command=self.add_new_question).pack(side="left", padx=10)
        ttk.Button(controls, text="Save Quiz", command=self.save_new_quiz).pack(side="left", padx=10)
        ttk.Button(controls, text="Cancel", command=self.show_welcome_screen).pack(side="left", padx=10)

    def add_new_question(self):
        q_num = len(self.new_quiz_questions) + 1
        frame = ttk.Frame(self.questions_frame, relief="solid", borderwidth=1, padding=10)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=f"Question {q_num}").pack(anchor="w")
        text = tk.Text(frame, height=3, width=70)
        text.pack()

        options = []
        var = tk.IntVar(value=0)

        for i in range(4):
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)
            tk.Radiobutton(row, variable=var, value=i).pack(side="left")
            entry = ttk.Entry(row, width=60)
            entry.pack(side="left", padx=5)
            options.append(entry)

        remove_btn = ttk.Button(frame, text="Remove", command=frame.destroy)
        remove_btn.pack(anchor="e")

        self.new_quiz_questions.append({"frame": frame, "text": text, "options": options, "answer_var": var})

    def save_new_quiz(self):
        title = self.quiz_title.get().strip()
        description = self.quiz_description.get().strip()
        difficulty = self.quiz_difficulty.get()
        category = self.quiz_category.get().strip()

        if not title or not difficulty:
            messagebox.showerror("Missing Info", "Please enter title and difficulty.")
            return

        questions = []
        for q in self.new_quiz_questions:
            text = q["text"].get("1.0", "end-1c").strip()
            options = [opt.get().strip() for opt in q["options"]]
            answer = q["answer_var"].get()

            if not text or any(not o for o in options):
                messagebox.showerror("Invalid Question", "All questions and options must be filled.")
                return

            questions.append({"text": text, "options": options, "answer": answer})

        new_quiz = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "category": category if category else difficulty,
            "questions": questions
        }

        self.quizzes["quizzes"].append(new_quiz)
        self.save_quizzes()
        messagebox.showinfo("Success", "Quiz saved!")
        self.show_welcome_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
