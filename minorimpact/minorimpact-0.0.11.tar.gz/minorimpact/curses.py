import curses

# Request a string from the user.
def getstring(stdscr, prompt_string, maxlength=40):
    curses.echo()
    stdscr.addstr(curses.LINES-1, 0, prompt_string)
    stdscr.refresh()
    input = stdscr.getstr(curses.LINES-1, len(prompt_string), maxlength).decode(encoding='utf-8')
    curses.noecho()
    return input

def highlight(stdscr, select_y, select_x, mark_y, mark_x):
    selected = ""
    if (mark_y is not None and mark_x is not None):
        sy = select_y
        sx = select_x
        my = mark_y
        mx = mark_x
        if (my < sy):
            foo = sy
            sy = my
            my = foo
            foo = sx
            sx = mx
            mx = foo
        elif (mark_y == select_y):
            if (mark_x < select_x):
                foo = select_x
                sx = mark_x
                mx = foo

        if (my == sy):
            for x in range(sx, mx+1):
                stdscr.chgat(sy, x, 1, curses.A_REVERSE)
                #selected += str(stdscr.inch(sy, x))
                selected += chr(stdscr.inch(sy, x) & 0xFF)
        else:
            for y in range(sy, my+1):
                if (y==sy):
                    for x in range(sx, curses.COLS-2):
                        stdscr.chgat(y, x, 1, curses.A_REVERSE)
                        #selected += str(stdscr.inch(y, x))
                        selected += chr(stdscr.inch(y, x) & 0xFF)
                elif (y > sy and y < my):
                    for x in range(0, curses.COLS-2):
                        stdscr.chgat(y, x, 1, curses.A_REVERSE)
                        #selected += str(stdscr.inch(y, x))
                        selected += chr(stdscr.inch(y, x) & 0xFF)
                elif (y > sy and y==my):
                    for x in range(0, mx+1):
                        stdscr.chgat(y, x, 1, curses.A_REVERSE)
                        #selected += str(stdscr.inch(y, x))
                        selected += chr(stdscr.inch(y, x) & 0xFF)
                if (y < my):
                    selected = f"{selected}\n"
    else:
        stdscr.chgat(select_y, select_x, 1, curses.A_REVERSE)
        selected = chr(stdscr.inch(select_y, select_x) & 0xFF)
    return selected


