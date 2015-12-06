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
                distance_mi = search_by_user_id(token, current_person['_id'])['distance_mi']
                current_person['distance_mi'] = distance_mi
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




def get_data_to_chop_n_screw(token):
    ppl_list = []
    for data in updates(token):
        if data.get('person'):
            person = data['person']
            current_person = personal_info(person)
            # distance_mi = search_by_user_id(token, current_person['_id'])['distance_mi']
            # current_person['distance_mi'] = distance_mi
            current_person['any_msg'] = 0 if len(data['messages']) <= 0 else 1
            current_person['dp'] = current_person['img'][0]
            ppl_list.append(current_person)

    # ppl_list = [{'bio': u"i'm a pretty interesting person", 'sign': 'Pisces', 'birthday': '1995-03-18', 'large_img_list': [u'http://images.gotinder.com/5380ce32f5c620eb1932245c/640x640_41bb8eef-356c-4a2b-8fb0-5b896ee4f3c4.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/640x640_245031e2-3a82-4f87-9dd5-275e017f3649.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/640x640_2bba1f02-0467-4bb0-889f-9fa20317422d.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/640x640_fb680e2f-a819-4f1a-8cab-f33550556d68.jpg'], 'dp': u'http://images.gotinder.com/5380ce32f5c620eb1932245c/172x172_41bb8eef-356c-4a2b-8fb0-5b896ee4f3c4.jpg', 'any_msg': 1, 'last_active_at': u'556 days ago', 'name': u'Taylor', 'img': [u'http://images.gotinder.com/5380ce32f5c620eb1932245c/172x172_41bb8eef-356c-4a2b-8fb0-5b896ee4f3c4.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/172x172_245031e2-3a82-4f87-9dd5-275e017f3649.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/172x172_2bba1f02-0467-4bb0-889f-9fa20317422d.jpg', u'http://images.gotinder.com/5380ce32f5c620eb1932245c/172x172_fb680e2f-a819-4f1a-8cab-f33550556d68.jpg'], 'age': 20, '_id': u'5380ce32f5c620eb1932245c'}, {'bio': u'Oddball ', 'sign': 'Virgo', 'birthday': '1989-08-25', 'large_img_list': [u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_dcbbc704-da48-43b3-852a-3bcf4132e29a.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_ff5dd09f-2f32-4559-8465-6dce274e79e3.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_07fe610e-1fd1-44f6-8b9f-462a4ce87fee.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_4b0fcd9e-da64-4590-ad23-bfffc04f0b12.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_0dc80fc9-6234-4d8d-af92-33bbaaa074ff.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/640x640_1eead3d3-642e-463b-93ab-87c1e4a61b90.jpg'], 'dp': u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_dcbbc704-da48-43b3-852a-3bcf4132e29a.jpg', 'any_msg': 1, 'last_active_at': u'11 hours ago', 'name': u'Sophie', 'img': [u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_dcbbc704-da48-43b3-852a-3bcf4132e29a.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_ff5dd09f-2f32-4559-8465-6dce274e79e3.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_07fe610e-1fd1-44f6-8b9f-462a4ce87fee.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_4b0fcd9e-da64-4590-ad23-bfffc04f0b12.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_0dc80fc9-6234-4d8d-af92-33bbaaa074ff.jpg', u'http://images.gotinder.com/51526f09ebf72c8e1500002a/172x172_1eead3d3-642e-463b-93ab-87c1e4a61b90.jpg'], 'age': 26, '_id': u'51526f09ebf72c8e1500002a'}, {'bio': u"I've made a huge mistake. \n", 'sign': 'Libra', 'birthday': '1989-10-08', 'large_img_list': [u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_4a05f0cb-117d-4b64-b291-99bc2ab4ee96.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_e2b37011-eb24-406c-830e-d76ec330e896.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_8293d8ab-d0e9-4c53-9fd4-a43af21e7eed.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_pct_0_80.249984_480_480_ec610ad9-a544-435b-9d98-0c0ef8141048.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_eb647ff0-4375-45b4-8dd2-fbebcc465c9f.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/640x640_cc65d530-8b7a-4dc4-a0e9-d4bafbdd717a.jpg'], 'dp': u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_4a05f0cb-117d-4b64-b291-99bc2ab4ee96.jpg', 'any_msg': 1, 'last_active_at': u'14 days ago', 'name': u'Abby', 'img': [u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_4a05f0cb-117d-4b64-b291-99bc2ab4ee96.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_e2b37011-eb24-406c-830e-d76ec330e896.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_8293d8ab-d0e9-4c53-9fd4-a43af21e7eed.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_pct_0_80.249984_480_480_ec610ad9-a544-435b-9d98-0c0ef8141048.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_eb647ff0-4375-45b4-8dd2-fbebcc465c9f.jpg', u'http://images.gotinder.com/51cf8ecf86eed65101000006/172x172_cc65d530-8b7a-4dc4-a0e9-d4bafbdd717a.jpg'], 'age': 26, '_id': u'51cf8ecf86eed65101000006'}, {'bio': u'Living in Geneva after nine years in New York. Studying, working, and trying to learn French.\n\nEN/SP/PT', 'sign': 'Scorpio', 'birthday': '1987-11-14', 'large_img_list': [u'http://images.gotinder.com/53827820a08836617baba78f/640x640_966bce44-4bda-4276-916b-54a1d3b62f29.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/640x640_7bb2bc0e-f8fc-4ce4-81a5-498432790445.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/640x640_59d39c47-31e5-40cf-b810-02604639e056.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/640x640_16eddc45-a680-46ca-875a-42840c0cb4bc.jpg'], 'dp': u'http://images.gotinder.com/53827820a08836617baba78f/172x172_966bce44-4bda-4276-916b-54a1d3b62f29.jpg', 'any_msg': 1, 'last_active_at': u'56 days ago', 'name': u'Kelly', 'img': [u'http://images.gotinder.com/53827820a08836617baba78f/172x172_966bce44-4bda-4276-916b-54a1d3b62f29.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/172x172_7bb2bc0e-f8fc-4ce4-81a5-498432790445.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/172x172_59d39c47-31e5-40cf-b810-02604639e056.jpg', u'http://images.gotinder.com/53827820a08836617baba78f/172x172_16eddc45-a680-46ca-875a-42840c0cb4bc.jpg'], 'age': 28, '_id': u'53827820a08836617baba78f'}, {'bio': u'', 'sign': 'Pisces', 'birthday': '1990-03-08', 'large_img_list': [u'http://images.gotinder.com/53474f2b74f3302a55002def/640x640_bc635665-cc8f-4b0f-877a-9709c8e41892.jpg', u'http://images.gotinder.com/53474f2b74f3302a55002def/640x640_04e2f52e-d2d8-4db7-943d-44552b59686b.jpg', u'http://images.gotinder.com/53474f2b74f3302a55002def/640x640_fdc7ab40-a0e8-4500-8695-896b60a01aea.jpg'], 'dp': u'http://images.gotinder.com/53474f2b74f3302a55002def/172x172_bc635665-cc8f-4b0f-877a-9709c8e41892.jpg', 'any_msg': 1, 'last_active_at': u'153 days ago', 'name': u'Margaret', 'img': [u'http://images.gotinder.com/53474f2b74f3302a55002def/172x172_bc635665-cc8f-4b0f-877a-9709c8e41892.jpg', u'http://images.gotinder.com/53474f2b74f3302a55002def/172x172_04e2f52e-d2d8-4db7-943d-44552b59686b.jpg', u'http://images.gotinder.com/53474f2b74f3302a55002def/172x172_fdc7ab40-a0e8-4500-8695-896b60a01aea.jpg'], 'age': 25, '_id': u'53474f2b74f3302a55002def'}]

    return ppl_list
