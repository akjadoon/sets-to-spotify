import requests
import base64
import os
import json
import datetime
import base64
from urllib.parse import urlencode

import pymongo
import dns
from flask import Flask, redirect, request, make_response, jsonify
from flask_cors import CORS

from extract_tracklists import scan_yt
from spotify import get_spotify_tracks, create_spotify_playlist

CLIENT_ID = os.getenv("MTP_SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("MTP_SPOTIFY_CLIENT_SECRET")
STATIC_BASE_URL = os.getenv("MTP_STATIC_BASE_URL")
DB_CONNECTION_STRING = os.getenv("MTP_DB_CONNECTION_STRING")
db_client = pymongo.MongoClient(DB_CONNECTION_STRING)
db = db_client.s2sdb

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": STATIC_BASE_URL}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


def refresh_token_decorator(f):
    def refresh_token_wrapper():
        access_token = request.cookies.get("token")
        resp = make_response()
        if not access_token:
            body = {
                "grant_type": "refresh_token",
                "refresh_token": request.cookies.get("refresh_token")
            }
            headers = {
                "Authorization": "Basic " + str(base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")), "utf-8")
            }
            print(body)
            print
            res = requests.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
            if res.status_code != 200:
                return "Invalid Authorization code", res.status_code
    
            content = json.loads(res.content)
            access_token = content['access_token']
            resp.set_cookie("token", content['access_token'], max_age=3600)
            resp.headers.add('Access-Control-Request-Headers', 'Cookie, Set-Cookie')
        return f(access_token, resp)
    return refresh_token_wrapper


@app.route('/authorize')
def auth():
    param_string = urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": f"{STATIC_BASE_URL}/logged_in",
        "scope": "user-read-private playlist-modify-public",
        "response_type": "code"
    })
    response = jsonify({"redirect_url": f"https://accounts.spotify.com/authorize?{param_string}"})
    return response


@app.route('/token')
def token():
    if not 'code' in request.args:
        return "No Spotify Authorization code recieved from client", 400

    body = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": request.args['code'],
        "redirect_uri": f"{STATIC_BASE_URL}/logged_in" # not redirected, only for verification
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=body)
    if res.status_code != 200:
        print(res.content)
        return "Invalid Authorization code", 400
    
    content = json.loads(res.content)
    resp = make_response()
    resp.set_cookie("token", content['access_token'], max_age=3600)
    resp.set_cookie("refresh_token", content['refresh_token'])
    resp.headers.add('Access-Control-Request-Headers', 'Cookie, Set-Cookie')
    return resp, 200


@app.route('/tracks', methods=['GET'])
@refresh_token_decorator
def tracks(access_token, resp):
    logs = {"at": datetime.datetime.now()}
    if 'link' in request.args:
        logs['link'] = request.args['link']
        title, track_names = scan_yt(request.args['link'])
        logs['yt_title'] = title
        if not track_names:
            return modify_response(resp, "Could not find a tracklist for your mix", 400, logs)
        logs['yt_tracks'] = {str(i): t for i, t in enumerate(track_names)}       
        spotify_tracks = get_spotify_tracks(track_names, access_token)
        if not spotify_tracks:
            return modify_response(resp, "Failed to find tracks on spotify", 400, logs)
        logs['spotify_tracks'] = {
            str(i): {
                "spotify_id": track.id,
                "track": track.name,
                "artists": {
                    str(j): artist 
                    for j, artist in enumerate(track.artists)}
                }
            for i, track in enumerate(spotify_tracks)}              
        return modify_response(resp,
                               json.dumps({'video_title': title, 'tracks': [t.serialize() for t in spotify_tracks]}),
                               200,
                               logs,
                               mimetype='application/json')
    return modify_response(resp, "No link in request", 400, logs)


@app.route('/playlist', methods=['POST'])
def playlist():
    data = request.get_json()
    success = create_spotify_playlist(data['track_ids'], data['video_title'], request.cookies.get('token'))
    if not success:
        return "Failed to create playlist", 400
    return "okay", 201


@app.route('/hello')
def hello():
    return "Hello World"


def modify_response(response, data, status_code, logs, mimetype=None):
    if status_code != 200:
        logs["failure_message"] = data
    print(logs)
    db["get_playlist_logs"].insert_one(logs)

    response.data = data
    response.status_code = status_code
    if mimetype:
        response.mimetype = mimetype
    return response


if __name__ == "__main__":
   app.run(host='127.0.0.1', port=5000, debug=True)