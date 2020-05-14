import sqlite3


class Database:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        with self.conn:
            self.c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER     PRIMARY KEY AUTOINCREMENT,
                fname      CHAR (250)  NOT NULL,
                lname      CHAR (250)  NOT NULL,
                password   CHAR (250)  NOT NULL,
                login      CHAR (250)  NOT  NULL,
                email      CHAR (250)  UNIQUE NOT NULL,
                phone      CHAR (20)   UNIQUE NOT NULL,
                pesel      CHAR (11)   UNIQUE NOT NULL,
                birth_date DATE        NOT NULL,
                perm       INTEGER (2) DEFAULT (0) NOT NULL
            );
            """)

            self.c.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id   INTEGER    PRIMARY KEY AUTOINCREMENT,
                name_subject CHAR (250) NOT NULL,
                class_name   CHAR (50)  NOT NULL,
                event        CHAR (250)
            );
            """)

            self.c.execute("""
            CREATE TABLE IF NOT EXISTS users_subjects (
                user_id    INTEGER,
                subject_id INTEGER,
                CONSTRAINT u_fk FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                CONSTRAINT s_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) ON DELETE CASCADE
            );
            """)

            self.c.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                mark_id    INTEGER       PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER       NOT NULL,
                subject_id INTEGER       NOT NULL,
                attendance BOOLEAN (2)   NOT NULL DEFAULT (0),
                late       BOOLEAN (2)   NOT NULL DEFAULT (0),
                date       DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                grade      REAL (4), 
                CONSTRAINT us_fk FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                CONSTRAINT su_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) ON DELETE CASCADE
            );
            """)

            self.c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id  INTEGER,
                event_note  VARCHAR(250),
                CONSTRAINT sub_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
                        );
                        """)
            # Commit transactions
            self.conn.commit()

    def __del__(self):
        self.conn.close()


class AdminDB(Database):
    def add_user(self, fname, lname, email, phone, pesel, birth_date, perm):
        self.c.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (fname, lname, pesel, fname.lower()[:1] + lname.lower(), email, phone, pesel, birth_date,
                        perm))
        self.conn.commit()

    def fetch(self):
        self.c.execute("SELECT * FROM users ORDER BY pesel, lname, fname")
        rows = self.c.fetchall()
        return rows

    def fetch_class_subj(self):
        self.c.execute("""SELECT users.user_id, perm, fname, lname, pesel, birth_date, name_subject, class_name
        FROM users LEFT JOIN users_subjects ON users.user_id = users_subjects.user_id LEFT JOIN subjects ON
          users_subjects.subject_id = subjects.subject_id WHERE perm = '0' OR perm = '1' ORDER BY pesel, lname, fname""")
        rows = self.c.fetchall()
        return rows

    def fetch_subjects(self):
        self.c.execute('''SELECT subject_id, name_subject, class_name FROM subjects ORDER BY class_name''')
        rows = self.c.fetchall()
        return rows
