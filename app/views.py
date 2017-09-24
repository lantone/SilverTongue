from flask import render_template, request, redirect, url_for, abort
from app import app
import speechace
from subprocess import Popen
import timestampencoding
from glob import glob

base_path = '/Users/lantonel/SilverTongue/'

@app.route('/')
@app.route('/enter_url')
def enter_url():
   return render_template('enter_url.html')

@app.route('/process')
def process_input():
   url = request.args.get('url_text')
   video_id = url.split('=')[-1]
   timestamp = timestampencoding.build_timestamp()
   print video_id, timestamp
   Popen(['process_input.py', video_id, timestamp])
   return redirect(url_for('decision', video_id=video_id, session=timestamp))

@app.route('/results')
def decision():
   session = request.args['session']
   video_id = request.args['video_id']
   output_dir = base_path + '/app/static/' + session + '/'   

   ready = False
   if len(glob(output_dir+'*.png')) >= 6:
      ready = True
   return render_template('results.html', ready = ready, session = session, video_id=video_id)
