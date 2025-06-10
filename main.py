from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.core.window import Window
from datetime import datetime
import os

# Импортируем наш менеджер базы данных
from database import DatabaseManager

# Загружаем Kivy Lang файл
import sys
import os
from kivy.lang import Builder

# Определяем путь к файлу .kv
kv_file_path = 'kivy_ui.kv'

# Если приложение запущено через PyInstaller
if getattr(sys, 'frozen', False):
    # sys._MEIPASS - это временная папка, куда PyInstaller распаковывает ресурсы
    kv_file_path = os.path.join(sys._MEIPASS, kv_file_path)

# Загружаем Kivy Lang файл
Builder.load_file(kv_file_path)

class MainScreen(Screen):
    pass

class CreateNoteScreen(Screen):
    client_id_input = NumericProperty(None)
    full_name_input = StringProperty('')
    age_input = StringProperty('')
    phone_input = StringProperty('')
    meeting_date_input = StringProperty(datetime.now().strftime("%Y-%m-%d"))
    meeting_time_input = StringProperty(datetime.now().strftime("%H:%M"))
    meeting_location_input = StringProperty('')
    weather_input = StringProperty('')
    initial_state_input = StringProperty('')
    initial_state_score_input = StringProperty('')
    request_input = StringProperty('')
    meeting_progress_input = StringProperty('')
    techniques_input = StringProperty('')
    outcome_input = StringProperty('')
    final_state_input = StringProperty('')
    final_state_score_input = StringProperty('')

    # Используется для редактирования заметки
    current_note_id = NumericProperty(0)
    delete_button_visible = ObjectProperty(False)

    def on_enter(self, *args):
        # При входе на экран, если current_note_id не 0, значит это редактирование
        if self.current_note_id != 0:
            self.load_note_data(self.current_note_id)
            self.delete_button_visible = True
        else:
            # Сброс полей для новой заметки
            self.reset_fields()
            self.delete_button_visible = False
            # Автозаполнение текущей даты и времени
            self.meeting_date_input = datetime.now().strftime("%Y-%m-%d")
            self.meeting_time_input = datetime.now().strftime("%H:%M")

    def reset_fields(self):
        self.client_id_input = 0
        self.full_name_input = ''
        self.age_input = ''
        self.phone_input = ''
        self.meeting_location_input = ''
        self.weather_input = ''
        self.initial_state_input = ''
        self.initial_state_score_input = ''
        self.request_input = ''
        self.meeting_progress_input = ''
        self.techniques_input = ''
        self.outcome_input = ''
        self.final_state_input = ''
        self.final_state_score_input = ''
        self.current_note_id = 0

    def load_note_data(self, note_id):
        db_manager = App.get_running_app().db_manager
        note_details = db_manager.get_note_details(note_id)
        if note_details:
            self.client_id_input = note_details[1] # client_id
            self.full_name_input = note_details[14] # full_name из JOIN
            self.age_input = str(note_details[15]) if note_details[15] is not None else '' # age
            self.phone_input = note_details[16] if note_details[16] is not None else '' # phone_number

            self.meeting_date_input = note_details[2]
            self.meeting_time_input = note_details[3]
            self.meeting_location_input = note_details[4] if note_details[4] is not None else ''
            self.weather_input = note_details[5] if note_details[5] is not None else ''
            self.initial_state_input = note_details[6] if note_details[6] is not None else ''
            self.initial_state_score_input = str(note_details[7]) if note_details[7] is not None else ''
            self.request_input = note_details[8] if note_details[8] is not None else ''
            self.meeting_progress_input = note_details[9] if note_details[9] is not None else ''
            self.techniques_input = note_details[10] if note_details[10] is not None else ''
            self.outcome_input = note_details[11] if note_details[11] is not None else ''
            self.final_state_input = note_details[12] if note_details[12] is not None else ''
            self.final_state_score_input = str(note_details[13]) if note_details[13] is not None else ''
            self.current_note_id = note_id
        else:
            self.reset_fields()
            self.manager.current = 'main' # На всякий случай, если заметка не найдена

    def save_note(self):
        db_manager = App.get_running_app().db_manager

        # Простая валидация
        if not self.full_name_input or not self.meeting_date_input or not self.meeting_time_input:
            self.show_popup("Ошибка", "ФИО клиента, дата и время встречи обязательны.")
            return

        # Проверяем, существует ли клиент по ФИО. Если нет, создаем нового.
        # Для простоты, здесь ищем только по ФИО. В реальном приложении лучше добавить выбор клиента из списка.
        client_id = self.client_id_input
        if not client_id: # Если клиент еще не выбран/привязан
            clients = db_manager.get_clients(search_query=self.full_name_input)
            found_client = None
            for client in clients:
                if client[1] == self.full_name_input: # Сравниваем полное имя
                    found_client = client
                    break

            if found_client:
                client_id = found_client[0]
            else:
                # Если клиент не найден, создаем нового
                try:
                    client_id = db_manager.add_client(
                        full_name=self.full_name_input,
                        age=int(self.age_input) if self.age_input else None,
                        phone_number=self.phone_input if self.phone_input else None
                    )
                except ValueError:
                    self.show_popup("Ошибка", "Возраст должен быть числом.")
                    return
        else:
            # Если client_id уже есть (при загрузке заметки), обновляем данные клиента
            # (предполагая, что они могли быть изменены на форме)
            try:
                db_manager.update_client(
                    client_id=client_id,
                    full_name=self.full_name_input,
                    age=int(self.age_input) if self.age_input else None,
                    phone_number=self.phone_input if self.phone_input else None,
                    temperament=None, character_type=None, perception_type=None, anamnesis=None, help_plan=None, requests=[]
                )
            except ValueError:
                self.show_popup("Ошибка", "Возраст должен быть числом.")
                return


        initial_score = int(self.initial_state_score_input) if self.initial_state_score_input else None
        final_score = int(self.final_state_score_input) if self.final_state_score_input else None

        if self.current_note_id == 0: # Создаем новую заметку
            db_manager.add_note(
                client_id=client_id,
                meeting_date=self.meeting_date_input,
                meeting_time=self.meeting_time_input,
                meeting_location=self.meeting_location_input,
                weather=self.weather_input,
                initial_state=self.initial_state_input,
                initial_state_score=initial_score,
                request=self.request_input,
                meeting_progress=self.meeting_progress_input,
                techniques_used=self.techniques_input,
                meeting_outcome=self.outcome_input,
                final_state=self.final_state_input,
                final_state_score=final_score
            )
            self.show_popup("Успех", "Заметка успешно создана!")
        else: # Обновляем существующую заметку
            # Для простоты, здесь нет отдельной функции update_note,
            # но можно добавить ее в DatabaseManager
            # Сейчас просто удаляем и добавляем заново (не оптимально, но для примера сойдет)
            db_manager.delete_note(self.current_note_id) # Удаляем старую
            db_manager.add_note( # Добавляем новую
                client_id=client_id,
                meeting_date=self.meeting_date_input,
                meeting_time=self.meeting_time_input,
                meeting_location=self.meeting_location_input,
                weather=self.weather_input,
                initial_state=self.initial_state_input,
                initial_state_score=initial_score,
                request=self.request_input,
                meeting_progress=self.meeting_progress_input,
                techniques_used=self.techniques_input,
                meeting_outcome=self.outcome_input,
                final_state=self.final_state_input,
                final_state_score=final_score
            )
            self.show_popup("Успех", "Заметка успешно обновлена!")

        self.reset_fields()
        self.manager.current = 'main' # Возвращаемся на главный экран

    def delete_note_from_db(self):
        if self.current_note_id != 0:
            db_manager = App.get_running_app().db_manager
            db_manager.delete_note(self.current_note_id)
            self.show_popup("Удаление", "Заметка удалена.")
            self.reset_fields()
            self.manager.current = 'history' # Возвращаемся в историю после удаления

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical', padding=10)
        popup_content.add_widget(Label(text=message, size_hint_y=None, height=40))
        close_button = Button(text='Закрыть', size_hint_y=None, height=40)
        popup_content.add_widget(close_button)

        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        close_button.bind(on_release=popup.dismiss)
        popup.open()


