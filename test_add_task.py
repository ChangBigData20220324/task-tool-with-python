import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from datetime import datetime
from task_tool import TaskToolGUI

class TestAddTask(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = TaskToolGUI(self.root)

    @patch('task_tool.sqlite3.connect')
    @patch('task_tool.messagebox.showinfo')
    @patch('task_tool.TaskToolGUI.get_user_id')
    def test_add_task_success(self, mock_get_user_id, mock_showinfo, mock_connect):
        # Setup
        mock_get_user_id.return_value = 1
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        self.app.date_entry.set_date(datetime(2023, 5, 25))
        self.app.name_entry.insert(0, '  ')
        self.app.task_content.insert(tk.END, 'Test Task')
        self.app.score_entry.insert(0, '5')

        # Action
        self.app.add_task()

        # Assert
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_showinfo.assert_called_once_with("Success", "Task added successfully!")

    def tearDown(self):
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
