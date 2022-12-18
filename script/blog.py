from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import get_db

bp = Blueprint('blog', __name__, url_prefix='/blog')


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT id, title, body, created, author_id'
        ' FROM post'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        user_id = request.form['user_id']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, user_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(post_id):
    post = get_db().execute(
        'SELECT id, title, body, created, author_id'
        ' FROM post'
        ' WHERE id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    return post


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
def update(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, post_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:post_id>/delete', methods=('POST',))
def delete(post_id):
    get_post(post_id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>/page', methods=('GET',))
def page(post_id):
    post = get_post(post_id)
    return render_template('blog/page.html', post=post)
