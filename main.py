import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
import pytz
import pandas as pd

class TaskToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Daily Task Recorder")
        master.geometry("1000x600")

        # Create notebook for multiple pages
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Page 1: Input and Weekly View
        self.page1 = ttk.Frame(self.notebook)
        self.notebook.add(self.page1, text="Input & Weekly View")

        # Page 2: Excel Export
        self.page2 = ttk.Frame(self.notebook)
        self.notebook.add(self.page2, text="Excel Export")

        self.setup_page1()
        self.setup_page2()

        # Initialize database
        self.init_db()

    def setup_page1(self):
        # Left side: Input fields
        input_frame = ttk.Frame(self.page1)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="Settlement Date:").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
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
        weekly_frame = ttk.Frame(self.page1)
        weekly_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(weekly_frame, text="Weekly View").pack()
        self.weekly_view = ttk.Treeview(weekly_frame, columns=("Date", "Name", "Task", "Score"), show="headings")
        self.weekly_view.heading("Date", text="Date")
        self.weekly_view.heading("Name", text="Name")
        self.weekly_view.heading("Task", text="Task")
        self.weekly_view.heading("Score", text="Score")
        self.weekly_view.pack(fill=tk.BOTH, expand=True)

        ttk.Button(weekly_frame, text="Refresh Weekly View", command=self.update_weekly_view).pack(pady=10)

    def setup_page2(self):
        ttk.Button(self.page2, text="Check Weekly Scores", command=self.check_weekly_scores).pack(pady=10)
        ttk.Button(self.page2, text="Export to Excel", command=self.export_to_excel).pack(pady=10)

    def init_db(self):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date text,
                    name text,                  
                    task text,
                    score integer,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def add_task(self):
        local_tz = pytz.timezone('Asia/Taipei')
        local_time = datetime.now(local_tz)
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (date, name, task, score, created_at)
                    VALUES (?,?,?,?,?)""", (
            self.date_entry.get_date().strftime('%Y-%m-%d'),
            self.name_entry.get(),
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
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        c.execute("SELECT date, name, task, score FROM tasks WHERE date BETWEEN ? AND ?", 
                  (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
        for row in c.fetchall():
            self.weekly_view.insert("", "end", values=row)
        conn.close()

    def check_weekly_scores(self):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        c.execute("SELECT name, SUM(score) FROM tasks WHERE date BETWEEN ? AND ? GROUP BY name", 
                  (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
        results = c.fetchall()
        conn.close()

        # Display results in a new window
        result_window = tk.Toplevel(self.master)
        result_window.title("Weekly Scores")
        for name, score in results:
            ttk.Label(result_window, text=f"{name}: {score}").pack()

    def export_to_excel(self):
        conn = sqlite3.connect('tasks.db')
        df = pd.read_sql_query("SELECT * FROM tasks", conn)
        conn.close()

        # Export to Excel
        df.to_excel("tasks_export.xlsx", index=False)
        tk.messagebox.showinfo("Export Successful", "Data has been exported to tasks_export.xlsx")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskToolGUI(root)
    root.mainloop()
