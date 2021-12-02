
# export / set FLASK_ENV = development   # ## make prod.
# export / set FLASK_APP = app
#           flask init-db
# run -p 5002
# make prod. server
# ############################################ flask ############################

import base64
import os
import sys
import subprocess
import platform
import sqlite3
import threading
import webbrowser
from time import sleep

from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from flask_cors import CORS
from werkzeug.exceptions import abort

try:
    import lib.eisen_radio as eR
except ImportError:
    import eisenradio.lib.eisen_radio as eR
import shutil

app = Flask(__name__)
# CORS(app, resources={r"*": {"origins": "*"}})
CORS(app)
app.config['SECRET_KEY'] = '32787586655322142587808ß974121342425235252353256467548121498ß09353'

dir = os.path.dirname(__file__)
app_db_path = os.path.join(dir, 'app_writeable','db','database.db')
snap_db_path = ''

first_run_index = True
listen_btn = False
status_listen_btn_dict = {}  # {table id 15: 1 } on
status_record_btn_dict = {}
# radio_pic_dict = {}

last_btn_id = None  # current button pressed, or btn predecessor / to redraw, if next is pressed / first is null->err
listen_last_url = None
combo_master_timer = 0
progress_master_percent = 0


@app.route('/', methods=('GET', 'POST'))
def index():
    global first_run_index
    global combo_master_timer
    global listen_last_url
    global current_station

    current_station = ''

    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()

    EisenApp.display_clean_titles()

    if first_run_index:
        first_run_index = False
        check_write_protected()
        eR.GBase.pool.submit(EisenApp.progress_timer)

        for row in posts:
            # init btn not pressed
            status_listen_btn_dict[row['id']] = 0
            status_record_btn_dict[row['id']] = 0

    if request.method == 'POST':
        # print_request_values(request.form.values())
        post_request = request.form.to_dict()  # flat dict werkzeug doc

        json_post = index_posts_clicked(post_request)
        return json_post

    for key_table_id, val in status_listen_btn_dict.items():
        if val:
            current_station = status_read_status_set(False, 'posts', 'title', key_table_id)

    return render_template('index.html',
                           posts=posts,
                           combo_master_timer=combo_master_timer,
                           status_listen_btn_dict=status_listen_btn_dict,
                           status_record_btn_dict=status_record_btn_dict,
                           current_station=current_station,
                           listen_last_url=listen_last_url)


@app.route('/index_posts_combo', methods=['POST'])
def index_posts_combo():
    global combo_master_timer
    combo_master_timer = request.form['time_record_select_all']
    return combo_master_timer  # return something to flask from route


@app.route('/index_posts_percent', methods=['POST'])
def index_posts_percent():
    global progress_master_percent
    return jsonify({'result': progress_master_percent})


def index_posts_clicked(post_request):

    # invoke m3u check function, this version does not have a relay server
    global listen_btn
    global last_btn_id
    global listen_last_url

    pay_load = post_request['data']
    button_list = pay_load.split('_')
    table_id = button_list[1]
    button = button_list[0]

    if button == 'Listen':  # turn values, update button status dict

        if status_listen_btn_dict[int(table_id)]:   # button was down
            status_listen_btn_dict[int(table_id)] = 0
            EisenApp.dispatch_master(int(table_id), 'Listen', 0)
            if not last_btn_id == table_id:
                return jsonify({'result': 'auto_click was here. no result needed. nada'})
        else:
            status_listen_btn_dict[int(table_id)] = 1   # button just pressed, register state, new station

            if not last_btn_id == table_id:  # other btn pressed
                if listen_btn:  # was playing before actual btn
                    switch_btn = last_btn_id  # press abandoned btn, play new url
                    last_btn_id = table_id
                    listen_last_url = query_radio_url(table_id)  # radio url
                    EisenApp.dispatch_master(int(table_id), 'Listen', 1)
                    current_station = status_read_status_set(False, 'posts', 'title', table_id)
                    # trigger auto_click
                    return jsonify(
                        {'former_button_to_switch': switch_btn,
                         'query_url': listen_last_url,
                         'if not last_btn_id == table_id': '------ last_btn_id --------',
                         'result': 'activate_audio', 'table_ident': current_station})

            EisenApp.dispatch_master(int(table_id), 'Listen', 1)

        listen_last_url = query_radio_url(table_id)  # radio url
        last_btn_id = table_id

        listen_btn = False
        for val in status_listen_btn_dict:
            if status_listen_btn_dict[val]:
                listen_btn = True
                break

        # print(status_listen_btn_dict)
        if listen_btn:
            current_station = status_read_status_set(False, 'posts', 'title', table_id)
            return jsonify(
                {'former_button_to_switch': False, 'buttons': button, 'query_url': listen_last_url,
                 'result': 'activate_audio', 'table_ident': current_station})
        else:
            return jsonify(
                {'former_button_to_switch': False, 'buttons': button, 'query_url': listen_last_url,
                 'result': 'deactivate_audio'})

    if button == 'Record':
        if status_record_btn_dict[int(table_id)]:
            status_record_btn_dict[int(table_id)] = 0
            EisenApp.dispatch_master(int(table_id), 'Record', 0)
        else:
            status_record_btn_dict[int(table_id)] = 1
            EisenApp.dispatch_master(int(table_id), 'Record', 1)

    # print(f' ---- index_posts_type_ajax {button + "_" + table_id}"')
    return jsonify({'buttons': button})


