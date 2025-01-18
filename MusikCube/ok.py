import curses


def main(stdscr):
    # Инициализация цветов
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Прячет курсор
    curses.curs_set(0)

    # Настройка начальных параметров
    menu_items = ["Artists", "Albums", "Tracks", "Now Playing", "Exit"]
    current_index = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Заголовок
        stdscr.addstr(0, 0, "Musikcube-like Interface".center(width), curses.color_pair(1) | curses.A_BOLD)

        # Отображение меню
        for idx, item in enumerate(menu_items):
            x = 3
            y = 2 + idx
            if idx == current_index:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(y, x, f" {item} ")
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addstr(y, x, f" {item} ", curses.color_pair(2))

        # Обработка клавиш
        key = stdscr.getch()

        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(menu_items) - 1:
            current_index += 1
        elif key == 10:  # Нажатие Enter
            if menu_items[current_index] == "Exit":
                break
            show_selection(stdscr, width, menu_items[current_index])
        elif key == 27:  # ESC
            break


def show_selection(stdscr, width, selection):
    stdscr.clear()
    message = f"You selected: {selection}"
    stdscr.addstr(10, (width - len(message)) // 2, message)
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
