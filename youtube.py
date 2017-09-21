from __future__ import unicode_literals
import youtube_dl
import os

def extractFromYoutube(url_id, output_path):

    ydl_opts = {
        'writesubtitles' : True,
        'writeautomaticsub' : True,
        'format': 'bestaudio/best',
        'outtmpl' : output_path+'/%(id)s.%(ext)s',
        'forcefilename' : True,
        'subtitleslangs' : ['en'],
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                }],
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        address = 'https://www.youtube.com/watch?v='+url_id
        print address
        ydl.download([address])

def extractFromMyYoutube(url_id, output_path):

    YOUTUBE_USERNAME = os.environ['YOUTUBE_USERNAME']
    YOUTUBE_PASSWORD = os.environ['YOUTUBE_PASSWORD']

    ydl_opts = {
        'username' : YOUTUBE_USERNAME,
        'password' : YOUTUBE_PASSWORD,
#        'writesubtitles' : True,
        'writeautomaticsub' : True,
        'format': 'bestaudio/best',
        'outtmpl' : output_path+'/%(id)s.%(ext)s',
        'forcefilename' : True,
        'subtitleslangs' : ['en'],
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                }],
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        address = 'https://www.youtube.com/watch?v='+url_id
        ydl.download([address])
