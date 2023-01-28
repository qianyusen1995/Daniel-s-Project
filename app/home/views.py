# encoding: utf-8
import os
import json
import uuid
import datetime

from . import home
from flask import render_template, redirect, url_for, flash, session, request, Response
from app.home.froms import RegisterForm, UserLoginForm, CommentForm, UserdetailForm
from app.models import User, UserLog, Preview, Tag, Movie, Comment, Moviecol
from app import db, app, rd
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from functools import wraps


# 登陆装饰器
def admin_login_req(f):
    @wraps(f)
    def decorate_function(*args, **kwargs):
        if not session.get("name", ""):
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorate_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@home.route("/", methods=["GET"])
def index(page=None):
    if page is None:
        page = 1
    tags = Tag.query.all()
    page_data = Movie.query
    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get('star', 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 上传时间
    time = request.args.get('time', 0)
    if int(star) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    # 播放量
    pm = request.args.get('pm', 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论数量
    cm = request.args.get('cm', 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    # page = request.args.get("page", 1)
    page_data = page_data.paginate(page=int(page), per_page=10)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            redirect(url_for('home.login'))
        session['name'] = data['name']
        session['name_id'] = user.id
        userlog = UserLog(
            user_id=user.id,
            ip=request.remote_addr,
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.index"))
    return render_template("home/login.html", form=form)


@home.route("/logout/")
@admin_login_req
def logout():
    session.pop("name", None)
    session.pop("name_id", None)
    return redirect(url_for("home.login"))


# 会员注册
@home.route("/register/", methods=["POST","GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user_name = User.query.filter_by(name=data["name"]).first()
        user_email = User.query.filter_by(email=data["email"]).first()
        user_phone = User.query.filter_by(phone=data["phone"]).first()
        if user_name:
            flash("账号已经存在，请重新输入！", 'err')
            return redirect(url_for('home.register'))
        if user_email:
            flash("账号已经存在，请重新输入！", 'err')
            return redirect(url_for('home.register'))
        if user_phone:
            flash("账号已经存在，请重新输入！", 'err')
            return redirect(url_for('home.register'))
        if data["pwd"] != data["re_pwd"]:
            flash("密码不一致，请重新输入！", 'err')
            return redirect(url_for('home.register'))
        user = User(name=data["name"],
                    email=data["email"],
                    phone=data["phone"],
                    pwd=generate_password_hash(data["pwd"]),
                    uuid=uuid.uuid4().hex)
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "ok")
    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@admin_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["name_id"]))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        file_face = secure_filename(form.face.data.filename)
        if not os.path.exists(app.config["FC_DIR"]):
            os.makedirs(app.config["FC_DIR"])
            os.chmod(app.config["FC_DIR"], "rw")
        user.face = change_filename(file_face)
        form.face.data.save(app.config["FC_DIR"] + user.face)

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称已经存在！", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已经存在！", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机号码已经存在！", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/")
@admin_login_req
def pwd():
    return render_template("home/pwd.html")


@home.route("/comments/")
@admin_login_req
def comments():
    return render_template("home/comments.html")


@home.route("/loginlog/<int:page>", methods=["GET"])
@admin_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = UserLog.query.filter_by(
        user_id=int(session["name_id"])
    ).order_by(
        UserLog.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


# 添加电影收藏
@home.route("/moviecol/add/", methods=["GET"])
@admin_login_req
def moviecol_add():
    name_id = request.args.get("name_id", "")
    movie_id = request.args.get("movie_id", "")
    movie_col = Moviecol.query.filter_by(
        user_id=int(name_id),
        movie_id=int(movie_id)
    ).count()
    if movie_col == 1:
        res = dict(ok=0)
    if movie_col == 0:
        movie_col = Moviecol(
            user_id=int(name_id),
            movie_id=int(movie_id)
        )
        db.session.add(movie_col)
        db.session.commit()
        res = dict(ok=1)
    return json.dumps(res)


# 电影收藏
@home.route("/moviecol/<int:page>", methods=["GET"])
@admin_login_req
def moviecol(page):
    if page is None:
        page = 1
    page_data = Moviecol.query.order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


@home.route("/animation/")
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html", data=data)


@home.route("/search/<int:page>")
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count=Movie.query.filter(
        Movie.title.ilike("%"+key+"%")
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike("%"+key+"%")
    ).order_by(Movie.addtime.desc()).paginate(
        page=page, per_page=10
    )
    page_data.key = key
    return render_template("home/search.html", key=key, page_data=page_data,movie_count=movie_count)


@home.route("/play/<int:id>/<int:page>", methods=["GET", "POST"])
def play(id=None, page=None):
    if page is None:
        page = 1
    movie = Movie.query.get_or_404(int(id))
    movie.playnum = movie.playnum + 1
    page_data = Comment.query.join(Movie).join(User).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id,
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    form = CommentForm()
    # todo 表单显示错误
    if 'name' in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            movie_id=movie.id,
            user_id=session["name_id"],
            content=data["content"],
        )
        movie.commentnum = movie.commentnum + 1
        db.session.add(comment)
        db.session.commit()
        db.session.add(movie)
        db.session.commit()
        flash("评论成功！", 'ok')
        return redirect(url_for('home.play', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data)


@home.route("/video/<int:id>/<int:page>", methods=["GET", "POST"])
def video(id=None, page=None):
    if page is None:
        page = 1
    movie = Movie.query.get_or_404(int(id))
    movie.playnum = movie.playnum + 1
    page_data = Comment.query.join(Movie).join(User).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id,
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    form = CommentForm()
    # todo 表单显示错误
    if 'name' in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            movie_id=movie.id,
            user_id=session["name_id"],
            content=data["content"],
        )
        movie.commentnum = movie.commentnum + 1
        db.session.add(comment)
        db.session.commit()
        db.session.add(movie)
        db.session.commit()
        flash("评论成功！", 'ok')
        return redirect(url_for('home.video', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html", movie=movie, form=form, page_data=page_data)


@home.route("/tm/", methods=["GET", "POST"])
def tm():
    if request.method == "GET":
        id = request.args.get("id")
        key = "movie" + str(id)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code":1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        data = json.loads(request.get_data())
        msg = {
            "__v":0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data["type"],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        rd.lpush("movie"+str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype="application/json")



