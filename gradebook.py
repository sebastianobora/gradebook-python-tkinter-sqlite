import copy
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import db_admin

# == Constants ==
CURR_ID = None

# colours

FRAME_BACKGROUND_COLOUR = "PeachPuff3"
CHECKBUTTON_BACKGROUND_COLOUR = "PeachPuff3"
LABEL_BACKGROUND_COLOUR = "PeachPuff3"
BUTTON_BACKGROUND_COLOUR = "white"
LABEL_FOREGROUND_COLOUR = "black"
INFO_BACKGROUND_COLOUR = "lightgrey"

# fonts
FONT_SETTINGS_0 = ('bold', 14)
FONT_SETTINGS_1 = ('bold', 12)
FONT_SETTINGS_2 = ('bold', 11)

# frame size
FRAME_SIZE = "766x335"

# frame title
FRAME_TITLE = "Gradebook"


class AbsentLateException(Exception):
    """Exception that raise, when teacher want to check late to absent student"""

    def __str__(self):
        return 'Absent student cant have late!'


def my_exit():
    """My exit with messagebox."""
    if messagebox.askyesno('Exit?', 'Are you sure?'):
        sys.exit()


class MainWindow:
    """Class that contain main window of application and login methods."""

    def __init__(self, master):
        """MainWindow init method."""
        self.frame = master
        # create window object
        self.frame.title(FRAME_TITLE)
        self.frame.geometry(FRAME_SIZE)
        self.frame.configure(background=FRAME_BACKGROUND_COLOUR)
        self.ADMIN_PERM = 2
        self.TEACHER_PERM = 1
        self.STUDENT_PERM = 0
        self.db = db_admin.DatabaseManagementClass('gradebook.db')

    def clear_frame(self):
        """Method that clear frame."""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def log_out(self):
        """Method that logout user from panel."""
        if messagebox.askyesno('Logout?', 'Are you sure?'):
            self.clear_frame()
            MainWindow(self.frame).login_main()

    def log_in(self):
        """Login management method,
        perm = 0 -> student,
        perm = 1 -> teacher,
        perm = 2 -> admin."""
        try:
            self.log_data = self.db.check_password(self.login_text.get(), self.password_text.get())
            global CURR_ID
            if self.log_data is not None:
                CURR_ID = self.log_data[1]
                if self.log_data[0] == self.ADMIN_PERM:
                    self.clear_frame()
                    Admin(self.frame).admin_main()
                elif self.log_data[0] == self.TEACHER_PERM:
                    self.clear_frame()
                    Teacher(self.frame).teacher_main()
                elif self.log_data[0] == self.STUDENT_PERM:
                    self.clear_frame()
                    Student(self.frame).student_main()
            else:
                messagebox.showerror("Warning", "Wrong login or password!")
                self.login_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
        except AttributeError:
            pass

    def login_main(self):
        """Method that creates login GUI elements."""
        # login and password buttons
        self.login_text = tk.StringVar()
        self.login_l = tk.Label(self.frame, text='Login', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.login_l.place(x=220, y=120)
        self.login_entry = tk.Entry(self.frame, textvariable=self.login_text)
        self.login_entry.place(x=300, y=122)

        self.password_text = tk.StringVar()
        self.password_l = tk.Label(self.frame, text='Password', bg=LABEL_BACKGROUND_COLOUR,
                                   fg=LABEL_FOREGROUND_COLOUR,
                                   font=FONT_SETTINGS_1)
        self.password_l.place(x=220, y=150)
        self.password_entry = tk.Entry(self.frame, show='*', textvariable=self.password_text)
        self.password_entry.place(x=300, y=152)
        # exit & log in buttons
        self.exit_button = tk.Button(self.frame, text='Exit', width=6, command=my_exit,
                                     bg=BUTTON_BACKGROUND_COLOUR)
        self.exit_button.place(x=714, y=2)

        self.login_button = tk.Button(self.frame, text='LOG IN', width=6, height=3,
                                      command=self.log_in, bg=BUTTON_BACKGROUND_COLOUR)
        self.login_button.place(x=430, y=119)


class Admin(MainWindow):
    """Admin management class."""

    def admin_main(self):
        """Method that creates admin main GUI elements."""
        # head label
        self.head_l = tk.Label(self.frame, text='admin', bg=INFO_BACKGROUND_COLOUR,
                               fg=LABEL_FOREGROUND_COLOUR,
                               font=FONT_SETTINGS_0)
        self.head_l.place(x=0, y=0)
        # login button
        self.personal_btn = tk.Button(self.frame, text='1. Manage personal data    ', width=22,
                                      command=self.go_to_data_manage, bg=BUTTON_BACKGROUND_COLOUR)
        self.personal_btn.place(x=290, y=123)
        # password button
        self.class_subj = tk.Button(self.frame, text='2. Manage class & subjects', width=22,
                                    command=self.go_to_add_class_subj, bg=BUTTON_BACKGROUND_COLOUR)
        self.class_subj.place(x=290, y=153)
        # log out button
        self.logout_button = tk.Button(self.frame, text='Log out', width=6, command=self.log_out,
                                       bg=BUTTON_BACKGROUND_COLOUR)
        self.logout_button.place(x=714, y=2)

    # admin main functions

    def go_to_data_manage(self):
        """Go to method, that clear frame and move user to data management frame."""
        self.clear_frame()
        Admin(self.frame).admin_db_manage()

    def go_to_add_class_subj(self):
        """Go to method, that clear frame and move user to class management frame."""
        self.clear_frame()
        Admin(self.frame).admin_add_class_subject()

    def go_to_menu(self):
        """Go to method, that clear frame and move user to admin menu frame."""
        self.clear_frame()
        Admin(self.frame).admin_main()

    # admin database manage panel

    def admin_db_manage(self):
        """Method that calls other methods, that are responsible for GUI elements in data
        management frame."""
        self.gui_admin_db()
        self.tree_admin_db()
        self.buttons_admin_db()
        self.show_list()

    # help functions for admin_db_manage

    def gui_admin_db(self):
        """Method that creates admin database management GUI elements: entries, labels."""
        # text and entry windows
        self.name_text = tk.StringVar()
        self.name_l = tk.Label(self.frame, text='First name:', bg=LABEL_BACKGROUND_COLOUR,
                               fg=LABEL_FOREGROUND_COLOUR,
                               font=FONT_SETTINGS_1)
        self.name_l.place(x=0, y=0)

        self.name_entry = tk.Entry(self.frame, textvariable=self.name_text)
        self.name_entry.place(x=100, y=4)

        self.lname_text = tk.StringVar()
        self.lname_l = tk.Label(self.frame, text='Last name:', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.lname_l.place(x=250, y=0)

        self.lname_entry = tk.Entry(self.frame, textvariable=self.lname_text)
        self.lname_entry.place(x=380, y=4)

        self.email_text = tk.StringVar()
        self.email_l = tk.Label(self.frame, text='Email:', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.email_l.place(x=0, y=30)

        self.email_entry = tk.Entry(self.frame, textvariable=self.email_text)
        self.email_entry.place(x=100, y=34)

        self.phone_text = tk.StringVar()
        self.phone_l = tk.Label(self.frame, text='Phone number:', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.phone_l.place(x=250, y=30)

        self.phone_entry = tk.Entry(self.frame, textvariable=self.phone_text)
        self.phone_entry.place(x=380, y=34)

        self.pesel_text = tk.StringVar()
        self.pesel_l = tk.Label(self.frame, text='Pesel:', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.pesel_l.place(x=0, y=60)

        self.pesel_entry = tk.Entry(self.frame, textvariable=self.pesel_text)
        self.pesel_entry.place(x=100, y=64)

        self.birth_text = tk.StringVar()
        self.birth_l = tk.Label(self.frame, text='Date of birth:', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_1)
        self.birth_l.place(x=250, y=60)

        self.birth_entry = tk.Entry(self.frame, textvariable=self.birth_text)
        self.birth_entry.place(x=380, y=64)

    def buttons_admin_db(self):
        """Method that creates admin database management GUI elements: buttons, entries, labels."""
        # checkbutton
        self.perm_chck_l = tk.Label(self.frame, text='Teacher:', bg=LABEL_BACKGROUND_COLOUR,
                                    fg=LABEL_FOREGROUND_COLOUR,
                                    font=FONT_SETTINGS_1)
        self.perm_chck_l.place(x=0, y=90)

        self.perm = tk.IntVar()
        self.perm_chck = tk.Checkbutton(self.frame, variable=self.perm,
                                        bg=CHECKBUTTON_BACKGROUND_COLOUR,
                                        cursor='plus',
                                        activebackground=CHECKBUTTON_BACKGROUND_COLOUR)
        self.perm_chck.place(x=95, y=91)

        # buttons
        self.add_button = tk.Button(self.frame, text='Add user', width=12, command=self.add_user,
                                    bg=BUTTON_BACKGROUND_COLOUR)
        self.add_button.place(x=585, y=2)

        self.del_button = tk.Button(self.frame, text='Delete user', width=12,
                                    command=self.delete_user, bg=BUTTON_BACKGROUND_COLOUR)
        self.del_button.place(x=585, y=32)

        self.update_button = tk.Button(self.frame, text='Update data', width=12,
                                       command=self.update_user, bg=BUTTON_BACKGROUND_COLOUR)
        self.update_button.place(x=585, y=62)

        # search machine button
        self.search_button = tk.Button(self.frame, text='Search', width=10,
                                       command=self.search_using_pesel, bg=BUTTON_BACKGROUND_COLOUR)
        self.search_button.place(x=335, y=121)

        self.search_label = tk.Label(self.frame, text='SEARCH USING PESEL',
                                     bg=LABEL_BACKGROUND_COLOUR,
                                     fg=LABEL_FOREGROUND_COLOUR,
                                     font=FONT_SETTINGS_1)
        self.search_label.place(x=0, y=122)

        self.search_text = tk.StringVar()
        self.search_entry = tk.Entry(self.frame, textvariable=self.search_text)
        self.search_entry.place(x=190, y=124)

        # clear fields button
        self.clear_field_button = tk.Button(self.frame, text='Clear fields', width=12,
                                            command=self.rmv_windows_data,
                                            bg=BUTTON_BACKGROUND_COLOUR)
        self.clear_field_button.place(x=585, y=121)

        # default password button
        self.default_pass_button = tk.Button(self.frame, text='Default pass', width=12,
                                             command=self.set_default_password,
                                             bg=BUTTON_BACKGROUND_COLOUR)
        self.default_pass_button.place(x=585, y=91)

        # go back button
        self.exit_button = tk.Button(self.frame, text='Go back', width=6, command=self.go_to_menu,
                                     bg=BUTTON_BACKGROUND_COLOUR)
        self.exit_button.place(x=714, y=2)

    def tree_admin_db(self):
        """Method that creates Treeview on users personal information's"""
        self.columns = (
            'ID', 'Name', 'Last name', 'Password', 'Login', 'Email', 'Phone', 'Pesel',
            'Date of birth', 'Perm')
        self.columns_size = [(25, 25), (80, 80), (80, 80), (80, 80), (80, 80), (140, 140), (67, 67),
                             (78, 78), (75, 75),
                             (39, 39)]

        # tree
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show='headings', height=7,
                                 selectmode=None)
        self.tree.place(x=0, y=150)

        for cols, width in zip(self.columns, self.columns_size):
            self.tree.column(cols, minwidth=width[0], width=width[1], anchor=tk.W)
            self.tree.heading(cols, text=cols)

        # scroll y
        self.scroll_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_y.place(in_=self.tree, relx=1.0, relheight=1.0)
        self.scroll_y.configure(command=self.tree.yview)

        # scroll x
        self.scroll_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_x.place(in_=self.tree, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_x.configure(command=self.tree.xview)

        # configuration of scrolls

        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.tree.configure(yscrollcommand=self.scroll_y.set)
        self.tree.bind('<ButtonRelease-1>', self.selected_user)

    def add_user(self):
        """Method, that adds user to database."""
        if not self.name_text.get() \
                or not self.lname_text.get() \
                or not self.email_text.get() \
                or not self.phone_text.get() \
                or not self.pesel_text.get() \
                or not self.birth_text.get():
            messagebox.showerror("Warning", "Fill all fields!")
        elif len(self.birth_text.get()) != 10:
            messagebox.showerror("Error!", "Wrong date!\nformat is:\nYYYY-MM-DD")
        elif len(self.pesel_text.get()) != 11:
            messagebox.showerror("Error!", "Wrong pesel!")
        else:
            try:
                self.db.add_user(self.name_text.get(), self.lname_text.get(), self.email_text.get(),
                                 self.phone_text.get(),
                                 self.pesel_text.get(), self.birth_text.get(), self.perm.get())
            except sqlite3.IntegrityError:
                messagebox.showerror("Error!",
                                     "Someone already has the same:\n pesel or\nphone number or\n "
                                     "email!")
            self.rmv_windows_data()
            self.show_list()

    def show_list(self):
        """Method, that put data into users information's Treeview"""
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for element in self.db.fetch():
                self.tree.insert('', tk.END, values=element)
        except KeyError:
            pass

    def delete_user(self):
        """Method, that delete selected user from database."""
        try:
            self.db.delete_user(self.select_user[self.columns[0]])  # columns[0] is id
            self.rmv_windows_data()
            self.show_list()
        except AttributeError:
            pass

    def update_user(self):
        """Method that updates user's data."""
        try:
            self.db.update_user(self.select_user[self.columns[0]], self.name_text.get(),
                                self.lname_text.get(),
                                self.email_text.get(), self.phone_text.get(), self.pesel_text.get(),
                                self.birth_text.get(),
                                self.perm.get())
            self.show_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Warning!", "Wrong data!")
        except AttributeError:
            pass

    def selected_user(self, event):
        """Treeview select method."""
        try:
            self.select_user = self.tree.set(self.tree.selection())
            self.rmv_windows_data()
            self.put_windows_data(self.select_user)
        except KeyError:
            pass
        except tk.TclError:
            pass

    def rmv_windows_data(self):
        """Method that remove all data's from entries."""
        # windows
        self.name_entry.delete(0, tk.END)
        self.lname_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.pesel_entry.delete(0, tk.END)
        self.birth_entry.delete(0, tk.END)
        # checkbutton
        self.perm_chck.deselect()

    def put_windows_data(self, user):
        """Method that put data into entries, when we select record."""
        # ind = 0 is a id, we jump over that
        self.name_entry.insert(tk.END, user[self.columns[1]])
        self.lname_entry.insert(tk.END, user[self.columns[2]])
        self.email_entry.insert(tk.END, user[self.columns[5]])
        self.phone_entry.insert(tk.END, user[self.columns[6]])
        self.pesel_entry.insert(tk.END, user[self.columns[7]])
        self.birth_entry.insert(tk.END, user[self.columns[8]])
        if int(user[self.columns[9]]) == 0 or int(user[self.columns[9]]) == 2:
            self.perm_chck.deselect()
        elif int(user[self.columns[9]]) == 1:
            self.perm_chck.select()

    def put_windows_pesel_search(self, user):
        """Method that puts data into entries, when user is using "pesel search"."""
        # ind = 0 is a id, we jump over that
        self.name_entry.insert(tk.END, user[1])
        self.lname_entry.insert(tk.END, user[2])
        self.email_entry.insert(tk.END, user[5])
        self.phone_entry.insert(tk.END, user[6])
        self.pesel_entry.insert(tk.END, user[7])
        self.birth_entry.insert(tk.END, user[8])
        if int(user[9]) == 0 or int(user[9]) == 2:
            self.perm_chck.deselect()
        elif int(user[9]) == 1:
            self.perm_chck.select()

    def search_using_pesel(self):
        """Searching user using pesel."""
        data = self.db.select_by_pesel(self.search_text.get())
        if len(self.search_text.get()) == 11 and data is not None:
            self.rmv_windows_data()
            self.put_windows_pesel_search(data)
            self.search_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Warning!", "Pesel is wrong!")

    def set_default_password(self):
        """Method that reset password - default password is a pesel."""
        try:
            self.db.default_password(self.select_user[self.columns[0]],
                                     self.select_user[self.columns[7]])
            self.show_list()
        except AttributeError:
            pass

    # Add class and subject panel
    def admin_add_class_subject(self):
        """Method that create "add class and subject to users" window, contain:
        - labels
        - entries
        - treeviews
        - buttons."""
        # class and subject windows
        self.class_text = tk.StringVar('')
        self.class_l = tk.Label(self.frame, text='Class', bg=LABEL_BACKGROUND_COLOUR,
                                fg=LABEL_FOREGROUND_COLOUR,
                                font=FONT_SETTINGS_2)
        self.class_l.place(x=0, y=30)

        self.class_entry = tk.Entry(self.frame, textvariable=self.class_text)
        self.class_entry.place(x=65, y=32)

        self.subject_text = tk.StringVar('')
        self.subject_l = tk.Label(self.frame, text='Subject', bg=LABEL_BACKGROUND_COLOUR,
                                  fg=LABEL_FOREGROUND_COLOUR,
                                  font=FONT_SETTINGS_2)
        self.subject_l.place(x=0, y=4)

        self.subject_entry = tk.Entry(self.frame, textvariable=self.subject_text)
        self.subject_entry.place(x=65, y=8)

        # users info

        self.columns_u = (
            'ID', 'Perm', 'Name', 'Last name', 'Pesel', 'Date of birth', 'Subject', 'Class')
        self.columns_u_size = [(30, 30), (40, 40), (85, 85), (85, 85), (80, 80), (75, 75), (90, 90),
                               (50, 50)]

        self.tree_u = ttk.Treeview(self.frame, columns=self.columns_u, show='headings', height=8)
        self.tree_u.place(x=0, y=130)

        for cols, width in zip(self.columns_u, self.columns_u_size):
            self.tree_u.column(cols, minwidth=width[0], width=width[1], anchor=tk.CENTER)
            self.tree_u.heading(cols, text=cols)

        # scroll y
        self.scroll_u_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_u_y.place(in_=self.tree_u, relx=1.0, relheight=1.0)
        self.scroll_u_y.configure(command=self.tree_u.yview)
        # scroll x
        self.scroll_u_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_u_x.place(in_=self.tree_u, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_u_x.configure(command=self.tree_u.xview)
        # configuration of scrolls
        self.tree_u.configure(xscrollcommand=self.scroll_u_x.set)
        self.tree_u.configure(yscrollcommand=self.scroll_u_y.set)
        self.tree_u.bind('<ButtonRelease-1>', self.multi_select_user_u)

        # subject & class
        self.columns_us = ('ID', 'Subject', 'Class')
        self.columns_us_size = [(30, 30), (100, 100), (55, 55)]

        self.tree_us = ttk.Treeview(self.frame, columns=self.columns_us, show='headings', height=8)
        self.tree_us.place(x=560, y=130)

        for cols, width in zip(self.columns_us, self.columns_us_size):
            self.tree_us.column(cols, minwidth=width[0], width=width[1], anchor=tk.CENTER)
            self.tree_us.heading(cols, text=cols)

        # scroll y
        self.scroll_us_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_us_y.place(in_=self.tree_us, relx=1.0, relheight=1.0)
        self.scroll_us_y.configure(command=self.tree_us.yview)
        # scroll x
        self.scroll_us_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_us_x.place(in_=self.tree_us, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_us_x.configure(command=self.tree_us.xview)
        # configuration of scrolls
        self.tree_us.configure(xscrollcommand=self.scroll_us_x.set)
        self.tree_us.configure(yscrollcommand=self.scroll_us_y.set)
        self.tree_us.bind('<ButtonRelease-1>', self.multi_select_us)

        # show
        self.show_list_u()
        self.show_list_us()

        # buttons
        self.add_sub_button = tk.Button(self.frame, text='Add subject\nand class', width=12,
                                        height=2,
                                        command=self.add_class, bg='snow')
        self.add_sub_button.place(x=195, y=10)

        # search machine button
        self.search_button = tk.Button(self.frame, text='Search', width=12,
                                       command=self.search_using_year, bg='snow')
        self.search_button.place(x=195, y=94)

        self.search_label = tk.Label(self.frame, text='Search by year', bg=LABEL_BACKGROUND_COLOUR,
                                     fg=LABEL_FOREGROUND_COLOUR,
                                     font=FONT_SETTINGS_2)
        self.search_label.place(x=0, y=94)

        self.search_text = tk.StringVar()
        self.search_entry = tk.Entry(self.frame, textvariable=self.search_text, width=13)
        self.search_entry.place(x=106, y=97)

        # show all
        self.show_button = tk.Button(self.frame, text='Show All', width=12,
                                     command=self.show_list_u, bg='snow')
        self.show_button.place(x=295, y=94)
        # join users and subjects
        self.join_button = tk.Button(self.frame, text='Join user-subject/s', width=17,
                                     command=self.join_user_subject,
                                     bg='snow')
        self.join_button.place(x=395, y=94)

        # disjoin users and subjects
        self.disjoin_button = tk.Button(self.frame, text='Disjoin user-subject/s', width=17,
                                        command=self.disjoin_user_subject,
                                        bg='snow')
        self.disjoin_button.place(x=530, y=94)

        # remove class
        self.rmv_class_button = tk.Button(self.frame, text='Remove class', width=12,
                                          command=self.rmv_class,
                                          bg='snow')
        self.rmv_class_button.place(x=665, y=94)

        # go back button
        self.exit_button = tk.Button(self.frame, text='Go back', width=6, command=self.go_to_menu,
                                     bg='snow')
        self.exit_button.place(x=714, y=2)

    # help functions for admin_add_class_subject

    def multi_select_user_u(self, event):
        """Treeview multi selection method - users."""
        if self.tree_u.selection() != ():
            temp_list_of_dict_users = [self.tree_u.set(i) for i in self.tree_u.selection()]
            self.selected_usr = copy.deepcopy(temp_list_of_dict_users)

    def multi_select_us(self, event):
        """Treeview multi selection method - users - subjects."""
        if self.tree_us.selection() != ():
            temp_list_of_dict_subj = [self.tree_us.set(i) for i in self.tree_us.selection()]
            self.selected_sub = copy.deepcopy(temp_list_of_dict_subj)

    def show_list_u(self):
        """Show users list."""
        for i in self.tree_u.get_children():
            self.tree_u.delete(i)
        for element in self.db.fetch_class_subj():
            self.tree_u.insert('', tk.END, values=element)

    def show_list_us(self):
        """Show users - subject list"""
        for i in self.tree_us.get_children():
            self.tree_us.delete(i)
        for element in self.db.fetch_subjects():
            self.tree_us.insert('', tk.END, values=element)

    def rmv_class(self):
        """Method that remove selected class."""
        try:
            for my_dict in self.selected_sub:
                self.db.delete_class(my_dict[self.columns_us[0]])
            self.show_list_us()
            self.show_list_u()
        except AttributeError:
            pass

    def add_class(self):
        """Method that add selected class."""
        try:
            self.db.add_class(self.subject_text.get(), self.class_text.get())
            self.rmv_windows_class_subj()
            self.show_list_us()
        except ValueError:
            messagebox.showerror("Warning", "Wrong data!")

    def join_user_subject(self):
        """Method that connect users with subjects and class."""
        try:
            for sub in self.selected_sub:
                for usr in self.selected_usr:
                    try:
                        self.db.join_usr_subj(int(usr[self.columns_u[0]]),
                                              int(sub[self.columns_u[0]]))
                    except AttributeError:
                        my_err = "".join(["User with ID: ",
                                          usr[self.columns_u[0]],
                                          " is already connected with subject with ID: ",
                                          sub[self.columns_u[0]],
                                          " !"])
                        messagebox.showerror("Warning", my_err)
            self.show_list_u()
        except AttributeError:
            pass

    def disjoin_user_subject(self):
        """Method that disconnect users with subjects and class."""
        try:
            for usr in self.selected_usr:
                self.db.disjoin_user_subj(int(usr[self.columns_u[0]]), usr[self.columns_u[6]],
                                          usr[self.columns_u[7]])
            self.show_list_u()
        except AttributeError:
            pass

    def rmv_windows_class_subj(self):
        """Method that remove class and subject from entries."""
        # windows
        self.class_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)

    def is_int(self, x):
        """Method that check the object is int type or not."""
        try:
            float(x)
        except ValueError:
            return False
        else:
            return float(x).is_integer()

    def search_using_year(self):
        """Search users using year."""
        data = self.db.select_by_year(self.search_text.get())
        if data is not None and self.is_int(self.search_text.get()):
            self.search_entry.delete(0, tk.END)
            for i in self.tree_u.get_children():
                self.tree_u.delete(i)
            for element in data:
                self.tree_u.insert('', tk.END, values=element)
        else:
            messagebox.showerror("Warning!", "Year is wrong!")


class Teacher(MainWindow):
    """Teacher management class."""

    # teacher main
    def __init__(self, master):
        """Teacher init method."""
        super().__init__(master)
        self.DATE = 'Date'
        self.curr_s_and_c = None
        self.curr_s_id = None
        self.COLUMNS_A = None
        self.COLUMNS_A_SIZE = None

    def teacher_main(self):
        """Create teacher's main frame: combobox, labels, buttons."""
        # combobox subject
        self.subject_text = tk.StringVar()
        self.subject_text.set('Choose subject')
        self.subject_cb = ttk.Combobox(self.frame, textvariable=self.subject_text, justify='center',
                                       state='readonly')
        self.subject_cb['values'] = self.db.get_teacher_subjects(CURR_ID)
        self.subject_cb.bind('<<ComboboxSelected>>', self.get_chosen_subject_and_id)
        self.subject_cb.place(x=250, y=132)

        # head label
        self.head_l = tk.Label(self.frame, text='Teacher', bg=INFO_BACKGROUND_COLOUR,
                               fg=LABEL_FOREGROUND_COLOUR,
                               font=FONT_SETTINGS_0)
        self.head_l.place(x=0, y=0)

        # select button
        self.select = tk.Button(self.frame, text='Log in', width=15,
                                command=self.new_dates_and_go_to_manage, bg='snow')
        self.select.place(x=400, y=130)
        # change password button
        self.change_pass = tk.Button(self.frame, text='Change password', width=22,
                                     command=self.go_to_change_password, bg='snow')
        self.change_pass.place(x=602, y=309)
        # log out button
        self.logout_button = tk.Button(self.frame, text='Log out', width=6, command=self.log_out,
                                       bg='snow')
        self.logout_button.place(x=714, y=2)

    def go_to_main(self):
        """Go to main method."""
        self.clear_frame()
        self.teacher_main()

    # get selected subject and class
    def get_chosen_subject_and_id(self, event):
        """Method that assign variable current student id."""
        self.curr_s_and_c = self.subject_cb.get().split(" ")
        try:
            self.curr_s_id = \
                (self.db.get_curr_subj_id(self.curr_s_and_c[1], self.curr_s_and_c[0], CURR_ID))[0]
        except TypeError:
            messagebox.showerror("Error!", "System require 1 word class name!\nChange it!")
        # thats 1 el. tuple

    # change password functions
    def change_password_panel(self):
        """Create GUI to change password panel: buttons, labels."""
        # log out button
        self.go_main_butt = tk.Button(self.frame, text='Back', width=6, command=self.go_to_main,
                                      bg='snow')
        self.go_main_butt.place(x=714, y=2)

        self.change_butt = tk.Button(self.frame, text='Change', width=10, height=3,
                                     command=self.change_password,
                                     bg='snow')
        self.change_butt.place(x=470, y=99)

        self.type_label = tk.Label(self.frame, text='Type new password', bg=LABEL_BACKGROUND_COLOUR,
                                   fg=LABEL_FOREGROUND_COLOUR, font=FONT_SETTINGS_1)
        self.type_label.place(x=160, y=128)
        self.login_label = tk.Label(self.frame, text='Your login', bg=LABEL_BACKGROUND_COLOUR,
                                    fg=LABEL_FOREGROUND_COLOUR,
                                    font=FONT_SETTINGS_1)
        self.login_label.place(x=160, y=100)

        self.r_login_label = tk.Label(self.frame, text=self.db.get_login(CURR_ID), bg='snow',
                                      fg=LABEL_FOREGROUND_COLOUR,
                                      font=FONT_SETTINGS_2,
                                      width=14)
        self.r_login_label.place(x=320, y=100)

        self.pass_text = tk.StringVar()
        self.pass_entry = tk.Entry(self.frame, show='*', width=21, textvariable=self.pass_text)
        self.pass_entry.place(x=320, y=130)

    def change_password(self):
        """Change user password method."""
        if self.pass_text.get() and len(self.pass_text.get()) >= 6:
            self.db.change_password(CURR_ID, self.pass_text.get())
            self.pass_text.set('')
            self.pass_entry.delete(0, tk.END)
            messagebox.showinfo("Succes!", "Password has been changed!")
        else:
            self.pass_entry.delete(0, tk.END)
            messagebox.showerror("Warning!", "Password too short!\nminimum 6 characters")

    def go_to_change_password(self):
        """Go to change password panel method."""
        self.clear_frame()
        self.change_password_panel()

    # teacher manage panel
    def manage_panel(self):
        """Create GUI to main teacher panel: labels, buttons."""
        self.subject_class_info = "".join([self.curr_s_and_c[0], " ", self.curr_s_and_c[1]])
        self.sub_l = tk.Label(self.frame, text=self.subject_class_info, bg=INFO_BACKGROUND_COLOUR,
                              fg=LABEL_FOREGROUND_COLOUR,
                              font=FONT_SETTINGS_0)
        self.sub_l.place(x=0, y=0)

        self.attendance = tk.Button(self.frame, text='Attendance', width=15, command=self.date_tree,
                                    bg='snow')
        self.attendance.place(x=130, y=2)

        self.marks = tk.Button(self.frame, text='Marks', width=15, command=self.marks_manage,
                               bg='snow')
        self.marks.place(x=260, y=2)

        self.events = tk.Button(self.frame, text='Events', width=15, command=self.events_manage,
                                bg='snow')
        self.events.place(x=390, y=2)

        # log out button
        self.logout_button = tk.Button(self.frame, text='Go back', width=6, command=self.go_to_main,
                                       bg='snow')
        self.logout_button.place(x=714, y=2)

    # Attendance functions

    def go_to_manage_panel(self):
        """Go to main teacher panel method."""
        self.clear_frame()
        self.manage_panel()

    def new_dates_and_go_to_manage(self):
        """Method responsible for add new "date" (attendance, marks)
        every time, when teacher select and log in subject."""
        if self.subject_cb.get() != 'Choose subject':
            self.go_to_manage_panel()
            for i in self.db.get_students_subject_id(self.curr_s_id):
                self.db.new_datas(i[0], self.curr_s_id)
        else:
            messagebox.showerror("Warning!", "Select subject!")

    def check_attendance(self):
        """Create GUI to attendance panel: labels, treeview, buttons, checkbox."""
        # attendance treeview
        self.COLUMNS_A = ('ID', 'Name', 'Last name', 'Attendance', 'Late')
        self.COLUMNS_A_SIZE = [(30, 30), (105, 105), (105, 105), (80, 80), (40, 40)]

        self.tree_a = ttk.Treeview(self.frame, columns=self.COLUMNS_A, show='headings', height=10)
        self.tree_a.place(x=180, y=65)

        for cols, width in zip(self.COLUMNS_A, self.COLUMNS_A_SIZE):
            self.tree_a.column(cols, minwidth=width[0], width=width[1], anchor=tk.CENTER)
            self.tree_a.heading(cols, text=cols)

        # scroll y
        self.scroll_a_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_a_y.place(in_=self.tree_a, relx=1.0, relheight=1.0)
        self.scroll_a_y.configure(command=self.tree_a.yview)
        # scroll x
        self.scroll_a_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_a_x.place(in_=self.tree_a, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_a_x.configure(command=self.tree_a.xview)
        # configuration of scrolls
        self.tree_a.configure(xscrollcommand=self.scroll_a_x.set)
        self.tree_a.configure(yscrollcommand=self.scroll_a_y.set)
        self.tree_a.bind('<ButtonRelease-1>', self.selected_user_attendance)

        # present & absent

        self.present = tk.Button(self.frame, text='Present', width=8, command=self.set_present,
                                 bg='DarkOliveGreen1')
        self.present.place(x=590, y=80)

        self.absent = tk.Button(self.frame, text='Absent', width=8, command=self.set_absent,
                                bg='brown1')
        self.absent.place(x=670, y=80)

        # checkbutton
        self.late_chck_l = tk.Label(self.frame, text='Late?', bg=LABEL_BACKGROUND_COLOUR,
                                    fg=LABEL_FOREGROUND_COLOUR,
                                    font=FONT_SETTINGS_1)
        self.late_chck_l.place(x=590, y=120)

        self.late = tk.IntVar()
        self.late_chck = tk.Checkbutton(self.frame, variable=self.late,
                                        bg=CHECKBUTTON_BACKGROUND_COLOUR,
                                        cursor='plus',
                                        activebackground=CHECKBUTTON_BACKGROUND_COLOUR,
                                        command=self.set_late)
        self.late_chck.place(x=640, y=120)

        self.attendance_show()

    def date_tree(self):
        """Create treeview with dates (attendance panel)."""
        self.go_to_manage_panel()
        # attendance date
        self.tree_date = ttk.Treeview(self.frame, columns=self.DATE, show='headings', height=10)
        self.tree_date.place(x=10, y=65)

        self.tree_date.column('Date', minwidth='140', width='140', anchor=tk.CENTER)
        self.tree_date.heading('Date', text='Date')

        # scroll date y
        self.scroll_date_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_date_y.place(in_=self.tree_date, relx=1.0, relheight=1.0)
        self.scroll_date_y.configure(command=self.tree_date.yview)
        # scroll date x
        self.scroll_date_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_date_x.place(in_=self.tree_date, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_date_x.configure(command=self.tree_date.xview)
        # configuration of scrolls
        self.tree_date.configure(xscrollcommand=self.scroll_date_x.set)
        self.tree_date.configure(yscrollcommand=self.scroll_date_y.set)
        self.tree_date.bind('<ButtonRelease-1>', self.selected_date_attendance)

        self.load_data_tree()

    def load_data_tree(self):
        """Method that put data into treeview with data's."""
        for item in self.tree_date.get_children():
            self.tree_date.delete(item)
        for element in self.db.fetch_date(self.curr_s_id):
            self.tree_date.insert('', tk.END, values=element)

    def selected_user_attendance(self, event):
        """Method that get selected by teacher users (attendance panel)."""
        try:
            if self.tree_a.selection() is not None:
                temp_list_of_dict_subj = [self.tree_a.set(item) for item in self.tree_a.selection()]
                self.selected_att = copy.deepcopy(temp_list_of_dict_subj)
                if int(self.selected_att[0][self.COLUMNS_A[4]]) == 0:
                    self.late_chck.deselect()
                else:
                    self.late_chck.select()
        except KeyError:
            pass
        except IndexError:
            pass

    def selected_date_attendance(self, event):
        """Method that get selected by teacher date."""
        try:
            self.selected_date = self.tree_date.set(self.tree_date.selection())
            self.check_attendance()
        except KeyError:
            pass

    def set_present(self):
        """Method that set selected students present."""
        try:
            for select in self.selected_att:
                self.db.set_present(select[self.COLUMNS_A[0]], self.curr_s_id,
                                    self.selected_date[self.DATE])
            self.attendance_show()
        except AttributeError:
            pass

    def set_absent(self):
        """Method that set selected students absent."""
        try:
            for select in self.selected_att:
                self.db.set_absent(select[self.COLUMNS_A[0]], self.curr_s_id,
                                   self.selected_date[self.DATE])
            self.attendance_show()
        except AttributeError:
            pass

    def set_late(self):
        """Method that set selected students late."""
        try:
            for select in self.selected_att:
                att = self.db.fetch_att_student_date(select[self.COLUMNS_A[0]], self.curr_s_id,
                                                     self.selected_date[self.DATE])
                att = int(att[0][0])
                if att:
                    self.db.set_late(select[self.COLUMNS_A[0]], self.curr_s_id,
                                     self.selected_date[self.DATE],
                                     self.late.get())
                else:
                    self.late_chck.deselect()
                    raise AbsentLateException
        except AbsentLateException as err:
            messagebox.showwarning('Warning!', err)
            pass
        except AttributeError:
            pass
        finally:
            self.attendance_show()

    def attendance_show(self):
        """Method that put attendance informations into treeview."""
        for i in self.tree_a.get_children():
            self.tree_a.delete(i)
        for element in self.db.fetch_attendance(self.curr_s_id, self.selected_date[self.DATE]):
            self.tree_a.insert('', tk.END, values=element)

    # Events

    def events_manage(self):
        """Create events management panel: buttons, labels."""
        self.go_to_manage_panel()

        self.add_event_b = tk.Button(self.frame, text='Add event', width=11, command=self.add_event,
                                     bg='snow')
        self.add_event_b.place(x=655, y=62)

        self.del_event_b = tk.Button(self.frame, text='Delete event', width=11,
                                     command=self.del_event, bg='snow')
        self.del_event_b.place(x=19, y=62)

        self.event_text = tk.StringVar()
        self.event_entry = tk.Entry(self.frame, textvariable=self.event_text, width=86)
        self.event_entry.place(x=120, y=65)

        self.tree_event()
        self.show_events()

    def tree_event(self):
        """Create treeview for events."""
        # events
        self.tree_event_col = ['ID', 'Events']
        self.tree_event_tv = ttk.Treeview(self.frame, columns=self.tree_event_col, show='headings',
                                          height=10)
        self.tree_event_tv.place(x=120, y=90)
        self.tree_event_col_size = ((30, 30, tk.CENTER), (470, 470, tk.W))
        for size, col in zip(self.tree_event_col_size, self.tree_event_col):
            self.tree_event_tv.column(col, minwidth=size[0], width=size[1], anchor=size[2])
            self.tree_event_tv.heading(col, text=col)

        # scroll date y
        self.scroll_event_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_event_y.place(in_=self.tree_event_tv, relx=1.0, relheight=1.0)
        self.scroll_event_y.configure(command=self.tree_event_tv.yview)
        # scroll date x
        self.scroll_event_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_event_x.place(in_=self.tree_event_tv, rely=1.0, relwidth=1.0,
                                  bordermode="inside")
        self.scroll_event_x.configure(command=self.tree_event_tv.xview)
        # configuration of scrolls
        self.tree_event_tv.configure(xscrollcommand=self.scroll_event_x.set)
        self.tree_event_tv.configure(yscrollcommand=self.scroll_event_y.set)
        self.tree_event_tv.bind('<ButtonRelease-1>', self.select_events)

    def select_events(self, event):
        """Method that get selected events."""
        try:
            if self.tree_event_tv.selection() is not None:
                temp_list_of_dict_subj = [self.tree_event_tv.set(i) for i in
                                          self.tree_event_tv.selection()]
                self.selected_events = copy.deepcopy(temp_list_of_dict_subj)
        except KeyError:
            pass

    def show_events(self):
        """Method that put events into treeview."""
        for i in self.tree_event_tv.get_children():
            self.tree_event_tv.delete(i)
        for element in self.db.fetch_events(self.curr_s_id):
            self.tree_event_tv.insert('', tk.END, values=element)

    def add_event(self):
        """Method that add new event."""
        try:
            if self.event_entry.get():
                self.db.add_event(self.event_entry.get(), self.curr_s_id)
                self.event_entry.delete(0, tk.END)
                self.show_events()
        except AttributeError:
            pass

    def del_event(self):
        """Method that delete selected events."""
        try:
            for i in self.selected_events:
                self.db.del_event(i[self.tree_event_col[0]])
            self.show_events()
        except AttributeError:
            pass

    # Marks

    def marks_manage(self):
        """Create marks management frame: labels, buttons."""
        self.go_to_manage_panel()
        self.marks_tree()
        self.show_marks()

        self.mark_l = tk.Label(self.frame, text="Mark:", bg=INFO_BACKGROUND_COLOUR,
                               fg=LABEL_FOREGROUND_COLOUR,
                               font=FONT_SETTINGS_2)
        self.mark_l.place(x=680, y=70)

        self.add_mark_b = tk.Button(self.frame, text='Add mark', width=10, command=self.add_mark,
                                    bg='snow')
        self.add_mark_b.place(x=680, y=100)

        self.del_mark_b = tk.Button(self.frame, text='Del mark', width=10, command=self.del_mark,
                                    bg='snow')
        self.del_mark_b.place(x=599, y=100)

        self.mark_text = tk.StringVar()
        self.mark_entry = tk.Entry(self.frame, textvariable=self.mark_text, width=6)
        self.mark_entry.place(x=720, y=72)

    def marks_tree(self):
        """Create treeview for marks."""
        self.go_to_manage_panel()
        # attendance treeview
        self.COLUMNS_M = ('ID', 'Name', 'Last name')
        self.COLUMNS_M_SIZE = [(30, 30), (105, 105), (105, 105)]
        self.how_much_grades = 11
        self.columns_marks = tuple(str(i) for i in range(self.how_much_grades))

        self.tree_m = ttk.Treeview(self.frame, columns=self.COLUMNS_M + self.columns_marks,
                                   show='headings', height=10)
        self.tree_m.place(x=2, y=65)

        for cols, width in zip(self.COLUMNS_M, self.COLUMNS_M_SIZE):
            self.tree_m.column(cols, minwidth=width[0], width=width[1], anchor=tk.CENTER)
            self.tree_m.heading(cols, text=cols)

        for i in range(self.how_much_grades):
            self.tree_m.column(str(i), minwidth=30, width=30, anchor=tk.CENTER)
            self.tree_m.heading(str(i), text=str(i))

        # scroll y
        self.scroll_m_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_m_y.place(in_=self.tree_m, relx=1.0, relheight=1.0)
        self.scroll_m_y.configure(command=self.tree_m.yview)
        # scroll x
        self.scroll_m_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_m_x.place(in_=self.tree_m, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_m_x.configure(command=self.tree_m.xview)
        # configuration of scrolls
        self.tree_m.configure(xscrollcommand=self.scroll_m_x.set)
        self.tree_m.configure(yscrollcommand=self.scroll_m_y.set)
        self.tree_m.bind('<ButtonRelease-1>', self.select_marks)

    def show_marks(self):
        """Method that put marks into treeview."""
        for i in self.tree_m.get_children():
            self.tree_m.delete(i)
        for s in self.db.fetch_students(self.curr_s_id):
            marks = self.db.fetch_marks(self.curr_s_id, s[0])
            self.tree_m.insert('', tk.END, values=s + marks)

    def select_marks(self, event):
        """Method that get selected by teacher users, that will get mark."""
        try:
            if self.tree_m.selection() is not None:
                temp_list_of_dict_subj = [self.tree_m.set(i) for i in self.tree_m.selection()]
                self.selected_marks = copy.deepcopy(temp_list_of_dict_subj)
        except KeyError:
            pass

    def add_mark(self):
        """Method that add marks to selected users."""
        try:
            if self.mark_entry.get():
                if 0.0 <= float(self.mark_entry.get()) <= 6.0:
                    for student_id in self.selected_marks:
                        self.db.add_mark(float(self.mark_entry.get()), self.curr_s_id,
                                         student_id[self.COLUMNS_M[0]])
                    self.mark_entry.delete(0, tk.END)
                    self.show_marks()
                else:
                    messagebox.showerror("Warning!", "Wrong mark!")
            else:
                pass
        except AttributeError:
            pass

    def del_mark(self):
        """Method that remove marks."""
        try:
            for i in self.selected_marks:
                self.db.del_mark(self.curr_s_id, i[self.COLUMNS_M[0]])
            self.show_marks()
        except AttributeError:
            pass
        except TypeError:
            pass


class Student(MainWindow):
    """Student management class."""
    def __init__(self, master):
        """Student class init method."""
        super().__init__(master)
        self.TREE_ATT_COL = ['Subject', 'Avg Attendance']
        self.TREE_AVG_COL = ['Subject', 'Avg']
        self.COLUMNS_SUBJECTS_SIZE = [(105, 105), ]
        self.COLUMNS_SUBJECTS = ('Subject',)
        self.TREE_EVENT_COL = ['Subject', 'Class', 'Events']
        self.tree_att_s_col = ['Subject', 'Attendance']

    def student_main(self):
        """Create student main GUI: labels, buttons."""
        # head label
        self.show_student()

        self.head_l = tk.Label(self.frame, text='Student', bg=INFO_BACKGROUND_COLOUR,
                               fg=LABEL_FOREGROUND_COLOUR,
                               font=FONT_SETTINGS_0)
        self.head_l.place(x=0, y=0)

        # change password button
        self.change_pass = tk.Button(self.frame, text='Change password', width=15,
                                     command=self.go_to_change_password, bg='snow')
        self.change_pass.place(x=520, y=2)

        self.attendance = tk.Button(self.frame, text='Attendance', width=15,
                                    command=self.attendance_panel, bg='snow')
        self.attendance.place(x=130, y=2)

        self.marks = tk.Button(self.frame, text='Marks', width=15, command=self.marks_panel,
                               bg='snow')
        self.marks.place(x=260, y=2)

        self.events = tk.Button(self.frame, text='Events', width=15, command=self.events_panel,
                                bg='snow')
        self.events.place(x=390, y=2)

        # log out button
        self.logout_button = tk.Button(self.frame, text='Log out', width=6, command=self.log_out,
                                       bg='snow')
        self.logout_button.place(x=714, y=2)

    def go_to_student_main(self):
        """Go to student main method."""
        self.clear_frame()
        self.student_main()

    # events

    def tree_event(self):
        """Create treeview for events."""
        # events
        self.tree_event_tv = ttk.Treeview(self.frame, columns=self.TREE_EVENT_COL, show='headings',
                                          height=10)
        self.tree_event_tv.place(x=2, y=70)
        self.tree_event_col_size = ((90, 90, tk.CENTER), (40, 40, tk.CENTER), (520, 520, tk.W))
        for size, col in zip(self.tree_event_col_size, self.TREE_EVENT_COL):
            self.tree_event_tv.column(col, minwidth=size[0], width=size[1], anchor=size[2])
            self.tree_event_tv.heading(col, text=col)

        # scroll date y
        self.scroll_event_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_event_y.place(in_=self.tree_event_tv, relx=1.0, relheight=1.0)
        self.scroll_event_y.configure(command=self.tree_event_tv.yview)
        # scroll date x
        self.scroll_event_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_event_x.place(in_=self.tree_event_tv, rely=1.0, relwidth=1.0,
                                  bordermode="inside")
        self.scroll_event_x.configure(command=self.tree_event_tv.xview)
        # configuration of scrolls
        self.tree_event_tv.configure(xscrollcommand=self.scroll_event_x.set)
        self.tree_event_tv.configure(yscrollcommand=self.scroll_event_y.set)

    def show_events(self):
        """Put data into events treeview."""
        for i in self.tree_event_tv.get_children():
            self.tree_event_tv.delete(i)

        for subj_id in self.db.get_subjects_id(CURR_ID):
            for element in self.db.fetch_events_student(subj_id[0]):
                self.tree_event_tv.insert('', tk.END, values=element)

    def events_panel(self):
        """Create main events frame."""
        self.clear_frame()
        self.student_main()
        self.tree_event()
        self.show_events()

    # change password

    def change_password_panel(self):
        """Create change password panel: buttons, labels, entry."""
        # log out button
        self.go_main_butt = tk.Button(self.frame, text='Back', width=6,
                                      command=self.go_to_student_main, bg='snow')
        self.go_main_butt.place(x=714, y=2)

        self.change_butt = tk.Button(self.frame, text='Change', width=10, height=3,
                                     command=self.change_password,
                                     bg='snow')
        self.change_butt.place(x=470, y=99)

        self.type_label = tk.Label(self.frame, text='Type new password', bg=LABEL_BACKGROUND_COLOUR,
                                   fg=LABEL_FOREGROUND_COLOUR, font=FONT_SETTINGS_1)
        self.type_label.place(x=160, y=128)
        self.login_label = tk.Label(self.frame, text='Your login', bg=LABEL_BACKGROUND_COLOUR,
                                    fg=LABEL_FOREGROUND_COLOUR,
                                    font=FONT_SETTINGS_1)
        self.login_label.place(x=160, y=100)

        self.r_login_label = tk.Label(self.frame, text=self.db.get_login(CURR_ID), bg='snow',
                                      fg=LABEL_FOREGROUND_COLOUR,
                                      font=FONT_SETTINGS_2,
                                      width=14)
        self.r_login_label.place(x=320, y=100)

        self.pass_text = tk.StringVar()
        self.pass_entry = tk.Entry(self.frame, show='*', width=21, textvariable=self.pass_text)
        self.pass_entry.place(x=320, y=130)

    def change_password(self):
        """Change password method."""
        if self.pass_text.get() and len(self.pass_text.get()) >= 6:
            self.db.change_password(CURR_ID, self.pass_text.get())
            self.pass_text.set('')
            self.pass_entry.delete(0, tk.END)
            messagebox.showinfo("Succes!", "Password has been changed!")
        else:
            messagebox.showerror("Warning!", "Password too short!\nminimum 6 characters")
            self.pass_entry.delete(0, tk.END)

    def go_to_change_password(self):
        """Go to change password method"""
        self.clear_frame()
        self.change_password_panel()

    # marks

    def marks_panel(self):
        """Create marks management panel."""
        self.clear_frame()
        self.student_main()
        self.tree_marks()
        self.show_marks()
        self.avg_marks_tree()
        self.show_avg_marks()

    def show_student(self):
        """Show informations about logged student."""
        self.student_data = self.db.get_fname_lname_class(CURR_ID)
        self.text = "".join(["Logged as: ", self.student_data[0], " ", self.student_data[1],
                             " class: ", self.student_data[2]])
        self.head_marks_l = tk.Label(self.frame, text=self.text, bg=INFO_BACKGROUND_COLOUR,
                                     fg=LABEL_FOREGROUND_COLOUR,
                                     font=FONT_SETTINGS_0)
        self.head_marks_l.place(x=2, y=36)

    def tree_marks(self):
        """Create treeview for subjects."""
        self.how_much_grades = 11
        self.columns_marks = tuple(str(i) for i in range(self.how_much_grades))

        self.tree_m = ttk.Treeview(self.frame, columns=self.COLUMNS_SUBJECTS + self.columns_marks,
                                   show='headings', height=10)
        self.tree_m.place(x=2, y=70)

        for cols, width in zip(self.COLUMNS_SUBJECTS, self.COLUMNS_SUBJECTS_SIZE):
            self.tree_m.column(cols, minwidth=width[0], width=width[0], anchor=tk.CENTER)
            self.tree_m.heading(cols, text=cols)

        for i in range(self.how_much_grades):
            self.tree_m.column(str(i), minwidth=30, width=30, anchor=tk.CENTER)
            self.tree_m.heading(str(i), text=str(i))
        # scroll y
        self.scroll_m_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_m_y.place(in_=self.tree_m, relx=1.0, relheight=1.0)
        self.scroll_m_y.configure(command=self.tree_m.yview)
        # scroll x
        self.scroll_m_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_m_x.place(in_=self.tree_m, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_m_x.configure(command=self.tree_m.xview)
        # configuration of scrolls
        self.tree_m.configure(xscrollcommand=self.scroll_m_x.set)
        self.tree_m.configure(yscrollcommand=self.scroll_m_y.set)

    def avg_marks_tree(self):
        """Create treeview for average marks of subjects."""
        self.tree_avg = ttk.Treeview(self.frame, columns=self.TREE_AVG_COL, show='headings',
                                     height=10)
        self.tree_avg.place(x=500, y=70)
        self.tree_avg_col_size = ((95, 95, tk.CENTER), (50, 50, tk.CENTER))
        for size, col in zip(self.tree_avg_col_size, self.TREE_AVG_COL):
            self.tree_avg.column(col, minwidth=size[0], width=size[1], anchor=size[2])
            self.tree_avg.heading(col, text=col)

        # scroll date y
        self.scroll_avg_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_avg_y.place(in_=self.tree_avg, relx=1.0, relheight=1.0)
        self.scroll_avg_y.configure(command=self.tree_avg.yview)
        # scroll date x
        self.scroll_avg_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_avg_x.place(in_=self.tree_avg, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_avg_x.configure(command=self.tree_avg.xview)
        # configuration of scrolls
        self.tree_avg.configure(xscrollcommand=self.scroll_avg_x.set)
        self.tree_avg.configure(yscrollcommand=self.scroll_avg_y.set)

    def show_avg_marks(self):
        """Put data into average marks treeview."""
        for i in self.tree_avg.get_children():
            self.tree_avg.delete(i)
        for subj_id in self.db.get_subjects_id(CURR_ID):
            grades = self.db.fetch_avg_student(CURR_ID, subj_id[0])
            name = self.db.fetch_subj_name_student(subj_id[0])
            try:
                self.tree_avg.insert('', tk.END, values=name + [round(grades[0][0], 2)])
            except TypeError:
                pass

    def show_marks(self):
        """Put ddata into marks treeview."""
        for i in self.tree_m.get_children():
            self.tree_m.delete(i)
        for subj_id in self.db.get_subjects_id(CURR_ID):
            grades = self.db.fetch_marks_student(CURR_ID, subj_id[0])
            name = self.db.fetch_subj_name_student(subj_id[0])
            self.tree_m.insert('', tk.END, values=name + grades)

    # attendance

    def attendance_panel(self):
        """Create main attendance panel."""
        self.clear_frame()
        self.student_main()
        self.att_tree()
        self.show_avg_att()
        self.att_s_tree()
        self.combo_att_s()

    def att_tree(self):
        """Create treeview for average attendance panel."""
        self.tree_att_h = tk.Label(self.frame, text='     Average attendance     ',
                                   bg=LABEL_BACKGROUND_COLOUR,
                                   fg=LABEL_FOREGROUND_COLOUR,
                                   font=FONT_SETTINGS_1)
        self.tree_att_h.place(x=450, y=65)

        self.tree_att = ttk.Treeview(self.frame, columns=self.TREE_ATT_COL, show='headings',
                                     height=10)
        self.tree_att.place(x=450, y=90)
        self.tree_att_col_size = ((95, 95, tk.CENTER), (103, 103, tk.CENTER))
        for size, col in zip(self.tree_att_col_size, self.TREE_ATT_COL):
            self.tree_att.column(col, minwidth=size[0], width=size[1], anchor=size[2])
            self.tree_att.heading(col, text=col)

        # scroll date y
        self.scroll_att_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_att_y.place(in_=self.tree_att, relx=1.0, relheight=1.0)
        self.scroll_att_y.configure(command=self.tree_att.yview)
        # scroll date x
        self.scroll_att_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_att_x.place(in_=self.tree_att, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_att_x.configure(command=self.tree_att.xview)
        # configuration of scrolls
        self.tree_att.configure(xscrollcommand=self.scroll_att_x.set)
        self.tree_att.configure(yscrollcommand=self.scroll_att_y.set)

    def show_avg_att(self):
        """Put data into average attendance treeview"""
        for item in self.tree_att.get_children():
            self.tree_att.delete(item)
        for subj_id in self.db.get_subjects_id(CURR_ID):
            att = self.db.fetch_att_student(CURR_ID, subj_id[0])
            name = self.db.fetch_subj_name_student(subj_id[0])
            try:
                self.tree_att.insert('', tk.END,
                                     values=name + ["".join([str(round(att[0][0], 2) * 100), "%"])])
            except TypeError:
                pass

    def att_s_tree(self):
        """Create treeview for attendance panel."""
        self.tree_att_s = ttk.Treeview(self.frame, columns=self.tree_att_s_col, show='headings',
                                       height=10)
        self.tree_att_s.place(x=150, y=90)
        self.tree_att_s_col_size = ((95, 95, tk.CENTER), (100, 100, tk.CENTER))
        for size, col in zip(self.tree_att_s_col_size, self.tree_att_s_col):
            self.tree_att_s.column(col, minwidth=size[0], width=size[1], anchor=size[2])
            self.tree_att_s.heading(col, text=col)

        # scroll date y
        self.scroll_att_s_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll_att_s_y.place(in_=self.tree_att_s, relx=1.0, relheight=1.0)
        self.scroll_att_s_y.configure(command=self.tree_att_s.yview)
        # scroll date x
        self.scroll_att_s_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_att_s_x.place(in_=self.tree_att_s, rely=1.0, relwidth=1.0, bordermode="inside")
        self.scroll_att_s_x.configure(command=self.tree_att_s.xview)
        # configuration of scrolls
        self.tree_att_s.configure(xscrollcommand=self.scroll_att_s_x.set)
        self.tree_att_s.configure(yscrollcommand=self.scroll_att_s_y.set)

    def combo_att_s(self):
        """Create combobox with dates to choose (attendance panel)."""
        # combobox subject
        self.att_text = tk.StringVar()
        self.att_text.set('Choose date')
        self.att_cb = ttk.Combobox(self.frame, textvariable=self.att_text, justify='center',
                                   state='readonly', width=29)
        self.att_cb['values'] = self.db.fetch_date_cutted(CURR_ID)
        self.att_cb.bind('<<ComboboxSelected>>', self.show_att_date)
        self.att_cb.place(x=150, y=68)

    def show_att_date(self, event):
        """Put data into attendance treeview."""
        for i in self.tree_att_s.get_children():
            self.tree_att_s.delete(i)
        for subj_id in self.db.get_subjects_id(CURR_ID):
            name = self.db.fetch_subj_name_student(subj_id[0])
            att = self.db.fetch_att_student_date(CURR_ID, subj_id[0], self.att_cb.get())
            self.tree_att_s.insert('', tk.END, values=name + att)
