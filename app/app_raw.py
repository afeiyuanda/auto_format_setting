#encoding:utf8
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, send_from_directory, url_for,redirect
import time
import os, exceptions
import sys

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, UPLOAD_FOLDER)
#alycode = 0
ALLOWED_EXTENSIONS = set(['txt', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getAllFile(dir):
    dirset = []
    fileset = []
    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)
        if os.path.isdir(filepath):
            filepath = os.path.basename(filepath)
            dirset.append(filepath)
        else:
            filepath = os.path.basename(filepath)
            fileset.append(filepath)
    return [fileset, dirset]


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def api_upload():
    # global alycode
    # code = 0
    file_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    allfileset = getAllFile(file_dir)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    try:
        f = request.files["file"]
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = secure_filename(f.filename)
            print fname
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            new_filename = 'upload' + '.' + ext  # 修改了上传的文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            code = 1
            allfileset = getAllFile(file_dir)
        else:
            code = 2
    except:
        code = 2
        print 'upload fail'
    return render_template('index.html', allfileset=allfileset, code=code)
    #return render_template('index.html', allfileset=allfileset, code=code, alycode=alycode)


@app.route('/aly/<filename>', methods=['GET', 'POST'], strict_slashes=False)
def startAly(filename):
    #global alycode
    try:
        os.rename(filename, filename+'_changed')
        alycode = 2
    except:
        alycode = 3
    return redirect("/")


@app.route('/remove/<filename>', methods=['GET', 'POST'], strict_slashes=False)
def deleteFile(filename):
    file = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    os.remove(file)
    return redirect("/")


@app.route('/download/<string:filename>', methods=['GET', 'POST'], strict_slashes=False)
def download_file(filename):
    file = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file):
        return send_from_directory(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), filename, as_attachment=True)
    raise exceptions.MyHttpNotFound('not found file')


if __name__ == '__main__':
    app.run(debug=True, port=9990)


    # 参考：https://blog.csdn.net/baidu_36831253/article/details/78180093