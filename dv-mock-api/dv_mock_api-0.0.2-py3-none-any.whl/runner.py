import threading
from dv_mock_api.main import app as flask_app


def flask_app_thread():
    flask_app.run(port="5050", debug=True, use_reloader=False)


app = threading.Thread(name='Flask thread', target=flask_app_thread)
app.setDaemon(True)


def create_app():
    if not app.is_alive():
        app.start()
