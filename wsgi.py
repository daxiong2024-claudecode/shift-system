import sys
print("Step 1: starting wsgi.py", flush=True)

from flask import Flask
print("Step 2: flask imported", flush=True)

from flask_sqlalchemy import SQLAlchemy
print("Step 3: flask_sqlalchemy imported", flush=True)

from flask_migrate import Migrate
print("Step 4: flask_migrate imported", flush=True)

from flask_login import LoginManager
print("Step 5: flask_login imported", flush=True)

from app.config import config
print("Step 6: config imported", flush=True)

from app import create_app
print("Step 7: create_app imported", flush=True)

app = create_app('development')
print("Step 8: app created", flush=True)

if __name__ == '__main__':
    app.run()
