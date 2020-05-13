from flask import Flask, Response,render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('record-live-audio.html')

if __name__ == "__main__":
    app.run(ssl_context='adhoc',port=80, debug=False)