class HistoryScreen(Screen):
    notes_grid = ObjectProperty(None) # Ссылка на GridLayout из .kv файла

    def on_enter(self, *args):
        self.load_notes()

    def load_notes(self):
        self.notes_grid.clear_widgets() # Очищаем сетку перед загрузкой
        db_manager = App.get_running_app().db_manager
        all_notes = db_manager.get_all_notes_with_client_info()

        # Для 3 заметок по вертикали и 5 по горизонтали (15 заметок на "странице")
        # В реальном приложении нужна пагинация или динамическая загрузка,
        # но для начала просто отобразим все.
        # В Kivy GridLayout работает иначе, columns = 5 означает 5 колонок, строк будет столько, сколько нужно.
        # Поэтому 3 по вертикали и 5 по горизонтали - это просто 5 колонок.
        # Если вы хотите, чтобы было 3 ряда, то нужно ограничить кол-во заметок.
        
        # Давайте отобразим их в виде списка для удобства, как в стандартных заметках
        # Каждая заметка - это Button с информацией
        for note in all_notes:
            note_id, date, time, client_name, client_id = note
            note_text = f"{date} {time}\n{client_name}"
            btn = Button(
                text=note_text,
                size_hint_y=None,
                height=dp(100), # dp() для адаптивного размера
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1), # Светлый фон
                color=(0, 0, 0, 1), # Черный текст
                halign='left',
                valign='top',
                text_size=(self.notes_grid.width - dp(20), None) # Адаптивный размер текста
            )
            btn.bind(on_release=lambda x, nid=note_id: self.open_note(nid))
            self.notes_grid.add_widget(btn)

    def open_note(self, note_id):
        # Передаем ID заметки на экран создания/редактирования
        self.manager.get_screen('create_note').current_note_id = note_id
        self.manager.current = 'create_note'


