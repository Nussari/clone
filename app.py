from flask import Flask, render_template, Response, session, request
from werkzeug.utils import redirect
from picam_py import Camera
import pyrebase
from json import loads

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
errors = {'404': 'Síða ekki til', '1062': 'Númer nú þegar í símaskrá', '500': 'Almenn Villa', '409': 'Netfang í notkun', '400': 'Ekki nógu sterkt lykilorð', '422': 'Ólögleg kennitala', 'INVALID_EMAIL': 'Rangt netfang', 'EMAIL_EXISTS': 'Netfang í notkun', 'INVALID_PASSWORD': 'Rangt lykilorð', 'WEAK_PASSWORD': 'Ekki nógu sterkt lykilorð'}

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
        error_json = e.args[1]
        error = loads(error_json)['error']
        errMSG = error['message']
        if errMSG=='WEAK_PASSWORD : Password should be at least 6 characters':
            errMSG='WEAK_PASSWORD'
        print(errMSG)
        if errMSG in errors:
            return redirect('error/' + errMSG)
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


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/error/404')


@app.route('/error/<error>')
def error(error):
    return render_template('error.html', error=errors[error])


if __name__ == '__main__':
    app.run(host='10.11.46.120', debug=True, threaded=True)