#
    def update_user(self, user_id, fname, lname, email, phone, pesel, birth_date, perm):
        self.c.execute("""UPDATE users SET fname = ?, lname = ?, email = ?, phone = ?, pesel = ?, birth_date = ?, 
                       perm = ? WHERE user_id = ?""", (fname, lname, email, phone, pesel, birth_date, perm, user_id))
        self.conn.commit()

    def default_password(self, user_id, pesel):
        self.c.execute("UPDATE users SET password = ? WHERE user_id = ?", (pesel, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        self.c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def delete_class(self, subject_id):
        self.c.execute('DELETE FROM subjects WHERE subject_id = ?', (subject_id,))
        self.c.execute('DELETE FROM users_subjects WHERE subject_id = ?', (subject_id,))
        self.conn.commit()

    def select_by_pesel(self, pesel):
        self.c.execute("SELECT * FROM users WHERE pesel = ?", (pesel,))
        u = self.c.fetchone()
        return u

    def select_by_year(self, year):
        year = '%' + year + '%'
        self.c.execute("""SELECT users.user_id, perm, fname, lname, pesel, birth_date, name_subject, class_name
        FROM users LEFT JOIN users_subjects ON users.user_id = users_subjects.user_id LEFT JOIN subjects ON
          users_subjects.subject_id = subjects.subject_id WHERE birth_date LIKE ? ORDER BY fname""", (year,))
        u = self.c.fetchall()
        return u

    def add_class(self, name_subject, class_name):
        self.c.execute('SELECT name_subject, class_name FROM subjects WHERE name_subject = ? AND class_name = ?',
                       (name_subject, class_name))
        if self.c.fetchone() != (name_subject, class_name) and (name_subject != '' and class_name != ''):
            self.c.execute('INSERT INTO subjects(name_subject, class_name) VALUES (?, ?)', (name_subject, class_name))
            self.conn.commit()
        else:
            raise ValueError

    def join_usr_subj(self, user_id, subject_id):
        self.c.execute('SELECT user_id, subject_id FROM users_subjects '
                       'WHERE user_id = ? AND subject_id = ?', (user_id, subject_id))
        if self.c.fetchone() != (user_id, subject_id):
            self.c.execute('INSERT INTO users_subjects(user_id, subject_id) VALUES(?, ?)', (user_id, subject_id))
            self.conn.commit()
        else:
            raise AttributeError

    def disjoin_user_subj(self, user_id, subject_name, class_name):
        self.c.execute('SELECT subject_id FROM subjects WHERE name_subject = ? AND class_name = ?',
                       (subject_name, class_name))
        try:
            subject_id = (self.c.fetchone())[0]
            self.c.execute('DELETE FROM users_subjects WHERE user_id = ? AND subject_id = ?', (user_id, subject_id))
            self.conn.commit()
        except TypeError:
            pass


class LoginDB(Database):
    def check_password(self, log, paswd):
        self.c.execute("SELECT perm, user_id FROM users WHERE login = ? AND password = ?", (log, paswd))
        lp = self.c.fetchone()
        return lp


class TeacherDB(Database):
    def get_login(self, user_id):
        self.c.execute('SELECT login FROM users WHERE user_id = ?', (user_id,))
        return self.c.fetchone()

    def change_password(self, user_id, password):
        self.c.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, user_id))
        self.conn.commit()

    def get_teacher_subjects(self, user_id):
        self.c.execute('''SELECT name_subject, class_name FROM users LEFT JOIN users_subjects 
        ON users.user_id = users_subjects.user_id LEFT JOIN subjects ON
        users_subjects.subject_id = subjects.subject_id WHERE users.user_id = ? ORDER BY class_name''', (user_id,))
        rows = self.c.fetchall()
        return rows

    def get_curr_subj_id(self, class_name, name_subject, user_id):
        self.c.execute('''SELECT subjects.subject_id FROM users LEFT JOIN users_subjects 
        ON users.user_id = users_subjects.user_id LEFT JOIN subjects ON
        users_subjects.subject_id = subjects.subject_id WHERE class_name = ? AND name_subject = ?
        AND users.user_id = ?''',
                       (class_name, name_subject, user_id))
        rows = self.c.fetchone()
        return rows

    def fetch_date(self, subject_id):
        self.c.execute("""SELECT date FROM marks WHERE subject_id = ? AND grade IS NULL GROUP BY date ORDER BY date DESC""",
                       (subject_id,))
        rows = self.c.fetchall()
        for i in rows:
            print(i)
        return rows

    def fetch_attendance(self, subject_id, selected_date):
        selected_date = '%' + selected_date + '%'
        self.c.execute("""SELECT users.user_id, fname, lname, attendance, late
        FROM users LEFT JOIN marks ON users.user_id = marks.user_id WHERE subject_id = ? AND perm = ? AND date
        LIKE ? ORDER BY lname""", (subject_id, 0, selected_date))
        rows = self.c.fetchall()
        return rows

    def set_present(self, user_id, subject_id, selected_date):
        self.c.execute('UPDATE marks SET attendance = "1" WHERE user_id = ? AND subject_id = ? AND date = ?',
                       (user_id, subject_id, selected_date))
        self.conn.commit()

    def set_absent(self, user_id, subject_id, selected_date):
        self.c.execute('UPDATE marks SET attendance = "0" WHERE user_id = ? AND subject_id = ? AND date = ?',
                       (user_id, subject_id, selected_date))
        self.conn.commit()

    def new_datas(self, user_id, subject_id):
        self.c.execute('INSERT INTO marks(attendance, user_id, subject_id) VALUES(0, ?, ?)', (user_id, subject_id))
        self.conn.commit()

    def get_students_subject_id(self, subject_id):
        self.c.execute("""SELECT users.user_id
        FROM users JOIN users_subjects ON users.user_id = users_subjects.user_id 
        WHERE subject_id = ? AND perm = ?""", (subject_id, 0))
        rows = self.c.fetchall()
        return rows

    def set_late(self, user_id, subject_id, selected_date, late):
        self.c.execute('UPDATE marks SET late = ? WHERE user_id = ? AND subject_id = ? AND date = ?',
                       (late, user_id, subject_id, selected_date))
        self.conn.commit()

    def fetch_events(self, subject_id):
        self.c.execute("""SELECT event_id, event_note FROM events WHERE subject_id = ? ORDER BY event_id""",
                       (subject_id,))
        rows = self.c.fetchall()
        return rows

    def add_event(self, event_note, subject_id):
        self.c.execute('INSERT INTO events(event_note, subject_id) VALUES(?, ?)', (event_note, subject_id))
        self.conn.commit()

    def del_event(self, event_id):
        self.c.execute('DELETE FROM events WHERE event_id = ?', (event_id,))
        self.conn.commit()

    def fetch_students(self, subject_id):
        self.c.execute("""SELECT users.user_id, fname, lname
                FROM users LEFT JOIN marks ON users.user_id = marks.user_id WHERE subject_id = ? AND perm = ?
                GROUP BY users.user_id ORDER BY lname""", (subject_id, 0))
        rows = self.c.fetchall()
        return rows

    def fetch_marks(self, subject_id, user_id):
        self.c.execute('''SELECT grade FROM marks WHERE subject_id = ? AND user_id = ? AND grade < '7' AND grade > 
        '-1' ''', (subject_id, user_id))
        rows = tuple(i for i in self.c.fetchall())
        return rows

    def add_mark(self, mark, subject_id, user_id):
        self.c.execute('INSERT INTO marks(grade, subject_id, user_id) VALUES(?, ?, ?)', (mark, subject_id, user_id))
        self.conn.commit()

    def del_mark(self, subject_id, user_id):
        self.c.execute(
            'SELECT mark_id FROM marks WHERE subject_id = ? AND user_id = ? AND grade > "-1" AND grade < "7" ORDER BY date',
            (subject_id, user_id))
        m_id = (self.c.fetchone())[0]
        self.c.execute('DELETE FROM marks WHERE mark_id = ?', (m_id,))
        self.conn.commit()


