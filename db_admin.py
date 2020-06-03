import sqlite3


class Database:
    """Main database class."""
    def __init__(self, database):
        """Init method for Database class. Create connection, cursor and tables."""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        with self.connection:
            self.cursor.execute("""
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

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id   INTEGER    PRIMARY KEY AUTOINCREMENT,
                name_subject CHAR (250) NOT NULL,
                class_name   CHAR (50)  NOT NULL
            );
             """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_subjects (
                user_id    INTEGER,
                subject_id INTEGER,
                CONSTRAINT u_fk FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                CONSTRAINT s_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) ON DELETE
                CASCADE
            );
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                mark_id    INTEGER       PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER       NOT NULL,
                subject_id INTEGER       NOT NULL,
                attendance BOOLEAN (2)   NOT NULL DEFAULT (0),
                late       BOOLEAN (2)   NOT NULL DEFAULT (0),
                mark_date       DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                grade      REAL (4), 
                CONSTRAINT us_fk FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                CONSTRAINT su_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) ON DELETE 
                CASCADE
            );
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id  INTEGER,
                event_note  VARCHAR(250),
                CONSTRAINT sub_fk FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
                        );
                        """)


class AdminDB(Database):
    """Admin panel database management class."""
    def add_user(self, fname, lname, email, phone, pesel, birth_date, perm):
        self.cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (fname, lname, pesel, fname.lower()[:1] + lname.lower(), email, phone,
                             pesel, birth_date,
                             perm))
        self.connection.commit()

    def fetch(self):
        """Get all of fields from users table."""
        self.cursor.execute("SELECT user_id, fname, lname, password, login, email, phone, pesel, "
                            "birth_date, perm FROM users ORDER BY pesel, lname, fname")
        rows = self.cursor.fetchall()
        return rows

    def fetch_class_subj(self):
        """Get data to class-subjects treeview."""
        self.cursor.execute("""SELECT user_id, perm, fname, lname, pesel, birth_date, name_subject, 
        class_name FROM users LEFT JOIN users_subjects USING(user_id) LEFT JOIN subjects 
        USING(subject_id) WHERE perm = 0 OR perm = 1 ORDER BY pesel, lname, fname""")
        rows = self.cursor.fetchall()
        return rows

    def fetch_subjects(self):
        """Get subjects and class informations."""
        self.cursor.execute(
            "SELECT subject_id, name_subject, class_name FROM subjects ORDER BY class_name")
        rows = self.cursor.fetchall()
        return rows

    def update_user(self, user_id, fname, lname, email, phone, pesel, birth_date, perm):
        """Update user."""
        self.cursor.execute("""UPDATE users SET fname = ?, lname = ?, email = ?, phone = ?,
        pesel = ?, birth_date = ?, perm = ? WHERE user_id = ?""",
                            (fname, lname, email, phone, pesel, birth_date, perm, user_id))
        self.connection.commit()

    def default_password(self, user_id, pesel):
        """Set default password."""
        self.cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (pesel, user_id))
        self.connection.commit()

    def delete_user(self, user_id):
        """Delete user using ID."""
        self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.connection.commit()

    def delete_class(self, subject_id):
        """Delete class using subject id."""
        self.cursor.execute('DELETE FROM subjects WHERE subject_id = ?', (subject_id,))
        self.cursor.execute('DELETE FROM users_subjects WHERE subject_id = ?', (subject_id,))
        self.connection.commit()

    def select_by_pesel(self, pesel):
        """Get data to search using pesel method."""
        self.cursor.execute("SELECT user_id, fname, lname, password, login, email, phone, pesel, "
                            "birth_date, perm FROM users WHERE pesel = ?", (pesel,))
        users = self.cursor.fetchone()
        return users

    def select_by_year(self, year):
        """Get data to search using year method."""
        year = "".join(["%", year, "%"])
        self.cursor.execute("""SELECT users.user_id, perm, fname, lname, pesel, birth_date,
        name_subject, class_name FROM users LEFT JOIN users_subjects USING(user_id) 
        LEFT JOIN subjects USING(subject_id) WHERE birth_date LIKE ? ORDER BY fname""",
                            (year,))
        u = self.cursor.fetchall()
        return u

    def add_class(self, name_subject, class_name):
        """Add new class and subject."""
        self.cursor.execute(
            'SELECT name_subject, class_name FROM subjects WHERE name_subject = ? AND class_name '
            '= ?',
            (name_subject, class_name))
        if self.cursor.fetchone() != (name_subject, class_name) and (
                name_subject != '' and class_name != ''):
            self.cursor.execute('INSERT INTO subjects(name_subject, class_name) VALUES (?, ?)',
                                (name_subject, class_name))
            self.connection.commit()
        else:
            raise ValueError

    def join_usr_subj(self, user_id, subject_id):
        """Connect user with subject."""
        self.cursor.execute('SELECT user_id, subject_id FROM users_subjects '
                            'WHERE user_id = ? AND subject_id = ?', (user_id, subject_id))
        if self.cursor.fetchone() != (user_id, subject_id):
            self.cursor.execute('INSERT INTO users_subjects(user_id, subject_id) VALUES(?, ?)',
                                (user_id, subject_id))
            self.connection.commit()
        else:
            raise AttributeError

    def disjoin_user_subj(self, user_id, subject_name, class_name):
        """Disconnect user and subject."""
        self.cursor.execute(
            'SELECT subject_id FROM subjects WHERE name_subject = ? AND class_name = ?',
            (subject_name, class_name))
        try:
            subject_id = (self.cursor.fetchone())[0]
            self.cursor.execute('DELETE FROM users_subjects WHERE user_id = ? AND subject_id = ?',
                                (user_id, subject_id))
            self.connection.commit()
        except TypeError:
            pass


class LoginDB(Database):
    """Login panel database management class."""
    def check_password(self, log, paswd):
        """Method that check the password is correct."""
        self.cursor.execute("SELECT perm, user_id FROM users WHERE login = ? AND password = ?",
                            (log, paswd))
        none_or_one = self.cursor.fetchone()
        return none_or_one


class TeacherDB(Database):
    """Teacher panel database management class."""
    def get_login(self, user_id):
        self.cursor.execute('SELECT login FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    def change_password(self, user_id, password):
        """Change password method."""
        self.cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, user_id))
        self.connection.commit()

    def get_teacher_subjects(self, user_id):
        """Get subjects and class connected with teacher."""
        self.cursor.execute("""SELECT name_subject, class_name FROM users LEFT JOIN
        users_subjects USING(user_id) LEFT JOIN subjects USING(subject_id) 
        WHERE users.user_id = ? ORDER BY class_name""", (user_id,))
        rows = self.cursor.fetchall()
        return rows

    def get_curr_subj_id(self, class_name, name_subject, user_id):
        """Get current subject id, that teacher is logged in."""
        self.cursor.execute("""SELECT subjects.subject_id FROM users LEFT JOIN users_subjects
        USING(user_id) LEFT JOIN subjects USING(subject_id) WHERE class_name = ? AND name_subject = ?
        AND users.user_id = ?""", (class_name, name_subject, user_id))
        rows = self.cursor.fetchone()
        return rows

    def fetch_date(self, subject_id):
        """Get dates that are connected with subject (attendance panel)."""
        self.cursor.execute(
            """SELECT mark_date FROM marks WHERE subject_id = ? AND grade IS NULL GROUP BY mark_date ORDER
            BY mark_date DESC""", (subject_id,))
        rows = self.cursor.fetchall()
        return rows

    def fetch_attendance(self, subject_id, selected_date):
        """Get attendances that are connected with date and subject."""
        selected_date = "".join(["%", selected_date, "%"])
        self.cursor.execute("""SELECT users.user_id, fname, lname, attendance, late FROM users
        LEFT JOIN marks USING(user_id) WHERE subject_id = ? AND perm = 0 AND
        mark_date LIKE ? ORDER BY lname""", (subject_id, selected_date))
        rows = self.cursor.fetchall()
        return rows

    def set_present(self, user_id, subject_id, selected_date):
        """Set student present method."""
        self.cursor.execute(
            """UPDATE marks SET attendance = 1 WHERE user_id = ? AND subject_id = ? 
            AND mark_date = ?""", (user_id, subject_id, selected_date))
        self.connection.commit()

    def set_absent(self, user_id, subject_id, selected_date):
        """Set student absent method."""
        self.cursor.execute(
            """UPDATE marks SET attendance = 0 WHERE user_id = ? AND subject_id = ? 
            AND mark_date = ?""", (user_id, subject_id, selected_date))
        self.connection.commit()

    def new_datas(self, user_id, subject_id):
        """Add new current date. The method is called every time, when teacher log in subject."""
        self.cursor.execute("INSERT INTO marks(attendance, user_id, subject_id) VALUES(0, ?, ?)",
                            (user_id, subject_id))
        self.connection.commit()

    def get_students_subject_id(self, subject_id):
        """Get all user_id from students that are connected with subject."""
        self.cursor.execute("""SELECT users.user_id FROM users LEFT JOIN users_subjects USING(user_id)
        WHERE subject_id = ? AND perm = 0""", (subject_id,))
        rows = self.cursor.fetchall()
        return rows

    def set_late(self, user_id, subject_id, selected_date, late):
        """Set student late method."""
        self.cursor.execute(
            "UPDATE marks SET late = ? WHERE user_id = ? AND subject_id = ? AND mark_date = ?",
            (late, user_id, subject_id, selected_date))
        self.connection.commit()

    def fetch_events(self, subject_id):
        """Get all events that are connected with subject."""
        self.cursor.execute(
            """SELECT event_id, event_note FROM events WHERE subject_id = ? ORDER BY event_id""",
            (subject_id,))
        rows = self.cursor.fetchall()
        return rows

    def add_event(self, event_note, subject_id):
        """Add new event."""
        self.cursor.execute("INSERT INTO events(event_note, subject_id) VALUES(?, ?)",
                            (event_note, subject_id))
        self.connection.commit()

    def del_event(self, event_id):
        """Delete event using event id."""
        self.cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
        self.connection.commit()

    def fetch_students(self, subject_id):
        """Get all students that are connected with subject."""
        self.cursor.execute("""SELECT users.user_id, fname, lname FROM users LEFT JOIN marks
        USING(user_id) WHERE subject_id = ? AND perm = 0 GROUP BY users.user_id
        ORDER BY lname""", (subject_id,))
        rows = self.cursor.fetchall()
        return rows

    def fetch_marks(self, subject_id, user_id):
        """Get all marks that are connected with student and subject."""
        self.cursor.execute("""SELECT grade FROM marks WHERE subject_id = ? AND user_id = ? AND
        grade IS NOT NULL""", (subject_id, user_id))
        rows = tuple(i for i in self.cursor.fetchall())
        # TODO: poprawić ten wynalazek
        return rows

    def add_mark(self, mark, subject_id, user_id):
        """Add new mark to the student."""
        self.cursor.execute("INSERT INTO marks(grade, subject_id, user_id) VALUES(?, ?, ?)",
                            (mark, subject_id, user_id))
        self.connection.commit()

    def del_mark(self, subject_id, user_id):
        """Delete mark, using user_id and student_id."""
        self.cursor.execute(
            """SELECT mark_id FROM marks WHERE subject_id = ? AND user_id = ? AND grade IS NOT NULL
        ORDER BY mark_date""", (subject_id, user_id))
        mark_id = (self.cursor.fetchone())[0]
        self.cursor.execute("DELETE FROM marks WHERE mark_id = ?", (mark_id,))
        self.connection.commit()


class StudentDB(Database):
    """Student panel database management class."""

    def get_subjects_id(self, user_id):
        self.cursor.execute("""SELECT subjects.subject_id FROM users LEFT JOIN users_subjects 
        USING(user_id) LEFT JOIN subjects USING(subject_id) WHERE users.user_id = ?""", (user_id,))
        subject_id = self.cursor.fetchall()
        return subject_id

    def fetch_events_student(self, subject_id):
        """Get all events that are connected with subject."""
        self.cursor.execute("""SELECT name_subject, class_name, event_note FROM subjects LEFT
        JOIN events USING(subject_id) WHERE events.subject_id = ? ORDER BY event_id""",
                            (subject_id,))

        rows = self.cursor.fetchall()
        return rows

    def fetch_marks_student(self, user_id, subject_id):
        """Get all marks that are connected with student and subject."""
        self.cursor.execute("""SELECT grade FROM subjects LEFT JOIN marks USING(subject_id) 
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NOT NULL""",
                            (user_id, subject_id))

        rows = self.cursor.fetchall()
        return rows

    def fetch_subj_name_student(self, subject_id):
        """Get subject name, using subject id."""
        self.cursor.execute("SELECT name_subject FROM subjects WHERE subject_id = ?", (subject_id,))
        name = self.cursor.fetchall()
        return name

    def fetch_avg_student(self, user_id, subject_id):
        """Get average marks, using user id and subject id."""
        self.cursor.execute("""SELECT avg(grade) FROM subjects LEFT JOIN marks USING(subject_id) 
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NOT NULL""",
                            (user_id, subject_id))
        rows = self.cursor.fetchall()
        return rows

    def get_fname_lname_class(self, user_id):
        """Get first name, last name and class name using user_id."""
        self.cursor.execute("""SELECT fname, lname, class_name FROM users LEFT JOIN
        users_subjects USING(user_id) LEFT JOIN subjects USING(subject_id) 
        WHERE users.user_id = ? GROUP BY lname""", (user_id,))
        rows = self.cursor.fetchone()
        return rows

    def fetch_att_student(self, user_id, subject_id):
        """Get average attendance. (using user id and subject id)"""
        self.cursor.execute("""SELECT avg(attendance) FROM subjects LEFT JOIN marks USING(subject_id)
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NULL""", (user_id, subject_id))
        rows = self.cursor.fetchall()
        return rows

    def fetch_date_cutted(self, user_id):
        """Get date in format: YYYY-MM-DD."""
        self.cursor.execute("""SELECT substr(CAST(mark_date AS TEXT), 0, 11) FROM marks WHERE grade IS
        NULL AND user_id = ? GROUP BY substr(CAST(mark_date AS TEXT), 0, 11) ORDER BY mark_date DESC""",
                            (user_id,))
        rows = self.cursor.fetchall()
        return rows

    def fetch_att_student_date(self, user_id, subject_id, date):
        """Get student's attendance using date of day from the subject."""
        date = "".join(["%", date, "%"])
        self.cursor.execute("""SELECT attendance FROM subjects LEFT JOIN marks USING(subject_id)
        WHERE user_id = ? AND marks.subject_id = ? AND grade IS NULL AND mark_date LIKE ?""",
                            (user_id, subject_id, date))
        rows = self.cursor.fetchall()
        return rows


class DatabaseManagementClass(AdminDB, LoginDB, TeacherDB, StudentDB):
    """Main database management class."""
    pass
