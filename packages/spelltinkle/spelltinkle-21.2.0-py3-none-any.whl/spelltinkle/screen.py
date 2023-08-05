import os
import locale
import curses

from .color import highlight_codes, RGB


class Screen:
    def __init__(self, size=None, corner=(0, 0)):
        self.win = None
        self.attrs = []

        if size is None:
            size = os.get_terminal_size()

        self.size = size
        self.w, self.h = size
        self.corner = corner

        self.keys = []
        self.children = []

    def start(self):
        self.win = curses.initscr()

        if hasattr(self.win, 'get_wch'):
            get_wch = self.win.get_wch
        else:
            def get_wch():
                key = self.win.getch()
                if key < 127:
                    key = chr(key)
                return key

        self.get_wch = get_wch

        os.putenv('ESCDELAY', '25')
        curses.noecho()
        curses.cbreak()
        curses.raw()
        curses.meta(1)
        curses.mousemask(-1)
        self.win.keypad(1)
        curses.start_color()

        i = 17
        for rgb in [(950, 950, 950),  # text bg
                    (850, 850, 850),  # current line bg
                    (900, 500, 500),  # highlight bg
                    (500, 900, 500),  # selected text bg
                    (700, 700, 700),  # tabs + status bg
                    (700, 0, 0),  # tabs: modified
                    (0, 700, 0),  # tabs: not modified
                    (1000, 1000, 0),  # line number bg1
                    (800, 800, 0),  # line number bg2
                    (600, 150, 150),  # line numbers
                    (0, 0, 0),  # status line
                    (400, 500, 400)  # empty space
                    ]:
            curses.init_color(i, *rgb)
            i += 1

        colors = {}
        ca = []
        for code in highlight_codes:
            if code[0] == '_':
                attr = curses.A_UNDERLINE
                code = code[1:-1]
            elif code[0] == '*':
                attr = curses.A_BOLD
                code = code[1:-1]
            else:
                attr = 0
            code = code or 'black'
            if code not in colors:
                colors[code] = i
                rgb = RGB[code]
                curses.init_color(i, *(int(c / 0.255) for c in rgb))
                i += 1
            ca.append((colors[code], attr))

        self.attrs = []
        p = 1
        for bg in [1, 2, 3, 4]:
            for fg, attr in ca:
                curses.init_pair(p, fg, bg + 16)
                self.attrs.append(curses.color_pair(p) | attr)
                p += 1

        for fg, bg in [(7, 1),
                       (6, 1),
                       (7, 5),
                       (6, 5),
                       (11, 5),
                       (10, 8),
                       (10, 9),
                       (11, 12)]:
            curses.init_pair(p, fg + 16, bg + 16)
            self.attrs.append(curses.color_pair(p))
            p += 1

        locale.setlocale(locale.LC_ALL, '')

    def resize(self, size=None):
        if size is None:
            size = os.get_terminal_size()
            self.size = size
            self.w, self.h = size
            for child in self.children:
                child.resize(size)
        else:
            if self.h == 1:
                self.w = size.columns
                self.size = os.terminal_size((self.w, 1))
                if self.corner[1] > 0:
                    self.corner = (0, size.lines - 1)
            else:
                self.size = os.terminal_size((size.columns, size.lines - 2))
                self.w, self.h = self.size

    def write(self, text=' ', colors=0):
        if isinstance(colors, int):
            colors = [colors] * len(text)
        c0 = None
        for x, color in zip(text, colors):
            if color != c0:
                a = self.attrs[color]
                c0 = color
            try:
                self.win.addstr(x, a)
            except curses.error:
                pass

    def input(self) -> str:
        if self.keys:
            return self.keys.pop(0)
        key = self.get_wch()
        if isinstance(key, str):
            i = ord(key)
            name = {0: '^ ',
                    9: 'tab',
                    10: 'enter',
                    27: 'esc'}.get(i)
            if name is not None:
                return name
            if i < 27:
                return '^' + chr(96 + i)
            return key

        if key == curses.KEY_MOUSE:
            id, x, y, z, event = curses.getmouse()
            self.position = x, y
            key = {curses.BUTTON1_CLICKED: 'mouse1_clicked',
                   curses.BUTTON1_PRESSED: 'mouse1_pressed',
                   curses.BUTTON1_RELEASED: 'mouse1_released',
                   curses.BUTTON2_PRESSED: 'mouse2_clicked',
                   curses.BUTTON2_CLICKED: 'mouse2_clicked',
                   curses.BUTTON4_PRESSED: ['scroll_up'] * 6,
                   2097152: ['scroll_down'] * 3,
                   134217728: ['scroll_down'] * 3}.get(event, 'unknown')
            if isinstance(key, list):
                self.keys = key
                key = key.pop(0)
            return key

        return {curses.KEY_UP: 'up',
                curses.KEY_DOWN: 'down',
                curses.KEY_RIGHT: 'right',
                curses.KEY_LEFT: 'left',
                curses.KEY_HOME: 'home',
                curses.KEY_END: 'end',
                curses.KEY_PPAGE: 'page_up',
                curses.KEY_NPAGE: 'page_down',
                curses.KEY_F5: 'F5',
                curses.KEY_F6: 'F6',
                curses.KEY_F7: 'F7',
                curses.KEY_F8: 'F8',
                curses.KEY_F9: 'F9',
                curses.KEY_F10: 'F10',
                566: 'ctrl_up',
                525: 'ctrl_down',
                560: 'ctrl_right',
                545: 'ctrl_left',
                574: 'ctrl_up',
                531: 'ctrl_down',
                568: 'ctrl_right',
                553: 'ctrl_left',
                curses.KEY_IC: 'insert',
                curses.KEY_DC: 'delete',
                curses.KEY_SDC: 'delete_more',
                curses.KEY_BACKSPACE: 'bs',
                127: 'bs',
                curses.KEY_RESIZE: 'resize'}.get(key, 'unknown')

    def refresh(self):
        self.win.refresh()

    def move(self, y, x):
        self.win.move(y + self.corner[1], x)
        self.c = x

    def stop(self):
        self.win.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def subwin(self, h, w, ch, cw):
        scr = Screen(os.terminal_size((w, h)), (cw, ch))
        scr.win = self.win
        scr.attrs = self.attrs
        self.children.append(scr)
        return scr


if __name__ == '__main__':
    import curses as c
    s = c.initscr()
    c.noecho()
    c.cbreak()
    c.raw()
    mm = c.mousemask(-1)

    s.keypad(True)
    c.start_color()
    cc2 = c.can_change_color()
    # y = c.init_color(1, 0, 1000, 0)
    # y = c.init_color(2, 0, 0, 1000)
    # y = c.init_pair(1, 1, 2)
    y = c.color_pair(1)
    s.move(0, 0)
    s.addstr('d')
    s.addstr('d')
    s.refresh()
    while 1:
        while 1:
            x = s.get_wch()
            break

        if x == c.KEY_MOUSE:
            xx = c.getmouse()
            yy = ''
            for t in dir(c):
                if t.startswith('BUTTON'):
                    if xx[4] & getattr(c, t):
                        yy += t
            print(x, xx, yy)

        if x == 'q':
            s.keypad(False)
            c.echo()
            c.nocbreak()
            c.endwin()
            break

        print(ord(x) if isinstance(x, str) else x)
        # print(x, type(x), c.COLOR_PAIRS, yy, c.COLORS, cc2)
        for y0 in dir(c):
            if getattr(c, y0) == x:
                print(y0)
