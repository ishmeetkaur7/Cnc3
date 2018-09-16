from flask import Flask, render_template, session, g, request, redirect, url_for
import pymongo
import json
import numpy as np
import matplotlib.pyplot as plt
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES
import json
import boto3
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

# UPLOAD_FOLDER = '/Users/ishmeetkaur/Desktop/SmilingFacesFinal/static'

app = Flask('__name__')
connection = pymongo.MongoClient("mongodb://localhost:27017/")
# db= pymongo.myclient["mydatabase"]
db = connection['mydatabase']
app.config['SECRET_KEY']='youcantguessthis'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = '/Users/ishmeetkaur/Desktop/SmilingFacesFinal/'
configure_uploads(app, photos)
import Algorithmia
AWS_ACCESS_KEY = 'AKIAJVNT2E3BPDFJ4ZMA'
AWS_ACCESS_SECRET_KEY = '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'
bucketName = "photobucket099"
BUCKET = "photobucket099"

FEATURES_BLACKLIST = ("Landmarks", "Emotions", "Pose", "Quality", "BoundingBox", "Confidence")


@app.route('/')
def index():
    print(connection.database_names())
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print('login')
    session.pop('user', None)
    user = db['users'].find_one({'username': request.form['username']})
    print(user)
    if user != None and user['password'] == request.form['password']:
        session['user'] = user
        print("yo")
        return redirect(url_for('panel'))
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if g.user:
        scores = db['scores'].find_one({'_id': g.user['_id']})
        prediction = sum(scores['scores'])
        percent = prediction/len(scores['scores'])*100.00

        if (prediction>=0.45*len(scores['scores'])):
            prediction = 1
        else:
            prediction = 0
            percent = 100 - percent
        return render_template('profile.html', user=g.user, prediction=prediction, percent=percent)
    return redirect(url_for('index'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if g.user:
        scores = db['scores'].find_one({'_id': g.user['_id']})
        prediction = sum(scores['scores'])
        percent = prediction/len(scores['scores'])*100.00

        if (prediction>=0.45*len(scores['scores'])):
            prediction = 1
        else:
            prediction = 0
            percent = 100 - percent

        scores['scores'].append(prediction)
        print(percent)
        print(prediction)
        # plt.figure(figsize=(6, 7))
        # ax = plt.subplot(111)
        # ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # plt.ylim(0, 1.1)
        # plt.xlim(0, 12)
        # plt.xticks(range(11), [str(i+1) + ' day ago' for i in range(11)], rotation=30, fontsize=7)
        # plt.yticks(fontsize=7)
        # plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='on', left='off', right='off', labelleft='on')
        # plt.plot(range(11), scores['scores'])
        # plt.title(g.user['name'] + ' Health status for past 10 days and future prediction.')
        # plt.savefig('static/' + g.user['username'] + '.png')
        # g.user['filename'] = g.user['username'] + '.png'
        return render_template('admin.html', user=g.user, scores=scores, prediction=prediction, percent=percent)
    return redirect(url_for('index'))

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    if g.user:
        scores = db['scores'].find_one({'_id': g.user['_id']})
        prediction = sum(scores['scores'])
        percent = prediction/len(scores['scores'])*100.00

        if (prediction>=0.45*len(scores['scores'])):
            prediction = 1
        else:
            prediction = 0
            percent = 100 - percent

        print(prediction)
        scores['scores'].append(prediction)
        plt.figure(figsize=(6, 7))
        ax = plt.subplot(111)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.ylim(0, 1.1)
        plt.xlim(0, 12)
        plt.xticks(range(11), [str(i+1) + ' day ago' for i in range(11)], rotation=30, fontsize=7)
        plt.yticks(fontsize=7)
        plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='on', left='off', right='off', labelleft='on')
        plt.plot(range(11), scores['scores'])
        plt.title(g.user['name'] + ' Health status for past 10 days and future prediction.')
        plt.savefig('static/' + g.user['username'] + '.png')
        g.user['filename'] = g.user['username'] + '.png'
        return render_template('graph.html', user=g.user, scores=scores, prediction=prediction, percent=percent)
    return redirect(url_for('index'))

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if g.user:
        scores = db['scores'].find_one({'_id': g.user['_id']})
        prediction = sum(scores['scores'])
        percent = prediction/len(scores['scores'])*100.00

        if (prediction>=0.45*len(scores['scores'])):
            prediction = 1
            songs = db.songs.find_one({'mood':'sad'})
        else:
            prediction = 0
            percent = 100 - percent
            songs = db.songs.find_one({'mood':'happy'})

        # songs = songs['songs']

        scores['scores'].append(prediction)
        return render_template('suggestions.html', user=g.user, percent=percent, prediction=prediction, songs=songs)
    return redirect(url_for('index'))

@app.route('/downloaddata')
def downloaddata():
    response = {
            'user': g.user,
            'scores': db['scores'].find_one({'_id': g.user['_id']})
        }
    return json.dumps(response)

@app.route('/facialExpression', methods=['GET', 'POST'])
def facialExpression():
    if g.user:
        scores = db['scores'].find_one({'_id': g.user['_id']})
        prediction = sum(scores['scores'])
        percent = prediction/len(scores['scores'])*100.00

        if (prediction>=0.45*len(scores['scores'])):
            prediction = 1
            songs = db.songs.find_one({'mood':'sad'})
        else:
            prediction = 0
            percent = 100 - percent
        if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            # filename=filename.replace('/','');
            print(filename)
            Key = filename
            outPutname = filename
            KEY = Key

            s3 = boto3.client('s3')
            s3.upload_file(Key, bucketName, outPutname)
            txt1 = ""
            txt2 = ""
            txt3 = ""

            for face in detect_faces(BUCKET, KEY):
                print ("Face ({Confidence}%)".format(**face))
                txt1+=("Face ({Confidence}%)".format(**face)+"\n")
                # emotions
                for emotion in face['Emotions']:
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    txt2+=("  {Type} : {Confidence}%".format(**emotion)+"\n")
                # quality
                for quality, value in face['Quality'].items():
                    print ("  {quality} : {value}".format(quality=quality, value=value))
                    txt3+=("  {quality} : {value}".format(quality=quality, value=value)+"\n")



            # client = Algorithmia.client('sim1RQY2i69eKdgkzU8PAsaq+V01')
            # algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
            # nlp_directory = client.dir("data://ishi/nlp_directory")
            # if nlp_directory.exists() is False:
            #     nlp_directory.create()
            # # Create your data collection if it does not exist
            # obj = "data://ishi/nlp_directory/"+filename
            # if client.file(obj).exists() is False:
            #     # Upload local file
            #     client.file(obj).putFile("/Users/ishmeetkaur/Desktop/SmilingFacesFinal/"+filename)
            # input = {
            # "image": obj,
            # "numResults": 1
            # }
            # print(algo.pipe(input).result)
            # x= algo.pipe(input).result
            # if x['results'][0]['emotions'][0]['label'] == "Happy":
            #     prediction=1
            # else:
            #     prediction=0
            return render_template('facialExpression.html', user=g.user, percent=percent, txt1=txt1, txt2=txt2, txt3=txt3)
    return render_template('facialExpression.html', user=g.user, percent=percent)



def detect_faces(bucket, key, attributes=['ALL']):
    rekognition = boto3.client("rekognition")
    response = rekognition.detect_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key,
            }
        },
        Attributes=attributes,
    )
    return response['FaceDetails']

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000, debug = True)
