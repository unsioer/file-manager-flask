# TODO:
# - Move file or folder
# - Strictly security test (eg: Known risk of deletion)
# - rename Folder bug
# - Normalize api
# - Front-end UI design

from flask import Flask, request, render_template
import os
import json

from util import *

app = Flask(__name__)

#app.url_map.converters['regex'] = RegexConverter


# Back-end
@app.route("/api/folder/<path:folderPath>", methods=['GET'])
def get(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    fileList = listFile(joinPath)
    return json.dumps({"files": fileList},
                      default=lambda obj: obj.__dict__,
                      indent=4)


@app.route("/api/folder/", methods=['GET'])
def getRoot():
    return get('')


@app.route('/api/file/check/<path:filePath>', methods=['GET'])
def checkFileExist(filePath):
    joinPath = os.path.join(ROOT_DIR, filePath)
    if os.path.exists(joinPath):
        return json.dumps({"status": 200})
    else:
        return json.dumps({"status": 404})


@app.route("/api/folder/<path:folderPath>", methods=['POST'])
def upload(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    # TODO: os.path.exists
    file = request.files['file']
    file.filename
    file.save(os.path.join(joinPath, file.filename))
    return json.dumps({"status": 200})


@app.route("/api/folder/", methods=['POST'])
def uploadRoot():
    return upload('')


@app.route("/api/folder/<path:folderPath>", methods=['PUT'])
def rename(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    data = json.loads(request.get_data())
    if data == None:
        return json.dumps({"status": 400, "msg": "No data given"})
    src = data.get('src')
    dst = data.get('dst')
    if src == None or dst == None:
        return json.dumps({
            "status": 400,
            "msg": "No source file or destination file given"
        })
    srcPath = os.path.join(joinPath, src)
    dstPath = os.path.join(joinPath, dst)
    if not os.path.exists(srcPath):
        return json.dumps({"status": 404, "msg": "Source file does not exist"})
    if srcPath == dstPath:
        return json.dumps({"status": 200})
    if os.path.exists(dstPath):
        return json.dumps({"status": 400, "msg": "Destination file exists"})
    print(srcPath, dstPath)
    # TODO: test
    os.rename(srcPath, dstPath)
    return json.dumps({"status": 200})


@app.route("/api/folder/", methods=['PUT'])
def renameRoot():
    return rename('')


@app.route("/api/folder/<path:folderPath>", methods=['DELETE'])
def delete(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    data = json.loads(request.get_data())
    if data == None:
        return json.dumps({"status": 400, "msg": "No data given"})
    src = data.get('src')
    if src == None:
        return json.dumps({"status": 400, "msg": "No source file given"})
    srcPath = os.path.join(joinPath, src)
    if not os.path.exists(srcPath):
        return json.dumps({"status": 404, "msg": "Source file does not exist"})
    # TODO: test
    try:
        if os.path.isdir(srcPath): shutil.rmtree(srcPath)
        else: os.remove(srcPath)
        return json.dumps({"status": 200})
    except PermissionError:
        return json.dumps({"status": 400, "msg": "Permission refused"})


@app.route("/api/folder/", methods=['DELETE'])
def deleteRoot():
    return delete('')


# Front-end
@app.route("/app/<path:folderPath>", methods=['GET'])
def index(folderPath):
    return render_template('app.html')


@app.route("/app/", methods=['GET'])
def indexRoot():
    return index('')


if __name__ == "__main__":
    app.run(debug=True)