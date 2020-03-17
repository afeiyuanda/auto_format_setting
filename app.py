#encoding:utf8
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash
import os, shutil, glob
#import os, exceptions, shutil, glob


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, UPLOAD_FOLDER)
app.config['DOWNLOAD_FOLDER'] = os.path.join(app.root_path, DOWNLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # limit upload file size 8Mb
ALLOWED_EXTENSIONS = set(['txt', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getAllFile(dir):
    dirset = []
    fileset = []
    for filename in os.listdir(dir):
        filename = filename.decode('gbk', 'ignore')
        filepath = os.path.join(dir, filename)
        if os.path.isdir(filepath):
            filepath = os.path.basename(filepath)
            dirset.append(filepath)
        else:
            filepath = os.path.basename(filepath)
            fileset.append(filepath)

    return fileset


def process_file(filename):
    try:
        shutil.copyfile(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename), os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'], filename))
        return 0  # success
    except:
        return 1  # fail


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def api_upload():
    error = None
    file_dir = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    allfileset = getAllFile(file_dir)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file attached in request'
            render_template('index.html', error=error, allfileset=allfileset)
            # return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            error = 'No file selected'
            render_template('index.html', error=error, allfileset=allfileset)
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename.replace(' ', '_')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_flag = 1
            while process_flag:
                process_flag = process_file(filename)
            flash('Upload and Process Successfully!')
            allfileset = getAllFile(file_dir)

            return redirect(url_for('api_upload', error=error, allfileset=allfileset))
            # return redirect(url_for('download_file', filename=filename))
        else:
            error = 'File format forbidon, only xls, xlsx allow!'
            return render_template('index.html', error=error, allfileset=allfileset)
    return render_template('index.html', error=error, allfileset=allfileset)


@app.route('/remove/<filename>', methods=['GET', 'POST'], strict_slashes=False)
def deleteFile(filename):
    # filename = filename.decode('gbk', 'ignore')
    file = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'], filename)
    os.remove(file)
    allfileset = getAllFile(os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER']))
    error = None
    return redirect(url_for('api_upload', error=error, allfileset=allfileset))


@app.route('/download/<string:filename>', methods=['GET', 'POST'], strict_slashes=False)
def download_file(filename):
    error = None
    file_dir = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    allfileset = getAllFile(file_dir)
    file = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file):
        return send_from_directory(os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER']), filename, as_attachment=True)
    else:
        error = 'Download file not exists!'
        return redirect(url_for('api_upload', error=error, allfileset=allfileset))
    # raise exceptions.MyHttpNotFound('not found file')


if __name__ == '__main__':
    app.run(port=9900)


    # 参考：https://blog.csdn.net/baidu_36831253/article/details/78180093
    # https://viveksb007.github.io/2018/04/uploading-processing-downloading-files-in-flask
    # set FLASK_APP=app.py
    # set FLASK_ENV=development
    # python -m flask run -p 9990