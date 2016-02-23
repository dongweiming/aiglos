# coding=utf-8
import os
import codecs
from datetime import datetime
from json import dumps

from flask import Flask, Markup, request
from werkzeug.utils import secure_filename
from flask_mako import render_template, MakoTemplates, render_template_def
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, func
import mistune

app = Flask(__name__)
mako = MakoTemplates(app)
app.config.from_object('config')
db = SQLAlchemy(app)

BOOK_DIR = app.config['BOOK_DIR']
markdown = None

if BOOK_DIR is None:
    print 'You must specify `BOOK` in local_settings.py'
    exit(1)


def get_summary_content():
    path = os.path.join(BOOK_DIR, 'SUMMARY.md')
    if os.path.exists(path):
        with codecs.open(path, 'r', 'utf-8') as f:
            content = f.read()
    else:
        content = ('Aiglos uses a SUMMARY.md file to define the structure '
                   'of chapters and subchapters of the book. See '
                   'https://help.gitbook.com/format/chapters.html '
                   'for more details.')
    return Markup(markdown(content))


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    nodenum = db.Column(db.Integer)
    chapter = db.Column(db.String(100))
    section = db.Column(db.String(100))
    pub_date = db.Column(db.DateTime)

    def __init__(self, chapter, section, nodenum, content, pub_date=None):
        self.chapter = chapter
        self.section = section
        self.nodenum = nodenum
        self.content = content
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Comment {} [{} {} {}]>'.format(self.id, self.chapter,
                                                self.section, self.nodenum)


db.create_all()


class Renderer(mistune.Renderer):
    def __init__(self, **kwargs):
        super(Renderer, self).__init__(**kwargs)
        self.c = 0
        self.cn = 0

    def header(self, text, level, raw=None):
        res = '<h%d class="cn title" id="cn%s">%s</h%d>\n' % (
            level, self.cn, text, level)
        self.cn += 1
        return res

    def paragraph(self, text):
        res = '<p class="cn" id="cn%s">%s</p>\n' % (
            self.cn, text.strip(' '))
        self.cn += 1
        return res

    def block_code(self, code, lang=None):
        code = code.rstrip('\n')
        code = mistune.escape(code, smart_amp=False)
        res = '<pre class="cn literal-block" id="cn%s">%s\n</pre>\n' % (
            self.cn, code)
        self.cn += 1
        return res

    def list_item(self, text):
        res = '<li class="cn" id="cn%s"><p class="first cn" id="cn%s">%s</li>\n' % (  # noqa
            self.cn, self.cn, text)
        self.cn += 1
        return res


@app.before_request
def before_request():
    renderer = Renderer()
    global markdown
    markdown = mistune.Markdown(renderer=renderer)


def patch_comments(comments):
    for comment in comments:
        comment.content = Markup(markdown(comment.content))
        yield comment


@app.route('/')
def index():
    content = get_summary_content()
    return render_template('index.html', content=content)


@app.route('/<chapter>/<section>/')
def section(chapter, section):
    chapter = secure_filename(chapter)
    section = secure_filename(section)
    path = os.path.join(BOOK_DIR, chapter, section)
    with codecs.open(path, 'r', 'utf-8') as f:
        content = f.read()
    content = Markup(markdown(content))
    return render_template('page.html', **locals())


@app.route('/<chapter>/<section>/comments/<comment_id>/')
@app.route('/<chapter>/<section>/comments/', methods=['GET', 'POST'])
def comment(chapter, section, comment_id=None):
    if comment_id is None and request.method == 'POST':
        nodenum = request.form.get('nodenum')
        comment = request.form.get('comment')
        if not (nodenum and comment) or not nodenum.isdigit():
            return 'Wrong!'
        nodenum = int(nodenum)
        c = Comments(chapter, section, nodenum, comment)
        db.session.add(c)
        db.session.commit()
        return '<li></li>'

    cond = {'chapter': chapter, 'section': section}
    if comment_id is not None:
        cond.update({'nodenum': comment_id})
    comments = Comments.query.filter_by(**cond).order_by(Comments.id.desc())
    comments = patch_comments(comments)
    return render_template_def('comment.html', 'main', comments=comments)


@app.route('/<chapter>/<section>/comments/counts/')
def counts(chapter, section):
    counts = db.session.query(Comments.nodenum, func.count(
        distinct(Comments.id))).filter_by(
            chapter=chapter, section=section).group_by(
                Comments.nodenum).all()
    return dumps(counts)


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.debug)
