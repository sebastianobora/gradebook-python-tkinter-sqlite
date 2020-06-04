import tkinter as tk
import unittest

import gradebook


class MainWindowTests(unittest.TestCase):
    wrong_login = "wrongLogin"
    wrong_password = "wrongPassword"
    correct_login = "11"
    correct_password = "1"

    def setUp(self):
        self.root = tk.Tk()
        self.main_window = gradebook.MainWindow(self.root)
        self.main_window.login_main()

    def test_password_is_incorrect(self):
        log_data = self.main_window.db.check_password(self.wrong_login, self.wrong_password)
        self.assertTrue(log_data is None)

    def test_password_is_correct(self):
        # admin login and password
        log_data = self.main_window.db.check_password(self.correct_login, self.correct_password)
        self.assertTrue(log_data is not None)

    def test_entries_are_clear_after_wrong_password(self):
        self.main_window.login_entry.insert(tk.END, self.wrong_login)
        self.main_window.password_entry.insert(tk.END, self.wrong_password)
        self.main_window.log_in()
        self.assertFalse(
            self.main_window.login_entry.get() and self.main_window.password_entry.get())

    def test_log_in_with_no_login_password(self):
        self.main_window.log_in()
        self.assertFalse(gradebook.CURR_ID)

    def test_admin_perm_is_correct(self):
        # log on user with perm = 2 (admin)
        log_data = self.main_window.db.check_password("11", "1")
        self.assertTrue(log_data[0] == self.main_window.ADMIN_PERM)

    def test_teacher_perm_is_correct(self):
        # log on user with perm = 1 (teacher)
        log_data = self.main_window.db.check_password("kpalka", "matematyka")
        self.assertTrue(log_data[0] == self.main_window.TEACHER_PERM)

    def test_student_perm_is_correct(self):
        # log on user with perm = 0 (student)
        log_data = self.main_window.db.check_password("mmatczak", "mata123")
        self.assertTrue(log_data[0] == self.main_window.STUDENT_PERM)


if __name__ == '__main__':
    unittest.main()
