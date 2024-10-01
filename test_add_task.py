import unittest
from unittest.mock import patch
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from task_tool import TaskToolGUI

class TestTaskToolGUI(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = TaskToolGUI(self.root)  # 初始化你的GUI類別

    @patch('task_tool.messagebox.showinfo')
    @patch('task_tool.TaskToolGUI.get_user_id')
    @patch('task_tool.sqlite3.connect')
    def test_add_task_success(self, mock_connect, mock_get_user_id, mock_showinfo):
        """測試成功新增任務"""
        mock_get_user_id.return_value = 1  # 模擬使用者存在於資料庫中
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        # 設定模擬輸入
        self.app.date_entry.set_date(datetime(2024, 1, 1))
        self.app.name_entry.insert(0, 'user')
        self.app.task_content.insert(tk.END, 'Test ')
        self.app.score_entry.insert(0, '1')

        # 執行 add_task 方法
        self.app.add_task()

        # 檢查是否呼叫了正確的 SQL 命令和參數
        mock_cursor.execute.assert_called_once_with(
            """INSERT INTO tasks (date, users_id, task, score, created_at)
                    VALUES (?,?,?,?,?)""",
            ('2024-01-01', 1, 'Test task', '3', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        mock_connection.commit.assert_called_once()  # 檢查是否有 commit

        # 檢查是否顯示成功訊息
        mock_showinfo.assert_called_once_with("Success", "Task added successfully!")

    @patch('task_tool.messagebox.showerror')
    @patch('task_tool.TaskToolGUI.get_user_id')
    def test_add_task_user_not_found(self, mock_get_user_id, mock_showerror):
        """測試使用者不存在於資料庫中的情況"""
        mock_get_user_id.return_value = None  # 模擬使用者不存在

        # 設定模擬輸入
        self.app.name_entry.insert(0, 'nonexistentuser')

        # 執行 add_task 方法
        self.app.add_task()

        # 檢查是否顯示錯誤訊息
        mock_showerror.assert_called_once_with("Error", "User not found in the database.")

if __name__ == '__main__':
    unittest.main()
