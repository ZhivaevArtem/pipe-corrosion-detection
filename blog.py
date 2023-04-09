from ast import Bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from click import open_file
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, current_app
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db

from app import mail
from flask_mail import Message

from Data import *
from Simple_Unet import *

import base64

bp = Blueprint('blog', __name__)

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_data(data, file_name):  # обрабатывает отправку основной картинки
    # try:
    with open(file_name, 'wb') as file:
        file.write(data)
    # except:
    #     with open(file_name, 'w') as file:
    #         file.write(data)

def convert_blob(data, file_name):  # обрабатывает отправку слоёв
    # try:
    #     with open(file_name, 'w') as file: 
    #         file.write(base64.b64decode(split_b64str(data)))
    # except:
    with open(file_name, 'wb') as file: 
        file.write(base64.b64decode(split_b64str(data)))

def attach_imgs(layer_id, img_data, mesg):
    # if (layer_id=='original'):
    #     convert_data(img_data[layer_id], "./static/temp/image.png")
    # else:
    try:
        convert_data(img_data[layer_id], "./static/temp/image.png")
    except:
        convert_blob(img_data[layer_id], "./static/temp/image.png")
    with bp.open_resource("./static/temp/image.png") as fp:
        mesg.attach(layer_id, "image/png", fp.read())
    os.remove('static/temp/image.png')

def split_b64str(b64string):
    result = b64string.split(',')[1]
    return result

def clear_temp():
    try:
        os.remove('static/temp/orig.png')
    except:
        pass
    try:
        os.remove('static/temp/res.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer0.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer1.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer2.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer3.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer4.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer5.png')
    except:
        pass
    try:
        os.remove('static/temp/res_layer6.png')
    except:
        pass
    try:
        os.remove('static/temp/background.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_salinity.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_corrosion.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_pitting.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_oil.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_recess.png')
    except:
        pass
    try:
        os.remove('static/temp/layer_ext_recess.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_salinity.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_corrosion.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_pitting.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_oil.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_recess.png')
    except:
        pass
    try:
        os.remove('static/temp/edit_ext_recess.png')
    except:
        pass
    return

layer_map = {
    'salinity': 'edit_salinity',
    'corrosion': 'edit_corrosion',
    'pitting': 'edit_pitting',
    'oil': 'edit_oil',
    'recess': 'edit_recess',
    'elongated_recess': 'edit_ext_recess'
}

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    clear_temp()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        file = request.files.get('file')
        error = None

        if not title:
            error = 'Title is required.'
        
        if file is None or file.filename == "":
            error = 'File is missing or incorrect'
        if not allowed_file(file.filename):
            error = 'File format is not supported'
        
        #Создать/запустить UNet, записать изображения на диск (см старый проект app.py, save_img), записать их в переменные ИЛИ читать прямо из переменных
        try:
            image_io = ImageIO()
            img_bytes = file.read()
            img = image_io.load(img_bytes)
            h,w = img.shape[2],img.shape[3]
            net = UNet(num_class=7)
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            net.load_state_dict(torch.load('dict.pth', map_location=device))
            net.eval()
            res = net(img)
            percents = image_io.save(res,'static/temp/res')
            file.seek(0)
            file.save('static/temp/orig.png')
        except:
            error = 'Error during prediction'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            with open("static/temp/orig.png", 'rb') as orig, open("static/temp/res_layer0.png", 'rb') as im_clear, open("static/temp/res.png", 'rb') as im_composite, open("static/temp/res_layer1.png", 'rb') as im_salen, open("static/temp/res_layer2.png", 'rb') as im_corros, open("static/temp/res_layer3.png", 'rb') as im_pit, open("static/temp/res_layer4.png", 'rb') as im_oil, open("static/temp/res_layer5.png", 'rb') as im_rec, open("static/temp/res_layer6.png", 'rb') as im_erec:
                db.execute(
                    'INSERT INTO post (title, body, author_id, original_picture, layer_clear, layer_composite, layer_salinity, layer_corrosion, layer_pitting, layer_oil, layer_recess, layer_ext_recess, clear_percentage, salinity_percentage, corrosion_percentage, pitting_percentage, oil_percentage, recess_percentage, ext_recess_percentage)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (title, body, g.user['id'], orig.read(), im_clear.read(), im_composite.read(), im_salen.read(), im_corros.read(), im_pit.read(), im_oil.read(), im_rec.read(), im_erec.read(), percents[0], percents[1], percents[2], percents[3], percents[4], percents[5], percents[6])
                )
            db.commit()
            # Удалить слои с диска (os.remove("path/to/img.png")) ЕСЛИ нужно было сохранять файл
        return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT *'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/show', methods=('GET',))
@login_required
def show(id):
    post = get_post(id)
    return render_template('blog/show.html', post=post)

# @bp.route('/<int:id>/<percent>')
# @login_required
# def percentage(id, percent):
#     post=get_post(id)
#     return post[percent]

