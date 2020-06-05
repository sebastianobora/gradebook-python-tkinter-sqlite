import tkinter as tk
import unittest

import gradebook


class MainWindowTests(unittest.TestCase):
    WRONG_LOGIN = "wrongLogin"
    WRONG_PASSWORD = "wrongPassword"
    CORRECT_LOGIN = "11"
    CORRECT_PASSWORD = "1"

    def setUp(self):
        self.root = tk.Tk()
        self.main_window = gradebook.MainWindow(self.root)
        self.main_window.login_main()

    def test_password_is_incorrect(self):
        log_data = self.main_window.db.check_password(self.WRONG_LOGIN, self.WRONG_PASSWORD)
        self.assertIsNone(log_data)

    def test_password_is_correct(self):
        # admin login and password
        log_data = self.main_window.db.check_password(self.CORRECT_LOGIN, self.CORRECT_PASSWORD)
        self.assertIsNotNone(log_data)

    def test_entries_are_clear_after_wrong_password(self):
        self.main_window.login_entry.insert(tk.END, self.WRONG_LOGIN)
        self.main_window.password_entry.insert(tk.END, self.WRONG_PASSWORD)
        self.main_window.log_in()
        self.assertFalse(self.main_window.login_entry.get())
        self.assertFalse(self.main_window.password_entry.get())

    def test_log_in_with_no_login_password(self):
        self.main_window.log_in()
        self.assertFalse(gradebook.CURR_ID)

    def test_admin_perm_is_correct(self):
        # log on user with perm = 2 (admin)
        log_data = self.main_window.db.check_password("11", "1")
        self.assertEqual(log_data[0], self.main_window.ADMIN_PERM)

    def test_teacher_perm_is_correct(self):
        # log on user with perm = 1 (teacher)
        log_data = self.main_window.db.check_password("kpalka", "matematyka")
        self.assertEqual(log_data[0], self.main_window.TEACHER_PERM)

    def test_student_perm_is_correct(self):
        # log on user with perm = 0 (student)
        log_data = self.main_window.db.check_password("mmatczak", "mata123")
        self.assertEqual(log_data[0], self.main_window.STUDENT_PERM)


if __name__ == '__main__':
    unittest.main()
