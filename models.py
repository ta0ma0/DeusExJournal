from app import db
from datetime import datetime

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Post {self.title}>'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    system_prompt = db.Column(db.Text, nullable=False,
                              default="Ты - полезный AI-ассистент, комментирующий текст.")
    prompt_template = db.Column(db.Text, nullable=False)
    # nullable=False - это правильное состояние, поле не должно быть пустым.
    # server_default='true' - инструкция для БД, какое значение использовать по умолчанию.
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default='true')

    comments = db.relationship('Comment', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Comment by {self.role.name} on Post {self.post_id}>'