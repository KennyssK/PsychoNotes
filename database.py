import sqlite3
import os

# Используем os.path.join, чтобы путь к базе данных был корректным на Android
# Это важно для Kivy, так как приложение запускается в своей песочнице
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(APP_DIR, 'psychologist_notes.db')

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
        self._init_db()

    def _connect(self):
        """Устанавливает соединение с базой данных."""
        if self.conn is None:
            self.conn = sqlite3.connect(DATABASE_NAME)
            self.cursor = self.conn.cursor()

    def _init_db(self):
        """Инициализирует таблицы в базе данных."""
        self._connect() # Убедимся, что соединение установлено
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        age INTEGER,
        phone_number TEXT,
        temperament TEXT,
        character_type TEXT,
        perception_type TEXT,
        anamnesis TEXT,
        help_plan TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ClientRequests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                request_text TEXT NOT NULL,
                FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                meeting_date TEXT NOT NULL, -- Формат YYYY-MM-DD
                meeting_time TEXT NOT NULL, -- Формат HH:MM
                meeting_location TEXT,
                weather TEXT,
                initial_state TEXT,
                initial_state_score INTEGER,
                request TEXT,
                meeting_progress TEXT,
                techniques_used TEXT,
                meeting_outcome TEXT,
                final_state TEXT,
                final_state_score INTEGER,
                FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def add_client(self, full_name, age=None, phone_number=None, temperament=None,
                   character_type=None, perception_type=None, anamnesis=None, help_plan=None, requests=None):
        self.cursor.execute('''
            INSERT INTO Clients (full_name, age, phone_number, temperament, character_type, perception_type, anamnesis, help_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, age, phone_number, temperament, character_type, perception_type, anamnesis, help_plan))
        client_id = self.cursor.lastrowid
        if requests:
            for req in requests:
                self.cursor.execute('INSERT INTO ClientRequests (client_id, request_text) VALUES (?, ?)', (client_id, req))
        self.conn.commit()
        return client_id

    def get_clients(self, search_query=None):
        if search_query:
            self.cursor.execute("SELECT client_id, full_name, age, phone_number FROM Clients WHERE full_name LIKE ? ORDER BY full_name",
                               ('%' + search_query + '%',))
        else:
            self.cursor.execute("SELECT client_id, full_name, age, phone_number FROM Clients ORDER BY full_name")
        return self.cursor.fetchall()

    def get_client_details(self, client_id):
        self.cursor.execute('''
            SELECT full_name, age, phone_number, temperament, character_type, perception_type, anamnesis, help_plan
            FROM Clients WHERE client_id = ?
        ''', (client_id,))
        client_data = self.cursor.fetchone()

        requests_data = None
        if client_data:
            self.cursor.execute('SELECT request_text FROM ClientRequests WHERE client_id = ?', (client_id,))
            requests_data = [row[0] for row in self.cursor.fetchall()]

        return client_data, requests_data

    def update_client(self, client_id, full_name, age, phone_number, temperament,
                      character_type, perception_type, anamnesis, help_plan, requests):
        self.cursor.execute('''
            UPDATE Clients SET full_name=?, age=?, phone_number=?, temperament=?, character_type=?, perception_type=?, anamnesis=?, help_plan=?
            WHERE client_id=?
        ''', (full_name, age, phone_number, temperament, character_type, perception_type, anamnesis, help_plan, client_id))

        # Удаляем старые запросы и вставляем новые
        self.cursor.execute('DELETE FROM ClientRequests WHERE client_id = ?', (client_id,))
        if requests:
            for req in requests:
                self.cursor.execute('INSERT INTO ClientRequests (client_id, request_text) VALUES (?, ?)', (client_id, req))
        self.conn.commit()

    def add_note(self, client_id, meeting_date, meeting_time, meeting_location=None, weather=None,
                 initial_state=None, initial_state_score=None, request=None,
                 meeting_progress=None, techniques_used=None, meeting_outcome=None,
                 final_state=None, final_state_score=None):
        self.cursor.execute('''
            INSERT INTO Notes (client_id, meeting_date, meeting_time, meeting_location, weather,
                               initial_state, initial_state_score, request,
                               meeting_progress, techniques_used, meeting_outcome,
                               final_state, final_state_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, meeting_date, meeting_time, meeting_location, weather,
              initial_state, initial_state_score, request,
              meeting_progress, techniques_used, meeting_outcome,
              final_state, final_state_score))
        self.conn.commit()

    def get_notes_for_client(self, client_id):
        self.cursor.execute('''
            SELECT note_id, meeting_date, meeting_time, initial_state, final_state
            FROM Notes
            WHERE client_id = ?
            ORDER BY meeting_date DESC, meeting_time DESC
        ''', (client_id,))
        return self.cursor.fetchall()

    def get_all_notes_with_client_info(self):
        self.cursor.execute('''
            SELECT n.note_id, n.meeting_date, n.meeting_time, c.full_name, c.client_id
            FROM Notes n
            JOIN Clients c ON n.client_id = c.client_id
            ORDER BY n.meeting_date DESC, n.meeting_time DESC
        ''')
        return self.cursor.fetchall()

    def get_note_details(self, note_id):
        self.cursor.execute('''
            SELECT n.*, c.full_name, c.age, c.phone_number
            FROM Notes n
            JOIN Clients c ON n.client_id = c.client_id
            WHERE n.note_id = ?
        ''', (note_id,))
        return self.cursor.fetchone()

    def delete_note(self, note_id):
        self.cursor.execute('DELETE FROM Notes WHERE note_id = ?', (note_id,))
        self.conn.commit()

    def delete_client(self, client_id):
        self.cursor.execute('DELETE FROM Clients WHERE client_id = ?', (client_id,))
        self.conn.commit()

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None