def query_radio_url(table_id):

    str_url = status_read_status_set(
        False, 'posts', 'content', table_id)
    return str_url


@app.route('/about', methods=('GET', 'POST'))
def about():

    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    try:
        print(f' Record (all) to folder: {posts[0]["download_path"]}')
        download_path=posts[0]["download_path"]
    finally:
        conn.close()
		
    if request.method == 'POST':
        if request.form['browser']:
            status_read_status_set(True, 'eisen_intern', 'browser_open', '1')
            return redirect(url_for('about'))

    is_browser_on = status_read_status_set(False, 'eisen_intern', 'browser_open', '1')
    return render_template('about.html',
                           is_browser_on=is_browser_on,
						   download_path=download_path)


def render_picture(byte_data, de_enc):

    render_pic = ''
    if de_enc == 'encode':
        render_pic = base64.b64encode(byte_data).decode('ascii')
    if de_enc == 'decode':
        render_pic = base64.b64decode(byte_data).decode('ascii')
    return render_pic


@app.route('/display_info', methods=('GET', 'POST'))
def display_info():

    if request.method == "GET":
        values = request.form.values()
        print_request_values(values)

        json_str = ''
        for val in EisenApp.active_displays:
            json_str = json_str + str(val) + '=' + str(EisenApp.active_displays[val]) + ','
        # print(json_str)
        return jsonify({"result": json_str})

    return render_template('display_info.html')


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    url_port = eR.GIni.parse_url_simple_url(post["content"])

    return render_template('post.html',
                           post=post,
                           url_port=url_port,)


@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Name is required!')
        if not content:
            flash('URL is required!')

        # Image
        if request.files['inputFile']:
            file = request.files['inputFile']
            content_type = file.content_type
            print(f' name {file.name} content-type {file.content_type}')
            try:
                db_img = file.read()
                image = render_picture(db_img, 'encode')
            except Exception as e:
                print(e)
                image = None
                content_type = None
                pass
        else:
            image = None
            content_type = None

        if request.form['text']:
            text = request.form['text']
        else:
            text = None

        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM posts').fetchall()
        # if we later make extra save to folders for each radio
        try:
            save_to = posts[0]["download_path"]
        except Exception as e:
            print(e)
            print(' looks like the first radio to create, no save to path set')
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
        else:
            conn.execute('INSERT INTO posts (title, content, download_path, pic_data, pic_content_type, pic_comment) '
                         'VALUES (?, ?, ?, ?, ?, ?)',
                         (title, content, save_to, image, content_type, text))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/page_flash', methods=('GET', 'POST'))
def page_flash():
    global progress_master_percent
    global combo_master_timer

    combo_master_timer = 0  # master timer recording
    progress_master_percent = 0

    flash('Count down timer ended all activities.')
    return render_template('page_flash.html')


@app.route('/save', methods=('GET', 'POST'))
def save():

    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    try:
        print(f' Record (all) to folder: {posts[0]["download_path"]}')
    finally:
        conn.close()

    if request.method == 'POST':
        save_to = request.form['Path']

        if not save_to:
            flash('A folder is required!')
        else:
            test_file = save_to + '/save_to'
            try:
                with open(test_file, 'wb') as record_file:
                    record_file.write(b'\x03')
                os.remove(test_file)
            except Exception as e:
                print(e)
                flash('folder is write protected!')
            else:
                conn = get_db_connection()
                records = conn.execute('select id from posts').fetchall()
                for id_num in records:
                    # print("Radio Id:", id_num[0])
                    conn.execute('UPDATE posts SET download_path = ? WHERE id = ?', (save_to, id_num[0]))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

    return render_template('save.html', save_to=posts[0]['download_path'])


