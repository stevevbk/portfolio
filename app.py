#Import required libraries
from flask import Flask, render_template, send_file
import os
import datetime

#Create an instance app
app = Flask(__name__)

dataProjectsList = [
    {
        'name': 'Speech to text & Text to Speech',
        'usedTechnos': ['Python', 'AssemblyAI', 'gTTS'],
        'description': 'Web development projects',
        'image': 'web.jpg',
        'link': 'web',
    },
    {
        'name': 'Social Media ChatBot',
        'used technos': ['DeepSeek', 'Python', 'Flask', 'TensorFlow', 'NLTK'],
        'description': 'Web development projects',
        'image': 'web.jpg',
        'link': 'web',
    },
    {
        'name': 'Recommendation System',
        'used technos': ['HTML', 'CSS', 'JavaScript'],
        'description': 'Web development projects',
        'image': 'web.jpg',
        'link': 'web',
    },
    {
        'name': 'Generative AI',
        'used technos': ['HTML', 'CSS', 'JavaScript'],
        'description': 'Web development projects',
        'image': 'web.jpg',
        'link': 'web',
    },
    {
        'name': "What's next ?",
        'used technos': ['HTML', 'CSS', 'JavaScript'],
        'description': 'Web development projects',
        'image': 'web.jpg',
        'link': 'web',
    }
]

#define routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/web')
def web():
    return render_template('web.html')

@app.route('/data')
def data():
    return render_template('data.html', dataProjects=dataProjectsList)

@app.route('/CloudDevOps')
def CloudDevOps():
    return render_template('CloudDevOps.html')

#Routes for downloads
@app.route('/cv_eng')
def cv_eng():
    return send_file('static/CV-2025-EN-EU.pdf', as_attachment=True)

@app.route('/cv_fr')
def cv_fr():
    return send_file('static/CV-2025.pdf', as_attachment=True)

@app.route("/heure")
def heure():
    now = datetime.datetime.now()
    print(now)
    return "What time is it now?"
    
#run app on debug mode
if __name__ == '__main__':
    app.run(debug=True)