class ClientsScreen(Screen):
    client_list_layout = ObjectProperty(None) # Ссылка на BoxLayout из .kv
    search_input = ObjectProperty(None)

    def on_enter(self, *args):
        self.load_clients()

    def load_clients(self, search_query=''):
        self.client_list_layout.clear_widgets()
        db_manager = App.get_running_app().db_manager
        clients = db_manager.get_clients(search_query=search_query)

        for client in clients:
            client_id, full_name, age, phone = client
            client_label = Button(
                text=full_name,
                size_hint_y=None,
                height=dp(60),
                background_normal='',
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0,0,0,1),
                halign='left',
                valign='middle',
                text_size=(self.client_list_layout.width - dp(20), None)
            )
            client_label.bind(on_release=lambda x, cid=client_id: self.open_client_card(cid))
            self.client_list_layout.add_widget(client_label)

    def open_client_card(self, client_id):
        self.manager.get_screen('client_card').current_client_id = client_id
        self.manager.current = 'client_card'

    def add_new_client(self):
        self.manager.get_screen('client_card').current_client_id = 0 # 0 для нового клиента
        self.manager.current = 'client_card'


class ClientCardScreen(Screen):
    current_client_id = NumericProperty(0) # 0 означает создание нового клиента
    full_name_input = StringProperty('')
    age_input = StringProperty('')
    phone_input = StringProperty('')
    temperament_input = StringProperty('')
    character_type_input = StringProperty('')
    perception_type_input = StringProperty('')
    anamnesis_input = StringProperty('')
    help_plan_input = StringProperty('')

    requests_container = ObjectProperty(None) # BoxLayout для динамического добавления запросов
    client_notes_layout = ObjectProperty(None) # GridLayout для заметок клиента

    def on_enter(self, *args):
        self.load_client_data()
        self.load_client_notes()

    def load_client_data(self):
        self.requests_container.clear_widgets() # Очищаем предыдущие запросы

        if self.current_client_id != 0:
            db_manager = App.get_running_app().db_manager
            client_data, client_requests = db_manager.get_client_details(self.current_client_id)
            if client_data:
                self.full_name_input = client_data[0]
                self.age_input = str(client_data[1]) if client_data[1] is not None else ''
                self.phone_input = client_data[2] if client_data[2] is not None else ''
                self.temperament_input = client_data[3] if client_data[3] is not None else ''
                self.character_type_input = client_data[4] if client_data[4] is not None else ''
                self.perception_type_input = client_data[5] if client_data[5] is not None else ''
                self.anamnesis_input = client_data[6] if client_data[6] is not None else ''
                self.help_plan_input = client_data[7] if client_data[7] is not None else ''

                if client_requests:
                    for req_text in client_requests:
                        self.add_request_input_field(req_text)
            else: # Если клиент не найден (например, был удален)
                self.reset_fields()
                self.manager.current = 'clients'
        else: # Создание нового клиента
            self.reset_fields()
            self.add_request_input_field() # Добавляем одно пустое поле для запроса

    def load_client_notes(self):
        self.client_notes_layout.clear_widgets()
        if self.current_client_id != 0:
            db_manager = App.get_running_app().db_manager
            notes = db_manager.get_notes_for_client(self.current_client_id)
            for note in notes:
                note_id, date, time, initial_state, final_state = note
                note_text = f"{date} {time}\nНачальное: {initial_state}\nКонечное: {final_state}"
                btn = Button(
                    text=note_text,
                    size_hint_y=None,
                    height=dp(100),
                    background_normal='',
                    background_color=(0.9, 0.9, 0.9, 1),
                    color=(0, 0, 0, 1),
                    halign='left',
                    valign='top',
                    text_size=(self.client_notes_layout.width - dp(20), None)
                )
                btn.bind(on_release=lambda x, nid=note_id: self.open_note_from_client_card(nid))
                self.client_notes_layout.add_widget(btn)

    def open_note_from_client_card(self, note_id):
        self.manager.get_screen('create_note').current_note_id = note_id
        self.manager.current = 'create_note'

    def add_request_input_field(self, text=''):
        request_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        text_input = TextInput(text=text, multiline=False, size_hint_x=0.9, background_color=(0.95,0.95,0.95,1))
        remove_button = Button(text='X', size_hint_x=0.1, background_color=(1,0.5,0.5,1))
        remove_button.bind(on_release=lambda x: self.requests_container.remove_widget(request_input_layout))
        request_input_layout.add_widget(text_input)
        request_input_layout.add_widget(remove_button)
        self.requests_container.add_widget(request_input_layout)

    def save_client(self):
        db_manager = App.get_running_app().db_manager

        if not self.full_name_input:
            self.show_popup("Ошибка", "ФИО клиента обязательно.")
            return

        age_val = None
        if self.age_input:
            try:
                age_val = int(self.age_input)
            except ValueError:
                self.show_popup("Ошибка", "Возраст должен быть числом.")
                return

        requests_list = [
            child.children[1].text # text_input - это второй ребенок в BoxLayout
            for child in self.requests_container.children
            if isinstance(child, BoxLayout) and len(child.children) == 2 # Убеждаемся, что это наше поле ввода запроса
        ]
        # Отфильтровываем пустые запросы
        requests_list = [req for req in requests_list if req.strip()]

        if self.current_client_id == 0: # Создаем нового клиента
            db_manager.add_client(
                full_name=self.full_name_input,
                age=age_val,
                phone_number=self.phone_input,
                temperament=self.temperament_input,
                character_type=self.character_type_input,
                perception_type=self.perception_type_input,
                anamnesis=self.anamnesis_input,
                help_plan=self.help_plan_input,
                requests=requests_list
            )
            self.show_popup("Успех", "Клиент успешно добавлен!")
        else: # Обновляем существующего клиента
            db_manager.update_client(
                client_id=self.current_client_id,
                full_name=self.full_name_input,
                age=age_val,
                phone_number=self.phone_input,
                temperament=self.temperament_input,
                character_type=self.character_type_input,
                perception_type=self.perception_type_input,
                anamnesis=self.anamnesis_input,
                help_plan=self.help_plan_input,
                requests=requests_list
            )
            self.show_popup("Успех", "Данные клиента обновлены!")

        self.reset_fields()
        self.manager.current = 'clients' # Возвращаемся к списку клиентов

    def delete_current_client(self):
        if self.current_client_id != 0:
            db_manager = App.get_running_app().db_manager
            db_manager.delete_client(self.current_client_id)
            self.show_popup("Удаление", "Клиент и все его заметки удалены.")
            self.reset_fields()
            self.manager.current = 'clients' # Возвращаемся к списку клиентов

    def reset_fields(self):
        self.current_client_id = 0
        self.full_name_input = ''
        self.age_input = ''
        self.phone_input = ''
        self.temperament_input = ''
        self.character_type_input = ''
        self.perception_type_input = ''
        self.anamnesis_input = ''
        self.help_plan_input = ''
        self.requests_container.clear_widgets() # Очищаем поля запросов
        self.client_notes_layout.clear_widgets() # Очищаем заметки клиента

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical', padding=10)
        popup_content.add_widget(Label(text=message, size_hint_y=None, height=40))
        close_button = Button(text='Закрыть', size_hint_y=None, height=40)
        popup_content.add_widget(close_button)

        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        close_button.bind(on_release=popup.dismiss)
        popup.open()


class PsychologistNotesApp(App):
    db_manager = ObjectProperty(None)

    def build(self):
        # Инициализируем менеджер базы данных
        self.db_manager = DatabaseManager()

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CreateNoteScreen(name='create_note'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(ClientsScreen(name='clients'))
        sm.add_widget(ClientCardScreen(name='client_card'))
        return sm

    def on_stop(self):
        # Закрываем соединение с базой данных при завершении приложения
        if self.db_manager:
            self.db_manager.close()

if __name__ == '__main__':
    # Импортируем dp (density-independent pixels) для адаптивного размера
    from kivy.metrics import dp
    PsychologistNotesApp().run()