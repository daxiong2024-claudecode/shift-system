import sys
print("Step 1: starting wsgi.py", flush=True)

from flask import Flask
print("Step 2: flask imported", flush=True)

app = Flask(__name__)
print("Step 3: flask app created", flush=True)


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/')
def hello():
    return 'Railway is working!', 200


print("Step 4: wsgi.py ready", flush=True)
