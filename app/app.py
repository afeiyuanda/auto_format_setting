#encoding:utf8
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash
import os, shutil, subprocess
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
        # filename = filename.decode('gbk', 'ignore')
        filepath = os.path.join(dir, filename)
        if os.path.isdir(filepath):
            filepath = os.path.basename(filepath)
            dirset.append(filepath)
        else:
            filepath = os.path.basename(filepath)
            fileset.append(filepath)

    return fileset


def process_file(filename):
    # python script/lib_sort_pre.py  uploads/终文库排版模型整合.xlsx temp/
    temp_outdir = os.path.join(app.root_path, 'temp')
    if os.path.exists(temp_outdir):
        shutil.rmtree(temp_outdir)
    os.makedirs(temp_outdir)
    p = subprocess.Popen('python script/lib_sort_pre.py %s %s' % (os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename), temp_outdir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.wait()
    if p.returncode:
        return [1, p.stderr.read()]  # 执行程序报错
    else:
        filename_prefix = filename.split('.')[0]
        if os.path.exists(os.path.join(temp_outdir, filename_prefix+'_out_result', filename_prefix+'_sort.xlsx')):
            shutil.copyfile(os.path.join(temp_outdir, filename_prefix+'_out_result', filename_prefix+'_sort.xlsx'), os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'], filename_prefix+'_sort.xlsx'))
        shutil.rmtree(temp_outdir)
        # shutil.copyfile(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename), os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'], filename))
        return [0, p.stdout.read()]


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
            run_num = 0
            while process_flag and run_num < 2:
                process_flag, feedback = process_file(filename)
                run_num += 1
            if process_flag == 0:
                flash('Upload and Process Successfully!', 'info')
                flash(feedback.decode('cp936', 'ignore').strip().replace('\r\n', '<br>'), 'info')
            else:
                flash(u'处理失败，请检查上传文件格式是否正确，或者联系开发人员！', 'error')
                flash(feedback.decode('cp936', 'ignore').strip().replace('\r\n', '<br>'), 'error')
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
    # app.run(host='0.0.0.0', debug=True, port=9900)
    app.run(host='0.0.0.0', port=5000)


    # 参考：https://blog.csdn.net/baidu_36831253/article/details/78180093
    # https://viveksb007.github.io/2018/04/uploading-processing-downloading-files-in-flask
    # set FLASK_APP=app.py
    # set FLASK_ENV=development
    # python -m flask run -p 5000
    # python -m flask run -h 0.0.0.0 -p 9900