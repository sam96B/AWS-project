from distutils.command.build import build
from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.utils import secure_filename
from time import perf_counter
from datetime import datetime
import os


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photo_gallery'
app.secret_key = "my-secret-key"



mysql = MySQL(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['POST', 'GET'])
@app.route("/add_image/", methods=['POST', 'GET'])
def add_image():
    if request.method == 'POST':
        my_key = request.form['key']
        name = request.files['name']
        if name and allowed_file(name.filename):
            filename = secure_filename(name.filename)
            name.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_size = os.path.getsize(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT image_key FROM image")
            keys = cursor.fetchall()
            key_exist = 'false'
            for key in keys:
                if int(my_key) == int(key[0]):
                    key_exist = 'true'
                    break
            if key_exist == 'false':
                cursor.execute(
                    "INSERT INTO image(image_key, image_name, size) VALUES(%s, %s, %s)", (my_key, name.filename, img_size))
                flash('Image is successfully uploaded!')
            else:
                cursor.execute(
                    "SELECT image_name FROM image WHERE image_key=%s", (my_key))
                filename = cursor.fetchone()
                os.unlink(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename[0]))
                cursor.execute(
                    "DELETE FROM image WHERE image_key=%s", (my_key))
                cursor.execute(
                    "INSERT INTO image(image_key, image_name, size) VALUES(%s, %s, %s)", (my_key, name.filename, img_size))
                flash('Image is successfully updated!')
            mysql.connection.commit()
            cursor.close()
        else:
            flash('(png, jpg, jpeg, gif) files only!')
    return render_template("add_image.html")


@app.route("/show_image/", methods=['POST', 'GET'])
def show_image():

    img_src = '/static/temp.jpg'
    if request.method == 'POST':
        key = request.form['key']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT image_name FROM image WHERE image_key = %s", (key))
        file = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()
        if file:
            filename = secure_filename(file[0])
            img_src = '/' + os.path.join(app.config['UPLOAD_FOLDER'], filename)
            flash('Image is successfully retrieved!')
    return render_template("show_image.html", image_src=img_src)


@app.route("/show_keys/", methods=['POST', 'GET'])
def show_keys():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT image_key FROM image ORDER BY image_key ASC")
        keys = cursor.fetchall()
        for key in keys:
            flash(key[0])
        mysql.connection.commit()
        cursor.close()
    return render_template("show_keys.html")


app.run(host='localhost', port=5001, debug=False)
