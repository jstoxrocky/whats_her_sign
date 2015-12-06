import requests
import json
import time

TINDER_TO_FB_CLIENT_ID = 464891386855067
HEADERS = {
    'app_version': '3',
    'platform': 'ios',
}


"""
Authenticate with Tinder
"""
def auth_token(fb_auth_token):
    h = HEADERS
    h.update({'content-type': 'application/json'})
    req = requests.post(
        'https://api.gotinder.com/auth',
        headers=h,
        data=json.dumps({'facebook_token': fb_auth_token, 'facebook_id': TINDER_TO_FB_CLIENT_ID})
    )
    try:
        return req.json()
    except:
        return None


"""
Get ALL updates 
"""
def updates(auth_token):
    h = HEADERS
    h.update({'X-Auth-Token': auth_token, 'Content-Type': 'application/json'})
    r = requests.post('https://api.gotinder.com/updates', headers=h, data=json.dumps({"last_activity_date":"2012-01-01T03:48:29.002Z"}))
    
    if r.status_code == 401 or r.status_code == 504:
        raise Exception('Invalid token. Try getting a fresh one.')
        print r.content

    for result in r.json()['matches']:
        yield result


"""
Get User info from their ID
"""
def search_by_user_id(auth_token, _id):
    
    h = HEADERS
    h.update({'X-Auth-Token': auth_token})
    r = requests.get('https://api.gotinder.com/user/%s' %(_id), headers=h)

    if r.status_code == 401 or r.status_code == 504:
        raise Exception('Invalid token. Try getting a fresh one.')
        print r.content

    if r.status_code == 429:        
        time.sleep(10)
        r = requests.get('https://api.gotinder.com/user/%s' %(_id), headers=h)
        print r.status_code


    return r.json()['results']


# """
# Superlike by ID
# """
# def superlike(_id):

#     try:
#         u = 'https://api.gotinder.com/like/%s/super' % _id
#         d = requests.post(u, headers=headers, timeout=10.0)
#         d.text
#     except KeyError:
#         pass
#     else:
#         print d.json()
#         return d.json()


"""
Like by ID
"""
def like_by_id(_id):

    url = 'https://api.gotinder.com/like/%s' % _id
    response = requests.get(url, headers=HEADERS, timeout=10.0)

    print response.status_code
    if response.status_code != 200:
        raise Exception('Some kind of error')
        print r.content

    return response.json()#['result']


"""
Superlike by ID
"""
def superlike_by_id(_id):

    url = 'https://api.gotinder.com/like/%s/super' % _id
    response = requests.get(url, headers=HEADERS, timeout=10.0)

    print response.status_code
    if response.status_code != 200:
        raise Exception('Some kind of error')
        print r.content

    return response.json()#['result']


"""
Pass by ID
"""
def pass_by_id(_id):

    url = 'https://api.gotinder.com/pass/%s' % _id
    response = requests.get(url, headers=HEADERS, timeout=10.0)

    print response.status_code
    if response.status_code != 200:
        raise Exception('Some kind of error')
        print r.content

    return response.json()#['result']


"""
Get Recommendations
"""
def recommendations(auth_token):
    h = HEADERS
    h.update({'X-Auth-Token': auth_token})
    r = requests.get('https://api.gotinder.com/user/recs', headers=h)
    if r.status_code == 401 or r.status_code == 504:
        raise Exception('Invalid code')
        print r.content

    if not 'results' in r.json():
        print r.json()

    return r.json()['results'][0]