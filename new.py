from os import system
from pygame import mixer
import time
import sqlite3

class Database:
    def __init__(self, db_name="music.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Создаем таблицы, если они не существуют"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS artist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS music (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                FOREIGN KEY (artist_id) REFERENCES artist(id)
            )
        ''')
        self.conn.commit()

    def add_music(self, song_name, artist_name, path):
        """Добавляем песню в базу данных"""
        # Проверим, существует ли уже такой исполнитель
        self.cursor.execute("SELECT id FROM artist WHERE name = ?", (artist_name,))
        artist = self.cursor.fetchone()
        if artist:
            artist_id = artist[0]
        else:
            # Добавим нового исполнителя
            self.cursor.execute("INSERT INTO artist (name) VALUES (?)", (artist_name,))
            artist_id = self.cursor.lastrowid

        # Добавляем песню
        self.cursor.execute("INSERT INTO music (title, artist_id, path) VALUES (?, ?, ?)",
                            (song_name, artist_id, path))
        self.conn.commit()

    def delete_music(self, song_name):
        """Удаляем песню из базы данных"""
        self.cursor.execute("DELETE FROM music WHERE title = ?", (song_name,))
        self.conn.commit()

    def get_all_music(self):
        """Получаем все песни из базы данных"""
        self.cursor.execute('''
            SELECT music.id, music.title, artist.name, music.path
            FROM music
            JOIN artist ON music.artist_id = artist.id
        ''')
        songs = self.cursor.fetchall()
        for song in songs:
            print(f"{song[0]}. {song[1]} - {song[2]} ({song[3]})")

    def close(self):
        """Закрыть соединение с базой данных"""
        self.conn.close()


class MusicApp:
    def __init__(self, db):
        self.db = db
        self.path_play = None

    def start(self) -> None:
        menu = """
        1. Добавить песню
        2. Удалить песню
        3. Просмотреть все песни
        4. Воспроизвести песню
        5. Выйти
        """
        try:
            start_menu = int(input(menu))
            while start_menu not in range(1, 6):
                print("Ошибка. Пожалуйста, введите число от 1 до 5.")
                start_menu = int(input(menu))

            if start_menu == 1:
                self.add_song()
            elif start_menu == 2:
                self.delete_song()
            elif start_menu == 3:
                self.show_all_songs()
            elif start_menu == 4:
                self.play_song()
            elif start_menu == 5:
                print("Выход из программы...")
                self.db.close()  # Закрытие соединения с БД
                exit()

        except ValueError:
            print("Ошибка: ввод должен быть числом.")
            self.start()

    def add_song(self):
        song_name = input("Введите название песни: ")
        artist_name = input("Введите имя исполнителя или название группы: ")
        path = input("Введите путь к файлу формата .mp3: ")

        if path.endswith(".mp3"):
            self.db.add_music(song_name, artist_name, path)
            print(f"Песня '{song_name}' успешно добавлена.")
        else:
            print("Ошибка: путь должен указывать на файл формата .mp3.")
        
        self.start()

    def delete_song(self):

        song_name = input("Введите название песни для удаления: ")
        self.db.delete_music(song_name)
        print(f"Песня '{song_name}' была успешно удалена.")
        self.start()

    def show_all_songs(self):
        system("clear")
        print("Список всех доступных песен:")
        self.db.get_all_music()
        input("\nНажмите Enter, чтобы вернуться в меню...")
        self.start()

    def play_song(self):
        system("clear")
        print("Выберите песню для воспроизведения:")
        self.db.get_all_music()
        try:
            choice = int(input("Введите id песни: "))
            result = self.db.cursor.execute(
                "SELECT title, artist_id, path FROM music WHERE id = ?", 
                (choice,)
            ).fetchone()

            if result:
                song_to_play = result[0]
                author_to_play = self.db.cursor.execute(
                    "SELECT name FROM artist WHERE id = ?", 
                    (result[1],)
                ).fetchone()[0]
                path_to_play = result[2]

                self.music_play(song_to_play, author_to_play, path_to_play)
            else:
                print("Ошибка: песня с таким id не найдена.")
                self.start()

        except ValueError:
            print("Ошибка: введите корректный id.")
            self.start()

    def music_play(self, song: str, author: str, path_play: str):
        try:
            self.path_play = path_play
            mixer.init()
            mixer.music.load(self.path_play)
            mixer.music.play()

            mus_length = int(mixer.Sound(self.path_play).get_length())
            time_elapsed = 0

            print(f"Сейчас играет: {song} - {author}")
            print(f"Длительность: {mus_length} секунд")

            while mixer.music.get_busy():
                time.sleep(1)
                time_elapsed += 1
                progress = int((time_elapsed / mus_length) * 10) * '▮'
                remaining = (10 - int((time_elapsed / mus_length) * 10)) * '▯'
                print(f"\r[{progress}{remaining}] {time_elapsed}/{mus_length} секунд", end="")

            print("\nВоспроизведение завершено.")
            self.start()

        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            self.start()


# Пример использования:
db = Database()
app = MusicApp(db)
app.start()

