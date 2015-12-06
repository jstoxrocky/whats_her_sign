from flask import Flask, request, session, render_template, jsonify, redirect, url_for
import requests
import os
from pandas import DataFrame


# Custom
from business_logic import *
df = DataFrame

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


"""
Redirect to explore page
"""
@app.route('/chop_n_screw')
def chop_n_screw():

    if session.get('name'):
        data = {'fb_auth_token': session['fb_auth_token'],
            'name':session['name'],
            'signed_in': True}
    else:
        data = {'signed_in': False,}

    return render_template('/chop_n_screw.html', data=data)

#---------------------------------------



"""
Get info by main search
"""
@app.route('/get_info', methods=["POST"])
def get_info():

    signed_in = True if session.get('name') else False
    if not signed_in:
        return jsonify({'signed_in':signed_in})

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

    signed_in = True if session.get('name') else False
    if not signed_in:
        return jsonify({'signed_in':signed_in})
    ppl_list = get_next_recommendation(session['fb_auth_token'])
    return jsonify({'ppl_list':ppl_list, 'signed_in':signed_in})


"""
Like
"""
@app.route('/like', methods=["POST"])
def like():
    _id = request.form['_id']
    result = like_by_id(_id)
    self_main_pic = session['me']['img'][0]
    print result.update({'self_main_pic': self_main_pic})
    return jsonify(result)


"""
Pass
"""
@app.route('/_pass', methods=["POST"])
def _pass():
    _id = request.form['_id']
    result = pass_by_id(_id)
    return jsonify(result)


"""
Superike
"""
@app.route('/superlike', methods=["POST"])
def superlike():
    _id = request.form['_id']
    result = superlike_by_id(_id)
    self_main_pic = session['me']['img'][0]
    print result.update({'self_main_pic': self_main_pic})
    return jsonify(result)










"""
Load Chop n Screw Data SOMETHIGN WEIRD HAPPENING WITH SESSION. NOT SAVING DATA. TOO BIG FOR COOKIE?
"""
@app.route('/load_chop_n_screw_data')
def load_chop_n_screw_data():
    global df
    df = get_data_to_chop_n_screw(session['fb_auth_token'])
    return jsonify({'msg':'df loaded'})


"""
Sort the Data
"""
@app.route('/sort_the_data', methods=["POST"])
def sort_the_data():

    #age, last time messaged, match date, distance

    # df = get_data_to_chop_n_screw(session['fb_auth_token'])
    global df

    data = DataFrame(df)
    age = request.form['age']
    # distance_mi = request.form['distance_mi']
    msg = request.form['msg']
    _zodiac = request.form['zodiac']


    df_array = [data]
    label_array = [[]]
    # if distance_mi:
    #     df_array, label_array = distance_gele(df_array, label_array, distance_mi)
    if age:
        df_array, label_array = age_gele(df_array, label_array, age)
    if int(msg) == 1:
        df_array, label_array = msg_yes_no(df_array, label_array)
    if int(_zodiac) == 1:
        df_array, label_array = sort_by_zodiac(df_array, label_array)

    groups = [df['dp'].tolist() for df in df_array]
    _ids = [df['_id'].tolist() for df in df_array]

    return jsonify({'groups':groups, 'labels':label_array, '_ids':_ids})



def msg_yes_no(df_array, label_array):
    new_df_array = []
    new_lbl_array = []
    for df, lbl in zip(df_array, label_array):

        a_arr = [l for l in lbl]
        a_arr.append("Never Messaged")
        b_arr = [l for l in lbl]
        b_arr.append("At least one message")
        new_lbl_array.append(a_arr)
        new_lbl_array.append(b_arr)

        new_df_array.append(df[df['any_msg']==0])
        new_df_array.append(df[df['any_msg']==1])
    return new_df_array, new_lbl_array

def age_gele(df_array, label_array, age):

    new_df_array = []
    new_lbl_array = []
    for df, lbl in zip(df_array, label_array):
        age = int(age)

        a_arr = [l for l in lbl]
        a_arr.append("At least %i years old" %age)
        b_arr = [l for l in lbl]
        b_arr.append("Under %i years old" %age)
        new_lbl_array.append(a_arr)
        new_lbl_array.append(b_arr)

        new_df_array.append(df[df['age']>=age])
        new_df_array.append(df[df['age']<age])
    return new_df_array, new_lbl_array


def distance_gele(df_array, label_array, distance_mi):

    new_df_array = []
    new_lbl_array = []
    for df, lbl in zip(df_array, label_array):
        distance_mi = int(distance_mi)

        a_arr = [l for l in lbl]
        a_arr.append("Above %i miles" %distance_mi)
        b_arr = [l for l in lbl]
        b_arr.append("Within %i miles" %distance_mi)
        new_lbl_array.append(a_arr)
        new_lbl_array.append(b_arr)

        new_df_array.append(df[df['distance_mi']>distance_mi])
        new_df_array.append(df[df['distance_mi']<=distance_mi])
    return new_df_array, new_lbl_array




def sort_by_zodiac(df_array, label_array):

    new_df_array = []
    new_lbl_array = []
    for df, lbl in zip(df_array, label_array):

        for sign in zodiacs:
            a_arr = [l for l in lbl]
            a_arr.append(sign[1])
            new_lbl_array.append(a_arr)
            new_df_array.append(df[df['sign']==sign[1]])

    return new_df_array, new_lbl_array





if __name__ == '__main__':
    app.run()
