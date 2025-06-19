import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import subprocess
from playsound import playsound

def start_quiz(player_name="অতিথি", total_questions=10):
    with open("questions.json", "r", encoding="utf-8") as file:
        questions = json.load(file)

    random.shuffle(questions)
    questions = questions[:total_questions]

    score_file = "scores.json"
    if not os.path.exists(score_file):
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

    dark_theme = {
        "BG_COLOR": "#1e1e1e",
        "FG_COLOR": "#ffffff",
        "BTN_COLOR": "#333333",
        "HL_COLOR": "#00ffcc",
    }
    light_theme = {
        "BG_COLOR": "#f0f0f0",
        "FG_COLOR": "#000000",
        "BTN_COLOR": "#dddddd",
        "HL_COLOR": "#0077cc",
    }

    theme = dark_theme

    question_index = 0
    score = 0
    attempts = 0
    time_left = 10
    timer_id = None
    current_options = []
    wrong_questions = []

    root = tk.Tk()
    root.title("বাংলাদেশ ইতিহাস কুইজ")
    root.geometry("600x520")

    def apply_theme():
        root.configure(bg=theme["BG_COLOR"])
        question_label.config(bg=theme["BG_COLOR"], fg=theme["FG_COLOR"])
        timer_label.config(bg=theme["BG_COLOR"])
        message_label.config(bg=theme["BG_COLOR"])
        dark_mode_btn.config(bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], activebackground="#555555")
        for btn in option_buttons:
            btn.config(bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], activebackground="#555555")

    def toggle_theme():
        nonlocal theme
        if theme == dark_theme:
            theme = light_theme
            dark_mode_btn.config(text="ডার্ক মোড")
        else:
            theme = dark_theme
            dark_mode_btn.config(text="লাইট মোড")
        apply_theme()

    def show_message(text, color=theme["HL_COLOR"], duration=1500):
        message_label.config(text=text, fg=color)
        message_label.after(duration, lambda: message_label.config(text=""))

    def load_question():
        nonlocal question_index, time_left, timer_id, current_options

        if question_index < len(questions):
            q = questions[question_index]
            options = q["options"].copy()
            random.shuffle(options)
            current_options = options

            question_label.config(text=f"প্রশ্ন {question_index+1}: {q['question']}")
            for i in range(4):
                option_buttons[i].config(text=options[i], state=tk.NORMAL, bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"])

            time_left = 10
            update_timer()
        else:
            show_result()

    def update_timer():
        nonlocal time_left, timer_id
        if time_left > 5:
            color = "#00ff00"
        elif time_left > 2:
            color = "#ffaa00"
        else:
            color = "#ff4444"
        timer_label.config(text=f"⏱️ সময় বাকি: {time_left} সেকেন্ড", fg=color)

        if time_left > 0:
            time_left -= 1
            timer_id = root.after(1000, update_timer)
        else:
            playsound("timeout.mp3", block=False)
            disable_buttons()
            show_message("সময় শেষ! পরের প্রশ্ন...", color="#ff8800", duration=2000)
            root.after(2000, next_question)

    def check_answer(selected_index):
        nonlocal score, timer_id, attempts
        if timer_id:
            root.after_cancel(timer_id)
        attempts += 1

        selected = current_options[selected_index]
        correct = questions[question_index]["answer"]

        if selected == correct:
            playsound("right.mp3", block=False)
            score += 1
            disable_buttons()
            show_message("✔️ সঠিক উত্তর!", color="#00ff00")
            root.after(1500, next_question)
        else:
            playsound("wrong.mp3", block=False)
            wrong_questions.append({
                "question": questions[question_index]["question"],
                "correct": correct
            })
            disable_buttons()
            show_message("❌ ভুল হয়েছে, পরের প্রশ্ন...", color="#ff4444")
            root.after(1500, next_question)

    def disable_buttons():
        for btn in option_buttons:
            btn.config(state=tk.DISABLED)

    def next_question():
        nonlocal question_index
        question_index += 1
        load_question()

    def show_result():
        nonlocal timer_id
        if timer_id:
            root.after_cancel(timer_id)

        with open(score_file, "r+", encoding="utf-8") as f:
            scores = json.load(f)
            scores.append({"name": player_name, "score": score, "attempts": attempts})
            scores = sorted(scores, key=lambda x: x["score"], reverse=True)
            f.seek(0)
            f.truncate()
            json.dump(scores, f, ensure_ascii=False, indent=2)

        with open(score_file, "r", encoding="utf-8") as f:
            scores = json.load(f)

        top_scores_text = "\n".join([
            f"{i+1}. {s['name']} - স্কোর: {s['score']} - চেষ্টা: {s.get('attempts', '?')}"
            for i, s in enumerate(scores[:5])
        ])

        result_window = tk.Toplevel(root)
        result_window.title("স্কোরবোর্ড")
        result_window.geometry("600x600")
        result_window.configure(bg=theme["BG_COLOR"])

        msg_label = tk.Label(result_window, text=f"{player_name}, তোমার স্কোর: {score} / {len(questions)}\nমোট চেষ্টা: {attempts}\n\nসেরা স্কোর:\n{top_scores_text}",
                             bg=theme["BG_COLOR"], fg=theme["HL_COLOR"], font=("Helvetica", 12), justify="left")
        msg_label.pack(pady=15, padx=10)

        if wrong_questions:
            wrong_label = tk.Label(result_window, text="\nতুমি যেসব প্রশ্নে ভুল করেছো:",
                                   bg=theme["BG_COLOR"], fg="#ff4444", font=("Helvetica", 14, "bold"), justify="left")
            wrong_label.pack(pady=10, padx=10, anchor="w")

            scroll_canvas = tk.Canvas(result_window, bg=theme["BG_COLOR"], highlightthickness=0)
            scroll_frame = tk.Frame(scroll_canvas, bg=theme["BG_COLOR"])
            scroll_bar = tk.Scrollbar(result_window, orient="vertical", command=scroll_canvas.yview)
            scroll_canvas.configure(yscrollcommand=scroll_bar.set)

            scroll_bar.pack(side="right", fill="y")
            scroll_canvas.pack(side="left", fill="both", expand=True)
            scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

            for wq in wrong_questions:
                q_label = tk.Label(scroll_frame, text=f"প্রশ্ন: {wq['question']}\nসঠিক উত্তর: {wq['correct']}\n",
                                   bg=theme["BG_COLOR"], fg=theme["FG_COLOR"], font=("Helvetica", 12), justify="left", wraplength=550)
                q_label.pack(padx=15, anchor="w")

            scroll_frame.update_idletasks()
            scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))

        def restart_game():
            nonlocal question_index, score, attempts, wrong_questions
            question_index = 0
            score = 0
            attempts = 0
            wrong_questions.clear()
            random.shuffle(questions)
            result_window.destroy()
            load_question()

        def exit_game():
            root.quit()

        def go_home():
            result_window.destroy()
            root.destroy()
            subprocess.Popen(["python", "game_menu.py"])

        tk.Button(result_window, text="পুনরায় শুরু করো", command=restart_game, bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], width=20).pack(pady=8)
        tk.Button(result_window, text="বের হও", command=exit_game, bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], width=20).pack(pady=8)
        tk.Button(result_window, text="🏠 হোমে ফিরে যাও", command=go_home, bg="#2288cc", fg="#ffffff", width=20).pack(pady=10)

        disable_buttons()

    question_label = tk.Label(root, text="", font=("Helvetica", 16), bg=theme["BG_COLOR"], fg=theme["FG_COLOR"], wraplength=550, justify="center")
    question_label.pack(pady=20)

    timer_label = tk.Label(root, text="", font=("Helvetica", 12), bg=theme["BG_COLOR"])
    timer_label.pack()

    message_label = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg=theme["BG_COLOR"], fg=theme["HL_COLOR"])
    message_label.pack(pady=10)

    dark_mode_btn = tk.Button(root, text="লাইট মোড", command=toggle_theme, bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], width=12)
    dark_mode_btn.pack(pady=10)

    option_buttons = []
    for i in range(4):
        btn = tk.Button(root, text="", font=("Helvetica", 12), width=50, height=2,
                        bg=theme["BTN_COLOR"], fg=theme["FG_COLOR"], activebackground="#555555",
                        command=lambda idx=i: check_answer(idx))
        btn.pack(pady=5)
        option_buttons.append(btn)

    apply_theme()
    load_question()
    root.mainloop()

# এই অংশটা স্ক্রিপ্ট হিসেবে চালাতে হলে নিচে রাখো
if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "অতিথি"
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    start_quiz(name, total)
