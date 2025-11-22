from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Ahoj Moniko, toto je web PAPRCEK. Běží na portu 5001!'
