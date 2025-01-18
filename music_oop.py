import time
import asciimatics
from pygame import mixer
import sqlite3
from asciimatics.screen import KeyboardEvent, Screen
from os import system


COLOUR_BLACK = 0
COLOUR_RED = 1
COLOUR_GREEN = 2
COLOUR_YELLOW = 3
COLOUR_BLUE = 4
COLOUR_MAGENTA = 5
COLOUR_CYAN = 6
COLOUR_WHITE = 7

A_BOLD = 1
A_NORMAL = 2
A_REVERSE = 3
A_UNDERLINE = 4


h = 0
m = 0
s = 0

menu = """
    Выберите одну из доступных опции:
---------------------------------------
| 1. Добавить песню в приложение      |
| 2. Удалить песню из приложения      |
| 3. Вывести список всех песен        |
| 4. Проиграть песню                  |
| 5. Вывести меню                     |
| 6. Выйти из приложения              |
---------------------------------------
"""

class Database():

    def __init__(self, db_name:str):
        self.con = sqlite3.connect(db_name)
        self.cursor = self.con.cursor()

    def add_music(self, title, artist, path) -> None:
        is_artist = self.cursor.execute("""
        SELECT COUNT(artist.id) as cnt, artist.id
        FROM
        artist
        WHERE
        artist.name = ? """, (artist,))
        fetched = is_artist.fetchall()
        cnt_artist = fetched[:][0][0]
        id_artist = fetched[:][0][1]
        if cnt_artist == 1:
            self.cursor.execute("INSERT INTO music(title, artist_id, path) VALUES(?, ?, ?)", (title, id_artist, path))
            print(cnt_artist)
            self.con.commit()
        else:
            self.cursor.execute("INSERT INTO artist(name) VALUES(?)", (artist,))
            self.con.commit()
            is_artist = self.cursor.execute("""
            SELECT COUNT(artist.id) as cnt, artist.id
            FROM
            artist
            WHERE
            artist.name = ? """, (artist,))
            id_artist = is_artist.fetchall()[0][1]
            self.cursor.execute("INSERT INTO music(title, artist_id, path) VALUES(?, ?, ?)", (title, id_artist, path))
            self.con.commit()
    
    def get_music(self, song_id) -> None:
        song_path = self.cursor.execute("SELECT path from music WHERE music.id = ?", (song_id,))
        return song_path.fetchall()[0][0]

    def delete_music(self, title) -> None:
        self.cursor.execute("DELETE FROM music WHERE music.title = ?", (title, ))
        self.con.commit()

    def get_all_music(self) -> None:
        result = self.cursor.execute("SELECT * FROM music")
        for i in result.fetchall():
            art = self.cursor.execute("SELECT name FROM artist WHERE id = ?", (i[3], ))
            print(str(i[0]) + ".", i[1], " ~ ", art.fetchall()[0][0])
    
    def get_artist(self, artist_id) -> None:
        art = self.cursor.execute("SELECT name FROM artists WHERE id = ?", (artist_id,))
        return art


