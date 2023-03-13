import os
import os.path
from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, send_file
from werkzeug.utils import secure_filename
import DH
import pickle
import random
from cryptography.hazmat.primitives import serialization

UPLOAD_FOLDER = './media/text-files/'
UPLOAD_KEY = './media/public-keys/'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

'''
-----------------------------------------------------------
					PAGE REDIRECTS
-----------------------------------------------------------
'''
def post_upload_redirect():
	return render_template('post-upload.html')

@app.route('/register')
def call_page_register_user():
	return render_template('register.html')

@app.route('/home')
def back_home():
	return render_template('index.html')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload-file')
def call_page_upload():
	return render_template('upload.html')
'''
-----------------------------------------------------------
				DOWNLOAD KEY-FILE
-----------------------------------------------------------
'''
@app.route('/public-key-directory/retrieve/key/<username>')
def download_public_key(username):
	# print(username)
	# return render_template('register.html')
	for root,dirs,files in os.walk('./media/public-keys/'):
		for file in files:
			list = file.split('-')
			if list[0] == username:
				filename = UPLOAD_KEY+file
				print(filename)
				return send_file(filename, as_attachment=True)


@app.route('/file-directory/retrieve/file/<filename>')
def download_file(filename):
	filepath = UPLOAD_FOLDER+filename
	if(os.path.isfile(filepath)):
		return send_file(filepath, attachment_filename='fileMessage-thrainSecurity.txt',as_attachment=True)
	else:
		return render_template('file-list.html',msg='An issue encountered, our team is working on that')

'''
-----------------------------------------------------------
		BUILD - DISPLAY FILE - KEY DIRECTORY
-----------------------------------------------------------
'''
# Build public key directory
@app.route('/public-key-directory/')
def downloads_pk():
	username = []
	if(os.path.isfile("./media/database/database_1.pickle")):
		pickleObj = open("./media/database/database_1.pickle","rb")
		username = pickle.load(pickleObj)
		pickleObj.close()
	if len(username) == 0:
		return render_template('public-key-list.html',msg='Aww snap! No public key found in the database')
	else:
		return render_template('public-key-list.html',msg='',itr = 0, length = len(username),directory=username)

# Build file directory
@app.route('/file-directory/')
def download_f():
	for root,dirs,files in os.walk(UPLOAD_FOLDER):
		if(len(files) == 0):
			return render_template('file-list.html',msg='Aww snap! No file found in directory')
		else:
			return render_template('file-list.html',msg='',itr=0,length=len(files),list=files)

'''
-----------------------------------------------------------
				UPLOAD ENCRYPTED FILE
-----------------------------------------------------------
'''

@app.route('/data', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return 'NO FILE SELECTED'
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
			return post_upload_redirect()
		return 'Invalid File Format !'

'''
-----------------------------------------------------------
REGISTER UNIQUE USERNAME AND GENERATE PUBLIC KEY WITH FILE
-----------------------------------------------------------
'''
@app.route('/register-new-user', methods = ['GET', 'POST'])

def register_user():
    usernamelist = []
    # Import pickle file to maintain uniqueness of the keys
    if(os.path.isfile("./media/database/database_1.pickle")):
        with open("./media/database/database_1.pickle", "rb") as f:
            usernamelist = pickle.load(f)
    
    # Declare a new list which consists all usernames 
    if request.form['username'] in usernamelist:
        return render_template('register.html', name='Username already exists')
    
    username = request.form['username']
    firstname = request.form['first-name']
    secondname = request.form['last-name']
    
    #Generating a unique private key
    privatekey = DH.generate_private_key()
    while True:
        filename = UPLOAD_KEY+username+'p-PrivateKey.pem'
        if not os.path.exists(filename):
            break
    
    with open(filename, "wb") as f:
        pvt = privatekey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        f.write(pvt)
    
    #Updating a new public key for a new user
    filename = UPLOAD_KEY+username+'-PublicKey.pem'
    # Generate public key and save it in the file generated
    publickey = DH.generate_public_key(privatekey)
    pub = publickey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, "wb") as f:
        f.write(pub)
    
    # Save the username to the database
    with open("./media/database/database_1.pickle", "wb") as f:
        usernamelist.append(username)
        pickle.dump(usernamelist, f)
    
    return render_template('key-display.html', privatekey=privatekey)
	
if __name__ == '__main__':
	#app.run(host="0.0.0.0", port=80)
	app.run()