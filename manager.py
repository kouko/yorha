"""
這是拿來init & migrate DB用的檔案
執行方式為：

manager.py db init
manager.py db migrate
manager.py db upgrade

init後會產生migrations資料夾，感覺好像不能刪掉～
"""

from flask_migrate import Migrate, MigrateCommand  # FLask-SQLAlchemy的延伸套件
from flask_script import Manager # Flask Command Line INterface
from yorha import app
from yorha.models import db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()