class MusicApp():

    def __init__(self, database):
        self.db = database
        mixer.init()


    def start(self) -> None:
        start_menu = int(input(menu))
        while start_menu not in range(1, 6):
            start_menu = int(input(menu))
        if start_menu == 1:
            song_name = input("Введите название песни: ")
            artist_name = input("Введите имя исполнителя или название группы:")
            path = input("Введите путь к файлу формата .mp3: ")
            self.db.add_music(song_name, artist_name, path)
            self.start()
        if start_menu == 2:
            song_name = input("Введите название песни: ")
            self.db.delete_music(song_name)
            self.start()
        if start_menu == 3:
            system("clear")
            self.db.get_all_music()
            self.start()
        if start_menu == 4:
            system("clear")
            print("Выберите любую из доступных песен по id:")
            self.db.get_all_music()
            choice = int(input("Введите id: "))
            result = self.db.cursor.execute("SELECT title, artist_id, path FROM music WHERE id = ?", (choice,)).fetchall()[0]
            song_to_play = result[0]
            author_to_play = self.db.cursor.execute("SELECT name FROM artist WHERE id = ?", (result[1],)).fetchall()[0][0]
            path_to_play = result[2]
            self.music_play(song_to_play, author_to_play, path_to_play)


    def music_play(self, song:str, author:str, path_play:str):
        self.path_play = path_play
        mixer.music.load(self.path_play)
        mixer.music.play()
        mus_length = int(mixer.Sound(self.path_play).get_length())
        symbols = {
            "play": "▷",
            "pause": "||"
        }
        long = int(mus_length) // 10


        def demo(screen):
            playing = True
            screen.print_at("Консольный медиа-плеер", int(screen.width / 2) - 11, 0, COLOUR_MAGENTA)
            screen.print_at("-" * screen.width, 0, 1, COLOUR_RED)
            screen.refresh()
            def playingg():
                global s
                global m
                global h
                for i in range(s * 100 + m * 60 * 100, mus_length * 100 + 1):
                    if True:
                        if i % 100 == 0:
                            s += 1
                            if s % 60 == 0:
                                s = 0
                                m += 1
                            if m < 10 and s < 10:
                                screen.print_at(f"00:0{m}:0{s}     {symbols["pause"]}" + "     " + "|" + "/" * int((i / 1000)) + (
                                        long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                screen.print_at(f"Playing: {song} ~ {author}", 0, 5)
                                screen.refresh()

                            if m >= 10 and s >= 10:
                                screen.print_at(f"00:{m}:{s}     {symbols["pause"]}" + "     " + "|" + "/" * int((i / 1000)) + (
                                            long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                screen.print_at(f"Playing: {song} - {author}", 0, 5)
                                screen.refresh()


                            if m >= 10 and s < 10:
                                screen.print_at(f"00:{m}:0{s}     {symbols["pause"]}" + "     " + "|" + "/" * int((i / 1000)) + (
                                            long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                screen.print_at(f"Playing: {song} - {author}", 0, 3)

                                screen.refresh()

                            if m < 10 and s >= 10:
                                screen.print_at(f"00:0{m}:{s}     {symbols["pause"]}" + "     " + "|" + "/" * int((i / 1000)) + (
                                            long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                screen.refresh()

                        x = screen.get_event()
                        if x:
                            if isinstance(x, KeyboardEvent):
                                if chr(x.key_code) in ("p", "P", "з", "З"):
                                    screen.refresh()
                                    mixer.music.stop()
                                    screen.refresh()

                                    if m < 10 and s < 10:
                                        screen.print_at(
                                            f"00:0{m}:0{s}     {symbols["play"]}" + "      " + "|" + "/" * int((i / 1000)) + (
                                                    long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                        screen.refresh()
                                    if m >= 10 and s >= 10:
                                        screen.print_at(
                                            f"00:{m}:{s}     {symbols["play"]}" + "      " + "|" + "/" * int((i / 1000)) + (
                                                    long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                        screen.refresh()

                                    if m >= 10 and s < 10:
                                        screen.print_at(
                                            f"00:{m}:0{s}     {symbols["play"]}" + "      " + "|" + "/" * int((i / 1000)) + (
                                                    long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                        screen.refresh()

                                    if m < 10 and s >= 10:
                                        screen.print_at(
                                            f"00:0{m}:{s}     {symbols["play"]}" + "      " + "|" + "/" * int((i / 1000)) + (
                                                    long - int(i / 1000)) * " " + "|" + " " * 20, 0, 2)
                                        screen.refresh()
                                    return False

                        time.sleep(0.01)
            playingg()

            for j in range(10000):
                x = screen.get_event()
                time.sleep(0.01)
                if x:
                    if isinstance(x, KeyboardEvent):
                        if chr(x.key_code) in ("p", "P", "з", "З"):
                            screen.print_at("", 0, 0)
                            screen.refresh()
                            mixer.music.play(start=m * 60 + s - 1)
                            playingg()
                        
        Screen.wrapper(demo)


app = MusicApp(Database("music.db"))
app.start()