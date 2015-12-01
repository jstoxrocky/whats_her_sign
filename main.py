from flask import Flask, request, session, render_template, jsonify, redirect, url_for
import requests
import os
import json
from datetime import datetime
import pytz

# Constants
APP_SECRET = os.environ.get('tinder_app_secret')

# Flask stuff
app = Flask(__name__)
app.debug = True
app.secret_key = APP_SECRET


"""
Function called when homepage requested
"""
@app.route('/')
@app.route('/index.html')
def index():

    # Get log in info if user logged into Venmo
    if session.get('fb_id'):
        data = {'fb_id': session['fb_id'],
                'fb_auth_token': session['fb_auth_token'],
                'signed_in': True}
        return render_template('index.html', data=data)
    else:
        data = {'signed_in': False,}

    return render_template('/index.html', data=data)

headers = {
    'app_version': '3',
    'platform': 'ios',
}



# https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token



zodiacs = [(120, 'Capricorn'), (219, 'Aquarius'), (321, 'Pisces'), (420, 'Aries'), (521, 'Taurus'),
           (621, 'Gemini'), (723, 'Cancer'), (823, 'Leo'), (923, 'Virgo'), (1023, 'Libra'),
           (1122, 'Scorpio'), (1222, 'Sagitarius'), (1231, 'Capricorn')]

def get_zodiac_of_date(date):
    date_number = int("".join((str(date.date().month), '%02d' % date.date().day)))
    for z in zodiacs:
        if date_number < z[0]:
            return z[1]


def auth_token(fb_auth_token, fb_user_id):
    h = headers
    h.update({'content-type': 'application/json'})

    fb_user_id = 464891386855067
    req = requests.post(
        'https://api.gotinder.com/auth',
        headers=h,
        data=json.dumps({'facebook_token': fb_auth_token, 'facebook_id': fb_user_id})
    )
    try:
        return req.json()['token']
    except:
        return None


def updates(auth_token):
    h = headers
    h.update({'X-Auth-Token': auth_token, 'Content-Type': 'application/json'})
    r = requests.post('https://api.gotinder.com/updates', headers=h, data=json.dumps({"last_activity_date":"2012-01-01T03:48:29.002Z"}))
    
    if r.status_code == 401 or r.status_code == 504:
        raise Exception('Invalid code')
        print r.content

    for result in r.json()['matches']:
        yield result


@app.route('/get_info', methods=["POST"])
def get_info():

    if session.get('fb_id'):
        data = {'fb_id': session['fb_id'],
                'fb_auth_token': session['fb_auth_token'],
                'signed_in': True}
    else:
        data = {'signed_in': False,}

    fb_auth_token = data['fb_auth_token']
    fb_id = data['fb_id']

    search_name = request.form['search_name']
    token = auth_token(fb_auth_token, fb_id)

    
    ppl_list = hit_tinder_api(token, search_name)
        
    return jsonify({'ppl_list':ppl_list})




def ago(raw):
    if raw:
        gmt = pytz.timezone('GMT')
        eastern = pytz.timezone('US/Eastern')

        dt = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
        dt_gmt = gmt.localize(dt)
        dt_eastern = dt_gmt.astimezone(eastern)

        now_dt = datetime.now()

        secs_ago = int(now_dt.strftime("%s")) - int(dt_eastern.strftime("%s"))

        if secs_ago > 86400:
            return u'{days} days ago'.format(days=secs_ago / 86400)
        elif secs_ago < 3600:
            return u'{mins} mins ago'.format(mins=secs_ago / 60)
        else:
            return u'{hours} hours ago'.format(hours=secs_ago / 3600)

    return '[unknown]'



def hit_tinder_api(token, search_name):

    ppl_list = []
    for data in updates(token):

        if data.get('person') and search_name.lower() in data.get('person')['name'].lower():

            person = data['person']
            name =  person['name']
            bio = person['bio']
            
            bday_str = person['birth_date']
            bday_dt = datetime.strptime(bday_str,"%Y-%m-%dT%H:%M:%S.%fZ")

            ping_str = person['ping_time']
            last_active_at = ago(ping_str)

            age = -(bday_dt - datetime.now()).days/365
            zodiac = get_zodiac_of_date(bday_dt)

            img_list = []
            for img in person['photos']:
                url = img['processedFiles'][-2]['url']
                img_list.append(url)
                

            current_person  = {'name':name, 
                                'age':age,
                                'sign':zodiac, 
                                'bio':bio,
                                'birthday':str(bday_dt.date()),
                                'img':img_list,
                                'last_active_at':last_active_at}

            ppl_list.append(current_person)

    return ppl_list


@app.route('/go_to_login_page')
def go_to_login_page():

    if session.get('fb_id'):
        data = {'fb_id': session['fb_id'],
                'fb_auth_token': session['fb_auth_token'],
                'signed_in': True}
        return render_template('index.html', data=data)
    else:
        data = {'signed_in': False,}

    return render_template('/login.html', data=data)


"""
Function called after authentication
"""
@app.route('/login', methods=["POST"])
def login():

    fb_id = request.form['fb_id']
    fb_auth_token = request.form['fb_auth_token']

    session['fb_id'] = fb_id
    session['fb_auth_token'] = fb_auth_token

    data = {'fb_id': session['fb_id'],
            'fb_auth_token': session['fb_auth_token'],
            'signed_in': True}

    return redirect(url_for('index'))



"""
Logout function
"""
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
