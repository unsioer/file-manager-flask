# TODO:
# - Strictly security test (eg: Known risk of deletion)
# - Normalize api

from flask import Flask, request, render_template
from flask_cors import *
import os
import re
import json
import shutil

from util import *

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#app.url_map.converters['regex'] = RegexConverter


# Back-end
@app.route("/api/folder/basic/<path:folderPath>", methods=['GET'])
@cross_origin()
def get(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    fileList = listFile(joinPath)
    return json.dumps({"files": fileList},
                      default=lambda obj: obj.__dict__,
                      indent=4)


@app.route("/api/folder/basic/", methods=['GET'])
@cross_origin()
def getRoot():
    return get('')


@app.route('/api/file/check/<path:filePath>', methods=['GET'])
@cross_origin()
def checkFileExist(filePath):
    joinPath = os.path.join(ROOT_DIR, filePath)
    if os.path.exists(joinPath):
        return json.dumps({"status": 200})
    else:
        return json.dumps({"status": 404})


@app.route("/api/folder/basic/<path:folderPath>", methods=['POST'])
@cross_origin()
def upload(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    # TODO: os.path.exists
    file = request.files['file']
    fullPath = os.path.join(joinPath, file.filename)
    if os.path.exists(fullPath):
        fullPath = nameConflict(fullPath)
    file.save(fullPath)
    return json.dumps({"status": 200})


@app.route("/api/folder/basic/", methods=['POST'])
@cross_origin()
def uploadRoot():
    return upload('')


@app.route("/api/folder/basic/<path:folderPath>", methods=['PUT'])
@cross_origin()
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


@app.route("/api/folder/basic/", methods=['PUT'])
@cross_origin()
def renameRoot():
    return rename('')


@app.route("/api/folder/basic/<path:folderPath>", methods=['DELETE'])
@cross_origin()
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


@app.route("/api/folder/basic/", methods=['DELETE'])
@cross_origin()
def deleteRoot():
    return delete('')


@app.route("/api/folder/new/<path:folderPath>", methods=['POST'])
@cross_origin()
def mkdir(folderPath):
    joinPath = os.path.join(ROOT_DIR, folderPath)
    data = json.loads(request.get_data())
    if data == None:
        return json.dumps({"status": 400, "msg": "No data given"})
    print(data)
    dst = data.get('dst')
    if dst == None:
        return json.dumps({"status": 400, "msg": "No folder name given"})
    if re.search('[\\\/:\?<>\.\*]', dst):
        return json.dumps({"status": 403, "msg": "Illegal folder name"})
    fullPath = os.path.join(joinPath, dst)
    if not os.path.exists(fullPath):
        os.makedirs(fullPath)
        return json.dumps({"status": 200})
    else:
        return json.dumps({"status": 400, "msg": "Destination folder exists"})


@app.route("/api/folder/new/", methods=['POST'])
@cross_origin()
def mkdirRoot():
    return mkdir('')


@app.route("/api/file/copy/<path:filePath>", methods=['PUT'])
@cross_origin()
def copy(filePath):
    fullPath = os.path.join(ROOT_DIR, filePath).replace('\\', '/')
    if not os.path.exists(fullPath):
        return json.dumps({"status": 404, "msg": "File not found"})
    data = json.loads(request.get_data())
    if data == None:
        return json.dumps({"status": 400, "msg": "No data given"})
    dst = data.get('dst')
    if dst == None:
        return json.dumps({
            "status": 400,
            "msg": "No destination folder given"
        })
    if dst[0] == '/':
        dst = dst[1:]
    if re.search('[:\?<>\.\*]', dst):
        return json.dumps({"status": 403, "msg": "Illegal folder name"})
    dstPath = os.path.join(ROOT_DIR, dst,
                           os.path.split(filePath)[-1]).replace('\\', '/')
    print(fullPath, dstPath)
    dstPath = nameConflict(dstPath)
    print(fullPath, dstPath)
    try:
        if not os.path.exists(os.path.join(ROOT_DIR, dst)):
            os.makedirs(os.path.join(ROOT_DIR, dst))
        if os.path.isdir(fullPath): shutil.copytree(fullPath, dstPath)
        else: shutil.copy2(fullPath, dstPath)
        return json.dumps({"status": 200})
    except Exception as e:
        return json.dumps({"status": 400, "msg": str(e)})


@app.route("/api/file/move/<path:filePath>", methods=['PUT'])
@cross_origin()
def move(filePath):
    fullPath = os.path.join(ROOT_DIR, filePath).replace('\\', '/')
    if not os.path.exists(fullPath):
        return json.dumps({"status": 404, "msg": "File not found"})
    data = json.loads(request.get_data())
    if data == None:
        return json.dumps({"status": 400, "msg": "No data given"})
    dst = data.get('dst')
    if dst == None:
        return json.dumps({
            "status": 400,
            "msg": "No destination folder given"
        })
    if dst[0] == '/':
        dst = dst[1:]
    if re.search('[:\?<>\.\*]', dst):
        return json.dumps({"status": 403, "msg": "Illegal folder name"})
    dstPath = os.path.join(ROOT_DIR, dst,
                           os.path.split(filePath)[-1]).replace('\\', '/')
    print(fullPath, dstPath)
    if fullPath == dstPath:
        return json.dumps({"status": 200})
    dstPath = nameConflict(dstPath)
    print(fullPath, dstPath)
    try:
        if not os.path.exists(os.path.join(ROOT_DIR, dst)):
            os.makedirs(os.path.join(ROOT_DIR, dst))
        shutil.move(fullPath, dstPath)
        return json.dumps({"status": 200})
    except Exception as e:
        return json.dumps({"status": 400, "msg": str(e)})


# Front-end
@app.route("/app/<path:folderPath>", methods=['GET'])
def index(folderPath):
    return render_template('app.html')


@app.route("/app/", methods=['GET'])
def indexRoot():
    return index('')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
