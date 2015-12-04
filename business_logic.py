from tinder_api import *
from datetime import datetime, timedelta
import pytz
from pandas import DataFrame, rolling_mean

zodiacs = [(120, 'Capricorn'), (219, 'Aquarius'), (321, 'Pisces'), (420, 'Aries'), (521, 'Taurus'),
           (621, 'Gemini'), (723, 'Cancer'), (823, 'Leo'), (923, 'Virgo'), (1023, 'Libra'),
           (1122, 'Scorpio'), (1222, 'Sagitarius'), (1231, 'Capricorn')]

def get_zodiac_of_date(date):
    date_number = int("".join((str(date.date().month), '%02d' % date.date().day)))
    for z in zodiacs:
        if date_number < z[0]:
            return z[1]


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
    _id = person['_id']
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
                        '_id':_id,
                        'age':age,
                        'sign':zodiac, 
                        'bio':bio,
                        'birthday':str(bday_dt.date()),
                        'img':img_list,
                        'large_img_list':large_img_list,
                        'last_active_at':last_active_at}

    return current_person

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def query_updates(token, search_name):

    ppl_list = []
    # search by id 
    if has_numbers(search_name):
        data = search_by_user_id(token, search_name)
        current_person = personal_info(data)
        ppl_list.append(current_person)
        new = True
    # search by name 
    else:
        for data in updates(token):
            if data.get('person') and search_name.lower() in data.get('person')['name'].lower():
                person = data['person']
                current_person = personal_info(person)
                ppl_list.append(current_person)
        new = False
    return ppl_list, new


def calc_match_volume(token):
    match_dt_arr = []
    for data in updates(token):
        if data.get('person'):
            match_dt_str = data['created_date']
            match_dt = datetime.strptime(match_dt_str,"%Y-%m-%dT%H:%M:%S.%fZ").date()
            match_dt_arr.append(match_dt)

    x, y = dt_to_count_by_dt(match_dt_arr, periods_to_roll=7)   
    return x, y


def calc_msg_volume(token, self_id):
    sent_msg = []
    recieved_msg = []
    for data in updates(token):
        for msg in data['messages']:
            
            msg_dt = datetime.strptime(msg['sent_date'],"%Y-%m-%dT%H:%M:%S.%fZ").date()
            if msg['from'] == self_id:
                sent_msg.append(msg_dt)
            else:
                recieved_msg.append(msg_dt)

    x, sent = dt_to_count_by_dt(sent_msg, periods_to_roll=7) 
    x, recieved = dt_to_count_by_dt(recieved_msg, periods_to_roll=7) 
    return x, sent, recieved


def dt_to_count_by_dt(arr, periods_to_roll=7):

    df = DataFrame({'arr_name':arr})
    df['c'] = 1
    gb = df.groupby('arr_name').agg(len)
    gb = gb.sort_index(ascending=True)
    num_days = (gb.index.max() - gb.index.min()).days
    gb = gb.reindex([gb.index.min() + timedelta(days=i) for i in range(num_days)]).fillna(0)

    x = [str(dt) for dt in gb.index.tolist()]
    y = rolling_mean(gb.c,periods_to_roll,min_periods=0).dropna().tolist()

    return x, y



def get_next_recommendation(token):
    ppl_list = []
    data = recommendations(token)
    current_person = personal_info(data)
    ppl_list.append(current_person)
    return ppl_list