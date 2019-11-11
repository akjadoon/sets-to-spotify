import requests
import base64
import os
import json
from urllib.parse import urlencode

from flask import Flask, redirect, request, make_response, jsonify
from flask_cors import CORS

from extract_tracklists import scan_yt
from spotify import get_spotify_tracks, create_spotify_playlist

CLIENT_ID = os.getenv("MTP_SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("MTP_SPOTIFY_CLIENT_SECRET")
STATIC_BASE_URL = os.getenv("MTP_STATIC_BASE_URL")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": STATIC_BASE_URL}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


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
        return "Invalid Authorization code", 400
    
    token = json.loads(res.content)['access_token']
    resp = make_response()
    resp.set_cookie("token", token)
    resp.headers.add('Access-Control-Request-Headers', 'Cookie, Set-Cookie')
    return resp, 200


@app.route('/tracks', methods=['GET'])
def tracks():
    if 'link' in request.args:
        title, track_names = scan_yt(request.args['link'])
        if not track_names:
            return "Could not find a tracklist for your mix", 400
        spotify_tracks = get_spotify_tracks(track_names, request.cookies.get('token'))
        if not spotify_tracks:
            return "Failed to find tracks on spotify", 400
        return jsonify({'video_title': title, 'tracks': [t.serialize() for t in spotify_tracks]}), 200


@app.route('/playlist', methods=['POST'])
def playlist():
    data = request.get_json()
    success = create_spotify_playlist(data['track_ids'], data['video_title'], request.cookies.get('token'))
    if not success:
        return "Failed to create playlits", 400
    return "okay", 201


@app.route('/check_cookie')
def check():
    print("My cookie", request.cookies.get('token'))
    return request.cookies.get('token')

@app.route('/hello')
def hello():
    return "Hello World"


if __name__ == "__main__":
   app.run(host='127.0.0.1', port=5000, debug=True)