import curses, random, time

#==============================================
# THE MATRIX RAIN BY DIVINEMONK 
#==============================================

try:

  SLEEP_BETWEEN_FRAME = .1 
  FALLING_SPEED = 100
  MAX_RAIN_COUNT = 10
  COLOR_STEP = 20
  NUMBER_OF_COLOR = 45 
  USE_GRADIENT = False
  START_COLOR_NUM = 128 
  HEAD_STANDOUT = curses.COLOR_WHITE | curses.A_STANDOUT  
  HEAD_BOLD = curses.COLOR_WHITE | curses.A_BOLD  

  options = {
      'head': HEAD_BOLD,
      'speed': FALLING_SPEED,
      'count': MAX_RAIN_COUNT,
      'opening_title': " ".join("A Divinemonk creation!".upper()),
      'end_title': " ".join("A Divinemonk creation!".upper()),
  }
  def config(stdscr):
      curses.curs_set(0)
      stdscr.nodelay(True)

      init_colors()

      options['count'] = MAX_COLS // 2
      options['speed'] = 1 + curses.LINES // 25
  def init_colors():
      curses.start_color()
      global USE_GRADIENT
      USE_GRADIENT = curses.can_change_color()

      if USE_GRADIENT:
          curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
          curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
          for i in range(NUMBER_OF_COLOR + 1):
              green_value = (1000 - COLOR_STEP * NUMBER_OF_COLOR) + COLOR_STEP * i
              curses.init_color(START_COLOR_NUM + i, 0, green_value, 0)
              curses.init_pair(START_COLOR_NUM + i, START_COLOR_NUM + i, curses.COLOR_BLACK)
      else:
          curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
  def get_matrix_code_chars():
      l = [chr(i) for i in range(0x21, 0x7E)]
      l.extend([chr(i) for i in range(0xFF66, 0xFF9D)])
      return l
  MATRIX_CODE_CHARS = get_matrix_code_chars()
  def random_char():
      return random.choice(MATRIX_CODE_CHARS)
  def random_rain_length():
      return random.randint(curses.LINES // 2, curses.LINES)
  def rain_forever(stdscr, pool):
      while True:
          if pool:
              x = random.choice(pool)
              pool.remove(x)
          else:
              break

          begin = random.randint(-curses.LINES // 2, curses.LINES // 3)
          if begin < 0:
              begin = 0

          end = random.randint(curses.LINES // 2, 2 * curses.LINES)
          if end > curses.LINES:
              end = curses.LINES

          should_stop = yield from rain_once(stdscr, x, begin, end)

          if should_stop:
              break
          else:
              pool.append(x)
  def rain_once(stdscr, x, begin, end, last_char=None):
      max_length = random_rain_length()
      speed = random.randint(1, options['speed'])
      r = yield from animate_rain(stdscr, x, begin, end, max_length, speed, last_char)
      return r
  def animate_rain(stdscr, x, begin, end, max_length, speed=FALLING_SPEED, last_char=None):
      head, tail = begin, begin

      head_style = options['head']

      def show_head():
          if head < end:
              stdscr.addstr(head, x, random_char(), head_style)

      def get_color(i):
          color_num = NUMBER_OF_COLOR - (head - i) + 1
          if color_num < 0:
              color_num = 0
          return curses.color_pair(START_COLOR_NUM + color_num)

      def show_body():
          if USE_GRADIENT:
              for i in range(tail, min(head, end)):
                  stdscr.addstr(i, x, random_char(), get_color(i))
          else:
              middle = head - max_length // 2
              if (middle < begin):
                  middle = begin
              for i in range(tail, min(middle, end)):
                  stdscr.addstr(i, x, random_char(), curses.color_pair(1))
              for i in range(middle, min(head, end)):
                  stdscr.addstr(i, x, random_char(), curses.color_pair(1) | curses.A_BOLD)

      def show_tail():
          for i in range(max(begin, tail - speed), min(tail, end)):
              stdscr.addstr(i, x, ' ', curses.color_pair(0))

      while tail < end:
          tail = head - max_length
          if tail < begin:
              tail = begin
          else:
              show_tail()

          show_body()

          show_head()

          head = head + speed
          r = yield

      if last_char:
          stdscr.addstr(end - 1, x, last_char, curses.color_pair(0))

      return r
  def update_style():
      options['head'] = HEAD_BOLD if options['head'] == HEAD_STANDOUT else HEAD_STANDOUT
  def show_title(stdscr, y, x, title):
      pool = list(range(MAX_COLS))
      rains = []
      count = 0

      for i, s in enumerate(title):
          col = x + i
          if col >= MAX_COLS:
              break
          pool.remove(col)
          if s != ' ':
              rains.append(rain_once(stdscr, col, 0, y, s))
              count = count + 1

      for i in range(len(pool) // 3):
          rains.append(rain_forever(stdscr, pool))

      stdscr.clear()
      should_stop = None
      while True:
          for r in rains:
              try:
                  r.send(should_stop)
              except StopIteration:
                  rains.remove(r)
                  count = count - 1

          if count == 0: 
              should_stop = True

          ch = stdscr.getch()
          if ch != curses.ERR and ch != ord(' '): 
              break 

          if not rains:
              break

          time.sleep(SLEEP_BETWEEN_FRAME)
  def main(stdscr):
      global MAX_COLS
      MAX_COLS = curses.COLS - 1
      stdscr.addstr(curses.LINES // 3, MAX_COLS // 4, options["opening_title"])
      config(stdscr)

      rains = []
      pool = list(range(MAX_COLS))

      start_time = time.time()
      seconds = 5

      while True:
          current_time = time.time()
          elapsed_time = current_time - start_time
          
          if elapsed_time > seconds:
            break 
        
          add_rain(rains, stdscr, pool)

          for r in rains:
              next(r)

          ch = stdscr.getch()
          if ch != curses.ERR and ch != ord(' '): 
              if ch == ord('h'):
                  update_style()
              else:
                  show_title(stdscr, curses.LINES // 2, MAX_COLS // 3, options["end_title"])
                  break 

          time.sleep(SLEEP_BETWEEN_FRAME)
  def add_rain(rains, stdscr, pool):
      if (len(rains) < options['count']) and (len(pool) > 0):
          rains.append(rain_forever(stdscr, pool))

  def matrixrain():
    curses.wrapper(main)

except KeyboardInterrupt:
  pass


#==============================================
# A Divinemonk creation!
#==============================================