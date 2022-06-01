import os
from flask import Flask, flash, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import mysql.connector
#werkzeug.utils fix til importerings fejl ifht. forkert navn: https://stackoverflow.com/questions/61628503/flask-uploads-importerror-cannot-import-name-secure-filename

# Vores MySQL objekter og variabler
conn = mysql.connector.connect(host='localhost', port='3306',
                               database='login',
                               user='admin',
                               password='12345678')
curs = conn.cursor()
selectQuery = "SELECT * FROM login"

#Vælg upload folderens sti
UPLOAD_FOLDER = './UPLOAD_FOLDER'
#Vælg hvilke filtyper er tilladt
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pptx'}

app = Flask(__name__)

# secret key bruges til at kunne lave sessions
app.secret_key = "grp7"

#Definere upload folderen: https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/
#Brug af forwardslash pga. backslash string escape error til at definere path
#Virker ikke foreløbigt og uploaded filer kommer i samme mappe som .py filen https://stackoverflow.com/questions/51733419/flask-file-upload-is-not-saving-the-file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#funktion til at tjekke tilladt file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    msg = ""
    if session.get('loggedin') == None:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            curs.execute('SELECT * FROM login WHERE username=%s AND password=%s',(username, password,))
            record = curs.fetchone()
            if record:
                session['loggedin']= True
                session['username']= username
                print(session)
                return render_template("home.html", username=session['username'])
            else:
                msg = "password and or username is incorrect"
                return render_template('index.html', msg=msg)
    elif session.get('loggedin') == True:
        return render_template("home.html", username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    msgx = 'Du er logget af'
    return render_template('index.html', msgx=msgx)

@app.route('/login/upload')
#html siden hvorfra man vælger filen der skal uploades, se "upload.html"
def upload_file():
    if session["loggedin"]:
        return render_template('upload.html')

@app.route('/uploaded', methods = ['GET', 'POST'])
#uploader function der uploader filen og som upload.html redirecter til
#der gøres brug af Werkzeugs secure_filename til at gemme med
#Skal evt. redirecte til anden side efter x antal sek?
def uploader():
    if request.method == 'POST':
        #tjek om post requesten har en fil
        if 'file' not in request.files:
            flash('Ingen fil valgt')
            return redirect('/login/upload')
        f = request.files['file'] #object til at holde
        #hvis ingen fil er valgt giver browseren en tom fil
        #uden filnavn?
        if f.filename == '':
            flash('Ingen fil valgt')
            return redirect('/login/upload')
        #hvis det er en tilladt fil gemmes den i valge folder
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Filen blev uploadet')
        return render_template('upload.html')

@app.route('/login/download')
def download_file():
    return render_template('download.html')

@app.route('/download_files')
def download():
    return send_file('./UPLOAD_FOLDER/abe.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)