from flask import Flask, render_template, Response, session, request
from werkzeug.utils import redirect
from camera_pi import Camera
import pyrebase

app = Flask(__name__)
config = {
    'apiKey': "AIzaSyDGNCH3whndlbTFhYP7OO5HmsX2Y4lQniQ",
    'authDomain': "vesm-e023f.firebaseapp.com",
    'projectId': "vesm-e023f",
    'storageBucket': "vesm-e023f.appspot.com",
    'messagingSenderId': "1044560069079",
    'appId': "1:1044560069079:web:f64966440adda963ea0b92",
    'measurementId': "G-S3B608VMRE"
}
app.secret_key = 'secretnohax'
fb = pyrebase.initialize_app(config)
au = fb.auth()

def get_login():
    if 'login' not in session:
        session['login'] = []
    return session['login']


@app.route('/')
def index():
    if not len(get_login()):
        return redirect('/login')
    return render_template('index.html')


@app.route('/login')
def login():
    if not len(get_login()):
        return render_template('login.html')
    return redirect('/')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    pw = request.form['pw']
    try:
        if request.form['type']=='login':
            session['login'] = au.sign_in_with_email_and_password(email, pw)
        else:
            user = au.create_user_with_email_and_password(email, pw)
            session['login'] = au.sign_in_with_email_and_password(email, pw)
    except Exception as e:
        return redirect('/error/500')
    return redirect('/')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='10.11.46.120', debug=True, threaded=True)