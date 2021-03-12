# TODO:
# - Move file or folder
# - Strictly security test (eg: Known risk of deletion)
# - Normalize api
# - Front-end UI design

from flask import Flask, request, render_template
import os
import json

from util import *

app = Flask(__name__)

#app.url_map.converters['regex'] = RegexConverter


# Back-end
@app.route("/api/<path:folderPath>", methods=['GET'])
def get(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    fileList = listFile(joinPath)
    return json.dumps({"files": fileList},
                      default=lambda obj: obj.__dict__,
                      indent=4)


@app.route("/api/", methods=['GET'])
def getRoot():
    return get('')


@app.route("/api/<path:folderPath>", methods=['POST'])
def upload(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    # TODO: os.path.exists
    file = request.files['file']
    file.save(os.path.join(joinPath, file.filename))
    return json.dumps({"status": 200})


@app.route("/api/", methods=['POST'])
def uploadRoot():
    return upload('')


@app.route("/api/<path:folderPath>", methods=['PUT'])
def rename(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    data = request.json
    print(data)
    src = data.get('src')
    dst = data.get('dst')
    if src == None or dst == None:
        return json.dumps({"status": 400})
    srcPath=os.path.join(joinPath, src)
    dstPath=os.path.join(joinPath, dst)
    if not os.path.exists(srcPath):
        return json.dumps({"status": 404, "msg":"Source File does not exist"})
    if srcPath == dstPath:
        return json.dumps({"status": 200})
    if os.path.exists(dstPath):
        return json.dumps({"status": 400, "msg":"Target File exists"})
    print(srcPath, dstPath)
    # TODO: test
    os.rename(srcPath, dstPath)
    return json.dumps({"status": 200})

@app.route("/api/", methods=['PUT'])
def renameRoot():
    return rename('')


@app.route("/api/<path:folderPath>", methods=['DELETE'])
def delete(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    data = request.json
    print(data)
    src = data.get('src')
    if src == None:
        return json.dumps({"status": 400})
    srcPath=os.path.join(joinPath, src)
    if not os.path.exists(srcPath):
        return json.dumps({"status": 404, "msg":"Source File does not exist"})
    # TODO: test
    try:
        os.remove(srcPath)
        return json.dumps({"status": 200})
    except PermissionError:
        try:
            os.rmdir(srcPath)
            return json.dumps({"status": 200})
        except PermissionError:
            return json.dumps({"status": 400, "msg":"Permission Refused"})

@app.route("/api/", methods=['DELETE'])
def deleteRoot():
    return delete('')

# Front-end
@app.route("/app/<path:folderPath>", methods=['GET'])
def index(folderPath):
    jsonstr = json.loads(get(folderPath))
    print(jsonstr)
    return render_template('app.html', **jsonstr)


@app.route("/app/", methods=['GET'])
def indexRoot():
    return index('')


if __name__ == "__main__":
    app.run(debug=True)