# coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Regexp
from app.models import User

from app.models import User


class RegisterForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号！",
            # "required": "required"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱！",
            # "required": "required"
        }

    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp("1\\d{1}\\d{9}", message="手机格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机！",
            # "required": "required"
        }

    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！",
            # "required": "required"
        }

    )

    re_pwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请再次输入密码！"),
            EqualTo("pwd", "两次密码不一致！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请再次输入密码！",
            # "required": "required"
        }

    )
    submit = SubmitField(
        "注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        })


class UserdetailForm(FlaskForm):

    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
        }
    )
    email = StringField(label="邮箱", validators=[
        DataRequired("请输入邮箱！"),
        Email("邮箱格式不正确！")
    ],
                        description="邮箱",
                        render_kw={
                            "class": "form-control input-lg",
                            "placeholder": "请输入邮箱！",
                        }
                        )
    phone = StringField(label="手机", validators=[
        DataRequired("请输入手机！"),
        Regexp("1[34578]\\d{9}", message="手机格式不正确")
    ],
                        description="手机",
                        render_kw={
                            "class": "form-control input-lg",
                            "placeholder": "请输入手机！",
                        }
                        )
    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像",
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success",
        }
    )


class UserLoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            # "required": "required"
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            # "required": "required"
        }

    )
    submit = SubmitField(
        "登陆",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        })

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 0:
            raise ValidationError("Account not exist")


class CommentForm(FlaskForm):
    # 各个表单标签之间不能加逗号，注意！
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容！")
        ],
        description="内容",
        render_kw={
            "id": "input_content",
        }
    )
    submit = SubmitField(
        "提交评论",
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub",
        }
    )