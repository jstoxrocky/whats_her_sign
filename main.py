from flask import Flask, request, session, render_template, jsonify, redirect, url_for
import requests
import os



# Custom
from business_logic import *

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
    if session.get('name'):
        data = {'fb_auth_token': session['fb_auth_token'],
            'name':session['name'],
            'signed_in': True}
        return render_template('index.html', data=data)
    else:
        data = {'signed_in': False,}
    return render_template('/index.html', data=data)


"""
Redirect to log in page
"""
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
Redirect to explore page
"""
@app.route('/explore')
def explore():

    if session.get('name'):
        data = {'fb_auth_token': session['fb_auth_token'],
            'name':session['name'],
            'signed_in': True}
    else:
        data = {'signed_in': False,}

    return render_template('/explore.html', data=data)



#---------------------------------------



"""
Get info by main search
"""
@app.route('/get_info', methods=["POST"])
def get_info():

    signed_in = True if session.get('name') else False
    fb_auth_token = session['fb_auth_token']
    search_name = request.form['search_name']
    ppl_list, new = query_updates(fb_auth_token, search_name)
        
    return jsonify({'ppl_list':ppl_list[::-1], 'signed_in':signed_in, 'new':new})


"""
Get your own profiles info
"""
@app.route('/get_self_info', methods=["POST"])
def get_self_info():
    return jsonify({'me_list':[session['me']]})


"""
Get match volume
"""
@app.route('/get_matches_over_time')
def get_matches_over_time():
    x, y = calc_match_volume(session['fb_auth_token']) 
    return jsonify({'x':x, 'y':y})


"""
Get message volume
"""
@app.route('/get_msg_over_time')
def get_msg_over_time():
    x, sent, recieved = calc_msg_volume(session['fb_auth_token'], session['id'])
    return jsonify({'x':x, 'sent':sent, 'recieved':recieved})

"""
Get recomendations
"""
@app.route('/get_explore_info', methods=["POST"])
def get_explore_info():
    ppl_list = get_next_recommendation(session['fb_auth_token'])
    return jsonify({'ppl_list':ppl_list})

"""
Like
"""
@app.route('/like', methods=["POST"])
def like():
    
    _id = request.form['_id']
    result = like_by_id(_id)
    print result

    return jsonify(result)







if __name__ == '__main__':
    app.run()
