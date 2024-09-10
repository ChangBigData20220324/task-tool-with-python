import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import pytz

class TaskToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Daily Task Recorder")
        master.geometry("1000x600")

        # Create main frame
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Input fields
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Input fields
        ttk.Label(input_frame, text="Settlement Date:").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(input_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=1, column=1, sticky="we", pady=5)

        ttk.Label(input_frame, text="Supervisor:").grid(row=2, column=0, sticky="w", pady=5)
        self.supervisor_entry = ttk.Entry(input_frame)
        self.supervisor_entry.insert(0, "陳煜騰")  # Set default value to "陳煜騰"
        self.supervisor_entry.grid(row=2, column=1, sticky="we", pady=5)

        ttk.Label(input_frame, text="Task Content:").grid(row=3, column=0, sticky="w", pady=5)
        self.task_content = tk.Text(input_frame, height=5)
        self.task_content.grid(row=3, column=1, sticky="we", pady=5)

        ttk.Label(input_frame, text="Score:").grid(row=4, column=0, sticky="w", pady=5)
        self.score_entry = ttk.Entry(input_frame)
        self.score_entry.insert(0, "1")  # Set default value to "1"
        self.score_entry.grid(row=4, column=1, sticky="we", pady=5)

        # Buttons
        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=5, column=0, pady=10)
        ttk.Button(input_frame, text="Supervisor Add", command=self.supervisor_add).grid(row=5, column=1, pady=10)
        ttk.Button(input_frame, text="Show All Data", command=self.query_all_data).grid(row=6, column=0, columnspan=2, pady=10)
        # Right side: Dashboard
        dashboard_frame = ttk.Frame(main_frame)
        dashboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(dashboard_frame, text="Dashboard").pack()
        self.dashboard = ttk.Treeview(dashboard_frame, columns=("ID", "Date", "Name", "Task", "Score", "Created At"), show="headings")
        self.dashboard.heading("ID", text="ID")
        self.dashboard.heading("Date", text="Date")
        self.dashboard.heading("Name", text="Name")
        self.dashboard.heading("Task", text="Task")
        self.dashboard.heading("Score", text="Score")
        self.dashboard.heading("Created At", text="Created At")
        self.dashboard.pack(fill=tk.BOTH, expand=True)



        # Initialize database
        self.init_db()
        self.update_dashboard()

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
        local_tz = pytz.timezone('Asia/Taipei')  # 例如，'Asia/Taipei'
        local_time = datetime.now(local_tz)
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (date, name,  task, score, created_at)
                    VALUES (?,?,?,?,?)""", (
            self.date_entry.get_date().strftime('%Y-%m-%d'),
            self.name_entry.get(),
            self.task_content.get("1.0", tk.END).strip(),
            self.score_entry.get(),
            local_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()
        self.update_dashboard()



    def supervisor_add(self):
        # Similar to add_task, but you might want to add some validation or different behavior
        self.add_task()

    def update_dashboard(self):
        for i in self.dashboard.get_children():
            self.dashboard.delete(i)

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT id, date, name,  task, score, created_at FROM tasks WHERE date=?", (self.date_entry.get_date().strftime('%Y-%m-%d'),))
        for row in c.fetchall():
            self.dashboard.insert("", "end", values=row)
        conn.close()

    
    def query_all_data(self):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT id, date, name,  task, score, created_at FROM tasks")
        all_data = c.fetchall()
        conn.close()

        for i in self.dashboard.get_children():
            self.dashboard.delete(i)

        for row in all_data:
            self.dashboard.insert("", "end", values=row)

        print("All data retrieved from the database and displayed in the dashboard.")



if __name__ == "__main__":
    root = tk.Tk()
    app = TaskToolGUI(root)
    root.mainloop()
