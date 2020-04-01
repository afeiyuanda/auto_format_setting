建库自动化排版
===

### 功能说明
提供给生产使用，进行自动化排版

### 依赖

python3

flask

### 使用方法：
已经添加了默认的python路径，所以无需指明python即可正常执行

script/lib_sort_pre.py <input> <outdir>

示例：

script/lib_sort_pre.py  uploads/终文库排版模型整合.xlsx temp


### FLASK项目启动方法：
linux下：export FLASK_APP=app.py

windows下：set FLASK_APP=app.py

python app.py

然后就可以访问 http://10.10.123.47:5000 使用了，注意URL中的IP是启动该服务器的电脑的IP