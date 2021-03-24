from flask import Flask, request, render_template

app = Flask(__name__)

remote_config = {'host_link':'http://127.0.0.1:5000'}


@app.route("/app/<path:folderPath>", methods=['GET'])
def index(folderPath):
    return render_template('app.html', **remote_config)


@app.route("/app/", methods=['GET'])
def indexRoot():
    return index('')


if __name__ == "__main__":

    app.run(debug=True, host='0.0.0.0', port='10000')