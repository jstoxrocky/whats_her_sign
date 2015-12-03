from flask import Flask, request, session, render_template, jsonify, redirect, url_for
import requests
import os
import json
from datetime import datetime, timedelta
import pytz
from pandas import DataFrame

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
    if session.get('name'):

        data = {'fb_auth_token': session['fb_auth_token'],
            'name':session['name'],
            'signed_in': True}
        return render_template('index.html', data=data)
    else:
        data = {'signed_in': False,}

    return render_template('/index.html', data=data)

headers = {
    'app_version': '3',
    'platform': 'ios',
}


zodiacs = [(120, 'Capricorn'), (219, 'Aquarius'), (321, 'Pisces'), (420, 'Aries'), (521, 'Taurus'),
           (621, 'Gemini'), (723, 'Cancer'), (823, 'Leo'), (923, 'Virgo'), (1023, 'Libra'),
           (1122, 'Scorpio'), (1222, 'Sagitarius'), (1231, 'Capricorn')]

def get_zodiac_of_date(date):
    date_number = int("".join((str(date.date().month), '%02d' % date.date().day)))
    for z in zodiacs:
        if date_number < z[0]:
            return z[1]


def auth_token(fb_auth_token):
    h = headers
    h.update({'content-type': 'application/json'})

    fb_user_id = 464891386855067
    req = requests.post(
        'https://api.gotinder.com/auth',
        headers=h,
        data=json.dumps({'facebook_token': fb_auth_token, 'facebook_id': fb_user_id})
    )
    try:
        return req.json()
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

    if session.get('fb_auth_token'):
        data = {'fb_auth_token': session['fb_auth_token'],
                'signed_in': True}
    else:
        data = {'signed_in': False,}
        return jsonify(data)

    fb_auth_token = data['fb_auth_token']

    search_name = request.form['search_name']
    

    try:
        search_name = int(search_name)
        func = ten_most_recent
    except:
        func = hit_tinder_api
    ppl_list = func(fb_auth_token, search_name)
        
    return jsonify({'ppl_list':ppl_list, 'signed_in':data['signed_in']})



@app.route('/get_self_info', methods=["POST"])
def get_self_info():

    return jsonify({'me_list':[session['me']]})



def ago(raw, return_seconds=False):
    if raw:
        gmt = pytz.timezone('GMT')
        eastern = pytz.timezone('US/Eastern')

        dt = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
        dt_gmt = gmt.localize(dt)
        dt_eastern = dt_gmt.astimezone(eastern)

        now_dt = datetime.now()
        now_dt_gmt = gmt.localize(now_dt)
        now_dt_eastern = now_dt_gmt.astimezone(eastern)

        secs_ago = int(now_dt_eastern.strftime("%s")) - int(dt_eastern.strftime("%s"))

        if return_seconds:
            return secs_ago

        if secs_ago > 86400:
            return u'{days} days ago'.format(days=secs_ago / 86400)
        elif secs_ago < 3600:
            return u'{mins} mins ago'.format(mins=secs_ago / 60)
        else:
            return u'{hours} hours ago'.format(hours=secs_ago / 3600)

    return '[unknown]'



def ten_most_recent(token, minutes):

    ppl_list = []
    for data in updates(token):
        if data.get('person'):
            person = data['person']
            ping_str = person['ping_time']
            last_active_at = ago(ping_str, return_seconds=True)
            if last_active_at <= minutes*60:
                current_person = personal_info(person)
                ppl_list.append(current_person)

        if len(ppl_list) >= 10:
            return ppl_list


def personal_info(person):

    name =  person['name']
    bio = person['bio']
    
    bday_str = person['birth_date']
    bday_dt = datetime.strptime(bday_str,"%Y-%m-%dT%H:%M:%S.%fZ")

    ping_str = person['ping_time']
    last_active_at = ago(ping_str)

    age = -(bday_dt - datetime.now()).days/365
    zodiac = get_zodiac_of_date(bday_dt)

    img_list = []
    large_img_list = []
    for img in person['photos']:
        url = img['processedFiles'][-2]['url']
        large_url = img['processedFiles'][0]['url']
        img_list.append(url)
        large_img_list.append(large_url)
        

    current_person  = {'name':name, 
                        'age':age,
                        'sign':zodiac, 
                        'bio':bio,
                        'birthday':str(bday_dt.date()),
                        'img':img_list,
                        'large_img_list':large_img_list,
                        'last_active_at':last_active_at}

    return current_person

def hit_tinder_api(token, search_name):

    ppl_list = []
    for data in updates(token):

        if data.get('person') and search_name.lower() in data.get('person')['name'].lower():

            person = data['person']
            current_person = personal_info(person)

            ppl_list.append(current_person)

    return ppl_list


@app.route('/go_to_login_page')
def go_to_login_page():

    if session.get('fb_auth_token'):
        data = {'fb_auth_token': session['fb_auth_token'],
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

    # fb_id = request.form['fb_id']
    fb_auth_token = request.form['fb_auth_token']
    data = auth_token(fb_auth_token)
    me = data['user']
    me_dict = personal_info(me)

    session['id'] = me['_id']
    session['name'] = me['full_name'].split(None)[0]
    session['me'] = me_dict

    session['fb_auth_token'] = data['token']

    return redirect(url_for('index'))



"""
Logout function
"""
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))






"""
See my account
"""
@app.route('/account')
def my_account():

    # See who is logged in
    data = {'fb_auth_token': session['fb_auth_token'],
            'name':session['name'],
            'signed_in': True}


    return render_template('/account.html', data=data)




"""
See my account
"""
@app.route('/get_matches_over_time')
def get_matches_over_time():
 
    match_dt_arr = []
    for data in updates(session['fb_auth_token']):
        if data.get('person'):
            match_dt_str = data['created_date']
            match_dt = datetime.strptime(match_dt_str,"%Y-%m-%dT%H:%M:%S.%fZ").date()
            match_dt_arr.append(match_dt)

    match_df = DataFrame({'match_dt':match_dt_arr})
    match_df['c'] = 1
    match_gb = match_df.groupby('match_dt').agg(len)
    match_gb = match_gb.sort_index(ascending=True)
    num_days = (match_gb.index.max() - match_gb.index.min()).days
    match_gb = match_gb.reindex([match_gb.index.min() + timedelta(days=i) for i in range(num_days)]).fillna(0)

    x = [str(dt) for dt in match_gb.index.tolist()]

    return jsonify({'x':x, 'y':match_gb['c'].tolist()})




if __name__ == '__main__':
    app.run()