class StudentDB(Database):

    def get_subjects_id(self, user_id):
        self.c.execute('''SELECT subjects.subject_id FROM users LEFT JOIN users_subjects ON users.user_id = users_subjects.user_id 
        LEFT JOIN subjects ON users_subjects.subject_id = subjects.subject_id WHERE users.user_id = ?''', (user_id,))
        subject_id = self.c.fetchall()
        return subject_id

    def fetch_events_student(self, subject_id):
        self.c.execute("""SELECT name_subject, class_name, event_note FROM subjects LEFT JOIN events ON subjects.subject_id = events.subject_id
        WHERE events.subject_id = ? ORDER BY event_id""",
                       (subject_id,))

        rows = self.c.fetchall()
        return rows

    def fetch_marks_student(self, user_id, subject_id):
        self.c.execute('''SELECT grade FROM subjects LEFT JOIN marks ON subjects.subject_id = marks.subject_id 
        WHERE user_id = ? AND marks.subject_id = ? AND grade > '-1' AND grade < '7' ''',
                       (user_id, subject_id))
        rows = self.c.fetchall()
        return rows

    def fetch_subj_name_student(self, subject_id):
        self.c.execute('SELECT name_subject FROM subjects WHERE subject_id = ?', (subject_id,))
        name = self.c.fetchall()
        return name

    def fetch_avg_student(self, user_id, subject_id):
        self.c.execute('''SELECT avg(grade) FROM subjects LEFT JOIN marks ON subjects.subject_id = marks.subject_id 
        WHERE user_id = ? AND marks.subject_id = ? AND grade > '-1' AND grade < '7' ''',
                       (user_id, subject_id))
        rows = self.c.fetchall()
        return rows

    def get_fname_lname_class(self, user_id):
        self.c.execute('''SELECT fname, lname, class_name FROM users LEFT JOIN users_subjects ON 
        users.user_id = users_subjects.user_id LEFT JOIN subjects ON 
        users_subjects.subject_id = subjects.subject_id WHERE users.user_id = ? GROUP BY lname''', (user_id,))
        rows = self.c.fetchone()
        return rows

    def fetch_att_student(self, user_id, subject_id):
        self.c.execute('''SELECT avg(attendance) FROM subjects LEFT JOIN marks ON subjects.subject_id = marks.subject_id 
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NULL''',
                       (user_id, subject_id))
        rows = self.c.fetchall()
        return rows

    def fetch_date_cutted(self, user_id):
        self.c.execute("""SELECT substr(CAST(date AS TEXT), 0, 11) FROM marks WHERE grade IS NULL AND user_id = ?
        GROUP BY substr(CAST(date AS TEXT), 0, 11) ORDER BY date DESC""", (user_id,))
        rows = self.c.fetchall()
        return rows

    def fetch_att_student_date(self, user_id, subject_id, date):
        self.c.execute('''SELECT attendance FROM subjects LEFT JOIN marks ON subjects.subject_id = marks.subject_id 
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NULL AND date LIKE ?''',
                       (user_id, subject_id, '%' + date + '%'))
        rows = self.c.fetchall()
        return rows


class DatabaseManagementClass(AdminDB, LoginDB, TeacherDB, StudentDB):
    pass


db = DatabaseManagementClass('gradebook.db')
# db.add_user('1', '1', '1', '1', '1', '1', '2') # admin
