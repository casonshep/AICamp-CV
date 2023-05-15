# import requirements needed
import os, shutil

# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session, flash
from url_utils import get_base_url
import model, requests
from werkzeug.utils import secure_filename

# setup the webserver + API calls
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)

# initialize backend to handle uploaded files
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#clears uploads folder on flask app run
for filename in os.listdir(UPLOAD_FOLDER):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, template_folder='templates', static_url_path=base_url + 'static')

# adds upload folder to base app directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(64)

# set up the routes and logic for the webserver
@app.route(f'{base_url}')
def home():
    return render_template('index.html', genre="no image uploaded")

# tests if file is a valid extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# bulk of work
@app.route(f'{base_url}', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
        file = request.files['file']
      
        if file.filename == '':
            flash("no selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # sanitizes and locally saves the image while the session is running
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
          
            # inference api call returns string
            genre_guess = model.query(f'static/uploads/{filename}')
            print(genre_guess)
            if 'error' in genre_guess:
                print('\nerror caught')
                flash('API error has occurred, wait a few seconds and try again...')
                return redirect(url_for('home'))
            else:
            # parsing and processing result from API to cleaner string
                genre_score = genre_guess[0]['score']
                genre_score *= 100
                genre_score = '%.4f'%(genre_score)
                genre_label = genre_guess[0]['label']
                genre_guess_label = f'There is a {genre_score} % chance that image is {genre_label}'
            # saving string to session data
                session['data'] = genre_guess_label
            return redirect(url_for('results', resulting_string=session["data"]))

@app.route(f'{base_url}/results')
def results():
    return render_template('results.html', resulting_string=session['data'])

if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'piercingfrequentos--casonshepard1.repl.co'
    
    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host = '0.0.0.0', port=port, debug=True)