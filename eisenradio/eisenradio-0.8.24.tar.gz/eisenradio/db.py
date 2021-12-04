import base64
import os
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


static_images = os.path.dirname(os.path.abspath(__file__)) + "/static/images/styles/"
save_parent_folder = "C:/Users/rene_/PycharmProjects/package_eisenradio/eisenradio/radiostations"


def convert_ascii(file_name):
    with open(file_name, "rb") as reader:
        img_bytes = reader.read()
        img_ascii = render_picture(img_bytes, 'encode')
    return img_ascii


def render_picture(byte_data, de_enc):
    render_pic = ''
    if de_enc == 'encode':
        render_pic = base64.b64encode(byte_data).decode('ascii')
    if de_enc == 'decode':
        render_pic = base64.b64decode(byte_data).decode('ascii')
    return render_pic


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# # # # custom filled db # # #
connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
            ('time_machine',
             'http://98.211.68.9:8765/listen',
             save_parent_folder,
             "image/jpeg",
             convert_ascii(static_images + "Radio48blue.png"))
            )

# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('goa_psi',
#              'http://amoris.sknt.ru:8004/stream',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "2.jpg"))
#             )
#
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('anime_jp',
#              'http://streamingv2.shoutcast.com/japanimradio-tokyo',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "3.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('NDR2',
#              'http://www.ndr.de/resources/metadaten/audio/m3u/ndr2.m3u',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "4.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('korean_pop',
#              'http://167.114.64.181:8818/stream',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "5.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('Samba_Brazil',
#              'http://185.33.21.111:80/samba_128',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "6.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('classic_1fm',
#              'http://185.33.21.113:80/classical_mobile_aac',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "7.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('classic_ro',
#              'http://37.251.146.169:8000/streamHD',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "8.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('Progress',
#              'http://stream.psychedelik.com:8010/sid=1',
#              save_parent_folder,
#              "image/jpeg",
#              convert_ascii(static_images + "9.jpg"))
#             )
#
# cur.execute("INSERT INTO posts (title, content, download_path, pic_content_type, pic_data) VALUES (?, ?, ?, ?, ?)",
#             ('pop24',
#              'http://rosewellpop.radioca.st:80/streams/128kbps',
#              save_parent_folder,
#              "image/png",
#              convert_ascii(static_images + "10.png"))
#             )
#
# cur.execute("INSERT INTO eisen_intern (browser_open) VALUES (?)", str(0))
# connection.commit()
# connection.close()