def check_write_protected():

    conn = get_db_connection()
    path = conn.execute('SELECT download_path FROM posts WHERE id = ? ;', [str(1)]).fetchone()
    try:
        print(f' Record (all) to folder: {path[0]}')
    finally:
        conn.close()

    write_file = str(path[0]) + '/eisen_write_test'
    try:
        with open(write_file, 'wb') as record_file:
            record_file.write(b'\x03')
        os.remove(write_file)
    except Exception as e:
        print(e)
        flash('Can not write to folder! ' + str(path[0]))


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    no_image = False
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        # Image, if empty keep db entry as it is
        if request.files['inputFile']:
            file = request.files['inputFile']
            content_type = file.content_type
            print(f' name {file.name} content-type {file.content_type}')
            try:
                db_img = file.read()
                image = render_picture(db_img, 'encode')
            except Exception as e:
                print(e)
                image = None
                content_type = None
                no_image = True
                pass
        else:
            image = None
            content_type = None
            no_image = True

        if request.form['text']:
            text = request.form['text']
            if text == 'None':
                text = ' '
        else:
            text = ' '

        conn = get_db_connection()
        if image:
            conn.execute('UPDATE posts SET title = ?, content = ?, pic_data = ?, pic_content_type = ?, '
                         'pic_comment = ? WHERE id = ?',
                         (title, content, image, content_type, text, id))
        else:
            conn.execute('UPDATE posts SET title = ?, content = ?, pic_comment = ?  WHERE id = ?',
                         (title, content, text, id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    get_db_smaller()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


def print_request_values(values):
    for val in values:
        print(' -- start print --')
        print(f'\tval in request.form.values(): {val}')
        print(f'\trequest.data {request.data}')
        print(f'\trequest.form {request.form}')
        print(f'\trequest.values {request.values}')
        print(f'\trequest.form.to_dict() {request.form.to_dict()}')
        print(' -- end print --')


def get_db_smaller():
    conn = sqlite3.connect(app_db_path, isolation_level=None)
    conn.execute("VACUUM")
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(app_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)  # flask.abort(404)
    return post


def status_read_status_set(set_status, table, column, table_id):
    # sqlite does not allow dynamic table or column assignment, user handbook
    col_value = ''
    conn = get_db_connection()

    if table == 'posts':

        if column == 'content':
            col_value = conn.execute('SELECT content FROM posts WHERE id = ? ;', [str(table_id)]).fetchone()
        if column == 'title':
            col_value = conn.execute('SELECT title FROM posts WHERE id = ? ;', [str(table_id)]).fetchone()
        if column == 'download_path':
            col_value = conn.execute('SELECT download_path FROM posts WHERE id = ? ;', [str(table_id)]).fetchone()
        conn.close()

    if table == 'eisen_intern':

        if column == 'browser_open':
            col_value = conn.execute(
                'SELECT browser_open FROM eisen_intern WHERE id = ?;', [str(table_id)]).fetchone()

            if set_status:
                if col_value[0]:  # twist values
                    conn.execute('UPDATE eisen_intern SET browser_open = ? WHERE id = ?;', [str(0), str(table_id)])
                else:
                    conn.execute('UPDATE eisen_intern SET browser_open = ? WHERE id = ?;', [str(1), str(table_id)])

        conn.commit()
        conn.close()
    return col_value[0]


class EisenApp:

    active_displays = {}
    eisen_threads = []

    @staticmethod
    def set_radio_path(table_id):
        radio_path = status_read_status_set(
            False, 'posts', 'download_path', table_id)
        eR.GBase.radio_base_dir = radio_path

    @staticmethod
    def dispatch_master(table_id, button, status):
        EisenApp.set_radio_path(table_id)
        str_radio = status_read_status_set(
            False, 'posts', 'title', table_id)

        if button == 'Listen':
            # print('Listen')
            EisenApp.dispatch_listen_btn(str_radio, table_id, status)

        elif button == 'Record':
            # print('RECORD')
            EisenApp.dispatch_record_btn(str_radio, table_id, status)

    @staticmethod
    def dispatch_listen_btn(str_radio, table_id, listen_status):

        if listen_status:
            eR.GRecorder.listen_active_dict[str_radio] = True  # later needed for relay

            if not status_record_btn_dict[table_id]:  # recorder not started / index_posts_ajax()
                eR.GRecorder.record_active_dict[str_radio] = False  # pass record write, else key error
                EisenApp.dispatch_record_title(table_id, False, True)  # start title grabber

        else:
            eR.GRecorder.listen_active_dict[str_radio] = False
            if not status_record_btn_dict[table_id]:
                EisenApp.dispatch_recorder_stop(table_id)

    @staticmethod
    def dispatch_record_btn(str_radio, table_id, record_status):

        if record_status:
            eR.GRecorder.record_active_dict[str_radio] = True

            if not status_listen_btn_dict[table_id]:  # listen not started / index_posts_ajax()
                eR.GRecorder.listen_active_dict[str_radio] = False
            EisenApp.dispatch_record_title(table_id, True, False)

        else:
            eR.GRecorder.record_active_dict[str_radio] = False
            EisenApp.dispatch_recorder_stop(table_id)

    @staticmethod
    def dispatch_recorder_stop(table_id):

        str_radio = status_read_status_set(
            False, 'posts', 'title', table_id)
        # stop recorder threads
        eR.GBase.dict_exit[str_radio] = True
        try:
            del EisenApp.active_displays[table_id]
            sleep(2)
            if status_listen_btn_dict[table_id]:
                EisenApp.dispatch_record_title(table_id, False, True)
        except KeyError:
            pass

    @staticmethod
    def dispatch_record_title(table_id, record, title):

        str_radio = status_read_status_set(
            False, 'posts', 'title', table_id)
        str_url = status_read_status_set(
            False, 'posts', 'content', table_id)

        eR.GBase.dict_exit[str_radio] = False
        # test for alive, container docker or snap, and playlist / data_base_auto
        str_checked_url_m3u = eR.check_alive_playlist_container(str_radio, str_url)
        if str_checked_url_m3u:
            # replace m3u with real url in database
            conn = get_db_connection()
            print('UPDATE posts SET content = ? WHERE id = ?', (str(str_checked_url_m3u), str(table_id)))
            conn.execute('UPDATE posts SET content = ? WHERE id = ?', (str(str_checked_url_m3u), str(table_id)))
            conn.commit()
            conn.close()
            str_url = str_checked_url_m3u
        # start threads
        try:
            print(eR.GBase.dict_error[str_radio])  # show connection error in display
        except KeyError:
            # no error, no key exists

            if title:
                thread = threading.Thread(target=eR.GRecorder.get_metadata_from_stream_loop, args=(str_url, str_radio), daemon=True)
                # thread.setDaemon(True)  # non block
                EisenApp.eisen_threads.append(thread)
                thread.start()

            elif record:
                # eR.record(str_radio, str_url)

                thread = threading.Thread(name=table_id, target=eR.record, args=(str_radio, str_url), daemon=True)
                #thread.setDaemon(True)
                EisenApp.eisen_threads.append(thread)
                thread.start()

            thread = threading.Thread(target=EisenApp.display_write_db, args=(str_radio, table_id), daemon=True)
            # thread.setDaemon(True)  # non block
            EisenApp.eisen_threads.append(thread)
            thread.start()
            return True
        else:
            # show error on display
            EisenApp.active_displays[table_id] = eR.GBase.dict_error[str_radio]
            eR.GBase.dict_exit[str_radio] = True
            return False

    @staticmethod
    def display_write_dict():

        conn = get_db_connection()
        try:
            titles = conn.execute('SELECT id, display FROM posts').fetchall()
            for row in titles:
                table_id = row[0]
                title = row[1]
                if title is not None:
                    EisenApp.active_displays[table_id] = title
        except KeyError:
            pass
        conn.close()

    @staticmethod
    def display_write_db(radio, table_id):  # write title in db
        title = ''
        while not eR.GBase.dict_exit[radio]:

            try:
                title = eR.GRecorder.current_song_dict[radio]
            except Exception as ex:
                print(ex)
                pass

            try:
                EisenApp.display_update_table(title, table_id)
            except Exception as e:
                print(e)
                pass

            for sec in range(5):
                sleep(1)
                if eR.GBase.dict_exit[radio]:
                    title = 'Null'
                    EisenApp.display_update_table(title, table_id)
                    print(f' exit display_write_db {radio}')
                    break

    @staticmethod
    def display_update_table(title, table_id):

        conn = get_db_connection()
        try:
            conn.execute('UPDATE posts SET display = ? WHERE id = ? ;', [str(title), str(table_id)])
        except Exception as e:
            print(f' utf char prob. check lang. support display_update_table(): {e}')
        else:
            conn.commit()
            conn.close()
            EisenApp.display_write_dict()

    @staticmethod
    def display_clean_titles():
        conn = get_db_connection()
        records = conn.execute('select id from posts').fetchall()
        for id_num in records:
            # print(f"Radio Id: {id_num[0]}")
            conn.execute('UPDATE posts SET display = ? WHERE id = ?', [None, id_num[0]])
        conn.commit()
        conn.close()

    @staticmethod
    def progress_timer():

        global combo_master_timer
        global progress_master_percent

        current_timer = 0
        while 1:

            if combo_master_timer:
                combo_time = (int(combo_master_timer) * 60 * 60)  # 3600
                percent = EisenApp.progress_bar_percent(current_timer, combo_time)
                if percent:
                    progress_master_percent = percent
                else:
                    progress_master_percent = 0
                    current_timer = 0

                if percent >= 100:
                    found = 0
                    for _ in eR.GBase.dict_exit:
                        found += 1
                    if found:
                        for recorder in eR.GBase.dict_exit:
                            eR.GBase.dict_exit[recorder] = True

            if not combo_master_timer:
                current_timer = 0
                progress_master_percent = 0

            current_timer += 1
            sleep(1)

    @staticmethod
    def progress_bar_percent(current_timer, max_value):
        if not max_value:
            return False
        # doing some math, p = (P * 100) / G, percent = (math.percentage value * 100) / base
        cur_percent = round((current_timer * 100) / max_value, 4)  # 0,0001 for 24h reaction to show
        return cur_percent


def get_environment():
    global app_db_path
    global snap_db_path
    try:
        if os.environ["SNAP"]:
            print('Eisen App runs in Ubuntu Snap Container, check environment:')
            print('')
            print('SNAP_USER_COMMON (your Database lives here, backup if you like): ' + os.environ["SNAP_USER_COMMON"])
            print('SNAP_LIBRARY_PATH: ' + os.environ["SNAP_LIBRARY_PATH"])
            print('SNAP_COMMON: ' + os.environ["SNAP_COMMON"])
            print('SNAP_USER_DATA: ' + os.environ["SNAP_USER_DATA"])
            print('SNAP_DATA: ' + os.environ["SNAP_DATA"])
            print('SNAP_REVISION: ' + os.environ["SNAP_REVISION"])
            print('SNAP_NAME: ' + os.environ["SNAP_NAME"])
            print('SNAP_ARCH: ' + os.environ["SNAP_ARCH"])
            print('SNAP_VERSION: ' + os.environ["SNAP_VERSION"])
            print('SNAP: ' + os.environ["SNAP"])
    except KeyError:
        pass

    try:
        if os.environ["SNAP"]:
            snap_db_path = os.environ["SNAP_USER_COMMON"] + '//database.db'
            if not os.path.exists(snap_db_path):
                shutil.copyfile(app_db_path, snap_db_path)
            app_db_path = snap_db_path # change database path
    except KeyError:
        pass


def open_with_default(path):
    current_platform = platform.system()
    if current_platform == "Linux":
        subprocess.call(["xdg-open", path])
    elif current_platform == "Windows":
        os.system("start "+path)
    elif current_platform == "Darwin":
        subprocess.call(["open", path])


def open_browser():
    print('\n\t---> Use url "http://localhost:5050/" to connect your Browser. <---\n')
    is_enabled = status_read_status_set(False, 'eisen_intern', 'browser_open', '1')

    if is_enabled:
        print(f' Browser auto start: Enabled')
        # webbrowser.open('http://localhost:5050', new=2)
        open_with_default('http://localhost:5050')
    else:
        print(f' Browser auto start: Disabled')


def main():
    try:
        if os.environ["DOCKER"]:
            print('\n\tEisenRadio App in Docker Container\n')
            print('\tUse url "http://localhost:5050/" to connect your Browser.\n')
    except KeyError:
        get_environment()
        open_browser()


class Radio:
    dict_stations = {}  # keys are used as variables, value is instance of Radio class

    def __init__(self, name, record, listen, error, error_text, stream_text, listen_history, last_button_id,
                 this_radio_id):
        self.name = name
        self.record = record  # False
        self.listen = listen  # False
        self.error = error  # False
        self.error_text = error_text  # None
        self.stream_text = stream_text  # None
        self.listen_history = listen_history  # not the first button pressed, False
        self.last_button_id = last_button_id  # int table_id, None
        self.this_radio_id = this_radio_id
if __name__ == "__main__":
    main()
    app.run(host='localhost', port='5050', threaded=True, debug=True, use_reloader=False)
