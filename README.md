# Aiglos

### ☤ Feature

1. 在线浏览渲染的本地Markdown文件。
2. 提供 http://djangobook.py3k.cn/2.0/ 那样的评注系统。
3. 评注支持Markdown语法。

### ☤ Demo

[Demo](https://dry-castle-71587.herokuapp.com/)

### ☤ Quick start

```
❯ git clone https://github.com/dongweiming/aiglos
❯ cd aiglos
❯ virtualenv-2.7 venv
❯ source venv/bin/activate
❯ pip install -r requirements.txt
❯ touch local_settings.py  # 增加BOOK_DIR (Markdown文件存放目录), SQLALCHEMY_DATABASE_URI等配置
❯ gunicorn -w 3 run:app -b 0.0.0.0:8000
```
