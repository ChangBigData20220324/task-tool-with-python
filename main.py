import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
import pytz
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

class TaskToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Daily Task Recorder")
        master.geometry("1000x600")

        # Create frame for single page
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_main_frame()

     

    def setup_main_frame(self):
        # Left side: Input fields
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        today = datetime.now().date()
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        
        ttk.Label(input_frame, text="Settlement Date:").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.set_date(thursday)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(input_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=1, column=1, sticky="we", pady=5)

        ttk.Label(input_frame, text="Task Content:").grid(row=2, column=0, sticky="w", pady=5)
        self.task_content = tk.Text(input_frame, height=5)
        self.task_content.grid(row=2, column=1, sticky="we", pady=5)

        ttk.Label(input_frame, text="Score:").grid(row=3, column=0, sticky="w", pady=5)
        self.score_entry = ttk.Entry(input_frame)
        self.score_entry.insert(0, "1")  # Set default value to "1"
        self.score_entry.grid(row=3, column=1, sticky="we", pady=5)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=4, column=0, columnspan=2, pady=10)

        # Right side: Weekly View
        weekly_frame = ttk.Frame(self.main_frame)
        weekly_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(weekly_frame, text="Weekly View").pack()
        self.weekly_view = ttk.Treeview(weekly_frame, columns=("Date", "User_id", "Task", "Score"), show="headings")
        self.weekly_view.heading("Date", text="Date")
        self.weekly_view.heading("User_id", text="User_id")
        self.weekly_view.heading("Task", text="Task")
        self.weekly_view.heading("Score", text="Score")
        self.weekly_view.pack(fill=tk.BOTH, expand=True)

        ttk.Button(weekly_frame, text="Refresh Weekly View", command=self.update_weekly_view).pack(pady=10)

    def get_user_id(self, name):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE name = ?", (name,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
        


    def add_task(self):
        local_tz = pytz.timezone('Asia/Taipei')
        local_time = datetime.now(local_tz)

        user_id = self.get_user_id(self.name_entry.get())
        if user_id is None:
            messagebox.showerror("Error", "User not found in the database.")
            return
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (date, users_id, task, score, created_at)
                    VALUES (?,?,?,?,?)""", (
            self.date_entry.get_date().strftime('%Y-%m-%d'),
            user_id,
            self.task_content.get("1.0", tk.END).strip(),
            self.score_entry.get(),
            local_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()
        self.update_weekly_view()

    def update_weekly_view(self):
        for i in self.weekly_view.get_children():
            self.weekly_view.delete(i)

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        
        today = datetime.now().date()
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        
        c.execute("SELECT date, users_id, task, score FROM tasks WHERE date = ?", 
                (thursday.strftime('%Y-%m-%d'),))
        for row in c.fetchall():
            self.weekly_view.insert("", "end", values=row)
        conn.close()

        
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskToolGUI(root)
    root.mainloop()
