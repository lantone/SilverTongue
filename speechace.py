import os
import json
import requests
import datetime

api_key =  os.environ['SPEECHACE_API_KEY']

def query(input_audio_file, input_text):

    url = 'https://api.speechace.co/api/scoring/text/v0.1/json?key='+api_key+'&user_id=002'
    files = [
        ('user_audio_file', open(input_audio_file, 'rb')),
    ]
    data = [
        ('text', input_text),
        ('dialect', 'general_american'),
        ('user_id', '1234')
    ]
    results = requests.post(url, files=files, data=data).text
    try:
        return json.loads(results)
    except:
        return {}

def create_word_list(data):

    info = data['text_score']
    word_data = info['word_score_list']

    # sentence -> word -> syllable -> phone
    sentence = []


    for word_index,word in enumerate(word_data):
        word_entry = {}
        syllable_score_list = word['syllable_score_list']
        phone_score_list = word['phone_score_list']

        # populate word info
        word_entry['index'] = word_index
        word_entry['text'] = word['word']
        word_entry['quality'] = word['quality_score']
        word_entry['start'] = syllable_score_list[0]['extent'][0]
        word_entry['end']   = syllable_score_list[-1]['extent'][1]
        
        word_entry['syllables'] = []
        for syl_index, syl in enumerate(syllable_score_list):
            syl_entry = {}

            # populate syllable info
            syl_entry['index'] = syl_index
            syl_entry['text'] = syl['letters']
            syl_entry['quality'] = syl['quality_score']
            syl_entry['start'] = syl['extent'][0]
            syl_entry['end']   = syl['extent'][1]

            
            # (protect against missing data)
            if 'intonation' in syl:
                syl_entry['intonation'] = syl['intonation'][1]
            else:
                syl_entry['intonation'] = None

            if 'pitch_range' in syl:
                syl_entry['pitch_low'] = syl['pitch_range'][1]
                syl_entry['pitch_high'] = syl['pitch_range'][0]
            else:
                syl_entry['pitch_low'] = 0
                syl_entry['pitch_high'] = 0


            syl_entry['phones'] = []
            
            for phone_index, phone in enumerate(phone_score_list):
                phone_entry = {}

                phone_start = phone['extent'][0]
                phone_end = phone['extent'][1]

                # this phone belongs to an earlier syllable, go to next one
                if phone_start < syl_entry['start']:
                    continue
                # this phone belongs to a later syllable, we've got all we need for the current syllable
                if phone_start >= syl_entry['end']:
                    break

                # add phone info
                phone_entry['index'] = phone_index
                phone_entry['text'] = phone['phone']
                phone_entry['quality'] = phone['quality_score']
                phone_entry['start'] = phone_start
                phone_entry['end'] = phone_end

                syl_entry['phones'].append(phone_entry)
            word_entry['syllables'].append(syl_entry)
        sentence.append(word_entry)

    return sentence


def activate_speechace(subs_for_speechace, audio_for_speechace, max_calls = 999, verbose = False):
    # API calls!!!
    data_for_speechace = zip(audio_for_speechace, subs_for_speechace)
    word_list = []
    bad_chunks = []
    unknown_word_list = []
    if verbose:
        print len(data_for_speechace)
    start_time = datetime.datetime.now()
    last_time = start_time
    total_time = 0
    for i,chunk in enumerate(data_for_speechace):
        if i >= max_calls:
            break
        if verbose:
            print "call #" + str(i)
        speechace_data = query(chunk[0],chunk[1])
        if 'status' not in speechace_data:
            if verbose:
                print speechace_data
                print "NO GO #1"
            bad_chunks.append(i)
            continue
        if speechace_data['status'] == 'success':
            word_list.extend(create_word_list(speechace_data))
        else:
            if speechace_data['short_message'] == 'error_unknown_words':
                unknown_words = speechace_data['detail_message'].encode('utf-8').split(':')[-1].split(',')
                if verbose:
                    print "found unknown_words!",unknown_words

                new_text = chunk[1]
                for unknown_word in unknown_words:
                    unknown_word_list.append(unknown_word.strip())
                    if unknown_word.strip() == 'gon':
                        new_text = new_text.replace('gonna','')
                    else:
                        new_text = new_text.replace(unknown_word,'')
                    
                speechace_data = query(chunk[0],new_text)
                if 'status' not in speechace_data:
                    if verbose:
                        print "NO GO #2"
                    bad_chunks.append(i)
                    continue
                if speechace_data['status'] == 'success':
                    word_list.extend(create_word_list(speechace_data))
                else:
                    if verbose:
                        print speechace_data['short_message']
                        print speechace_data['detail_message']
                        print "NO GO #3"
                    bad_chunks.append(i)
            else:
                if verbose:
                    print speechace_data['short_message']
                    print "NO GO #4"
                bad_chunks.append(i)

        current_time = datetime.datetime.now()        
        if verbose:
            print "took", (current_time-last_time).total_seconds()
            print "total time is", (current_time-start_time).total_seconds()
            print
        last_time = current_time
    return word_list, bad_chunks, unknown_word_list