@bp.route('/<int:id>/<layer>')
@login_required
def layer(id, layer):
    post=get_post(id)
    bytes_io = BytesIO(post[layer])
    return send_file(bytes_io, mimetype='image/png')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        picture = request.form['canvasimg'] # picture is str object
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            layer = request.form['fdbcktype']
            db.execute(
                # 'UPDATE post SET title = ?, body = ?'
                'UPDATE post SET '+ layer_map[layer] + ' = ?'
                ' WHERE id = ?',
                # (title, body, id)
                (picture, id)
            )
            db.commit()
            with open("static/temp/" + layer_map[layer] + ".png", 'wb') as file:    # Сохраняет пользовательскую картинку на диск
                file.write(base64.b64decode(split_b64str(picture)))
            flash("Layer saved!")
            # return redirect(url_for('blog.index'))
    else:
        #УДАЛЯТЬ СТАРЫЕ КАРТИНКИ ИЗ ПАМЯТИ

        #Заменить на массив
        picture = post['original_picture']
        sal_layer = post['layer_salinity']
        cor_layer = post['layer_corrosion']
        pit_layer = post['layer_pitting']
        oil_layer = post['layer_oil']
        rec_layer = post['layer_recess']
        ere_layer = post['layer_ext_recess']
        edit_sal = post['edit_salinity']
        edit_cor = post['edit_corrosion']
        edit_pit = post['edit_pitting']
        edit_oil = post['edit_oil']
        edit_rec = post['edit_recess']
        edit_ere = post['edit_ext_recess']
        with open("static/temp/background.png", 'wb') as bgfile, open("static/temp/layer_salinity.png", "wb") as salfile, open("static/temp/layer_corrosion.png", "wb") as corfile, open("static/temp/layer_pitting.png", "wb") as pitfile, open("static/temp/layer_oil.png", "wb") as oilfile, open("static/temp/layer_recess.png", "wb") as recfile, open("static/temp/layer_ext_recess.png", "wb") as erefile:   # Сохраняет вывод сетки на диск
            bgfile.write(picture)
            salfile.write(sal_layer)
            corfile.write(cor_layer)
            pitfile.write(pit_layer)
            oilfile.write(oil_layer)
            recfile.write(rec_layer)
            erefile.write(ere_layer)
        try:
            with open("static/temp/edit_salinity.png", 'wb') as file:    # Сохраняет пользовательскую картинку на диск
                file.write(base64.b64decode(split_b64str(edit_sal)))
        except:
            os.remove('static/temp/edit_salinity.png')
        try:
            with open("static/temp/edit_corrosion.png", 'wb') as file:
                file.write(base64.b64decode(split_b64str(edit_cor)))
        except:
            os.remove('static/temp/edit_corrosion.png')
        try:
            with open("static/temp/edit_pitting.png", 'wb') as file:
                file.write(base64.b64decode(split_b64str(edit_pit)))
        except:
            os.remove('static/temp/edit_pitting.png')
        try:
            with open("static/temp/edit_oil.png", 'wb') as file:
                file.write(base64.b64decode(split_b64str(edit_oil)))
        except:
            os.remove('static/temp/edit_oil.png')
        try:
            with open("static/temp/edit_recess.png", 'wb') as file:
                file.write(base64.b64decode(split_b64str(edit_rec)))
        except:
            os.remove('static/temp/edit_recess.png')
        try:
            with open("static/temp/edit_ext_recess.png", 'wb') as file:
                file.write(base64.b64decode(split_b64str(edit_ere)))
        except:
            os.remove('static/temp/edit_ext_recess.png')

    return render_template('blog/feedback.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/feedback', methods=('GET', 'POST'))
@login_required
def send_feedback(id):
    
    # Проверка отправляемых слоёв - нужно спросить у пользователя, что отправлять
    
    msg = Message("Test message",
                    sender="pigin.labdef@gmail.com",
                    recipients=["pigin.labdef@gmail.com"])
    msg.body=get_db().execute(
        'SELECT body'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()[0]
    #Неплохо бы завернуть этот код в метод
    image_data={
        'original':
        get_db().execute(
            'SELECT original_picture'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'salinity':
        get_db().execute(
            'SELECT edit_salinity'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'corrosion':
        get_db().execute(
            'SELECT edit_corrosion'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'pitting':
        get_db().execute(
            'SELECT edit_pitting'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'oil':
        get_db().execute(
            'SELECT edit_oil'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'recess':
        get_db().execute(
            'SELECT edit_recess'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0],
        'elongated_recess':
        get_db().execute(
            'SELECT edit_ext_recess'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()[0]
    }
    #Вместо отправки всего выбирать нужные слои или отправлять все и писать нужные слои текстом
    error = ""
    attach_imgs('original', image_data, msg)
    empty_layers = 0
    #Заменить на цикл
    try:
        attach_imgs('salinity', image_data, msg)
    except:
        error += "Salinity "
        empty_layers += 1
    try:
        attach_imgs('corrosion', image_data, msg)
    except:
        error += "Corrosion "
        empty_layers += 1
    try:
        attach_imgs('pitting', image_data, msg)
    except:
        error += "Pitting "
        empty_layers += 1
    try:
        attach_imgs('oil', image_data, msg)
    except:
        error += "Oil "
        empty_layers += 1
    try:
        attach_imgs('recess', image_data, msg)
    except:
        error += "Recess "
        empty_layers += 1
    try:
        attach_imgs('elongated_recess', image_data, msg)
    except:
        error += "Elongated recess"
        empty_layers += 1
    if (empty_layers == 6):
            flash("There are no edited layers for this post")
    else:
        if (error == ""):
            flash("Message sent with all the layers!")
            mail.send(msg)
        else:
            flash("Post " + get_db().execute(
                'SELECT title'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' WHERE p.id = ?',
                (id,)
            ).fetchone()[0] + " (ID: " + str(id) + "): The following layers weren't saved to be sent: " + error)
            mail.send(msg)
    return redirect(url_for('blog.index'))
