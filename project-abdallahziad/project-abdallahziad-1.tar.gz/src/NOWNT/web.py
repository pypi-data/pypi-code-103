from flask import Flask, render_template, request, redirect
import datetime


def launch_web(host, port, test, database):
    app = Flask(__name__)

    @app.route("/")
    def home():
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')
        return render_template('index.html')

    @app.route("/start", methods=['POST'])
    def start():
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')

        test.hostname = request.form['hostname']
        test.start()
        return redirect('/results')

    @app.route("/results")
    def results():
        all_results = []
        for user in test.users:
            all_results.extend(user.results)
        return render_template('results.html', **{'results': all_results, 'hostname': test.hostname})

    @app.route("/stop")
    def stop():
        try:
            test.stop(database)
        except:
            pass
        return redirect('/')

    @app.route("/previous")
    def previous():
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')
        hostnames = database.get_all_hostnames()
        tests = database.get_all_tests()[::-1]
        tests = [
            (
                t[0],
                t[1],
                t[2],
                datetime.datetime.fromtimestamp(float(t[3])).strftime("%m/%d/%Y, %H:%M:%S"),
                datetime.datetime.fromtimestamp(float(t[4])).strftime("%m/%d/%Y, %H:%M:%S"),
                t[5],
                t[6],
                next((h[0] for h in hostnames if t[7] == h[1]), '-'))
            for t in tests
        ]
        return render_template('previous.html', **{'tests': tests})

    app.run(host=host, port=port, debug=True)
