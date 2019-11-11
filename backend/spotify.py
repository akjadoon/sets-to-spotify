import requests
import json
import logging
from enum import Enum
from typing import List


logging.basicConfig(level=logging.INFO)

FAILURE = "Failure"
SUCCESS = "Success"

HEADERS = {
    "Accept": "application/json", 
    "Content-Type": "application/json", 
    "Authorization": ""
}


class SpotifyTrack:
    def __init__(self, _id:str, name: str, artists: List[str]):
        self.id = _id
        self.name = name
        self.artists = artists

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "artists": self.artists
        }


def get_spotify_tracks(names, token):
    HEADERS['Authorization'] = "Bearer " + token
    if not isinstance(names, List):
        names = [names]
    tracks = []
    for name in names:
        param_str = name.replace("-", "").replace(" ", "%20")
        url = f"https://api.spotify.com/v1/search?q={param_str}&type=track"
        try:
            res = requests.get(url, headers=HEADERS)
            info = json.loads(res.content)['tracks']['items'][0]
            artists = [artist['name'] for artist in info['artists']]
            tracks.append(SpotifyTrack(info['id'], info['name'], artists))
            logging.info(f"Matched {name} to song:{info['name']}, artists: {','.join(artists)}")
        except Exception as e:
            logging.error(f"Song: {name} not found, {repr(e)}")
    return tracks


def create_playlist(user_id, name):
    data = {
        "name": name,
        "public": True,
        "description": ""
    }
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    res = requests.post(url, headers=HEADERS, json=data)
    try:
        return json.loads(res.content)['id']
    except Exception as e:
        logging.error(f"Failed to Create Playlist, {e}")
        return FAILURE


def get_user_id():
    res = requests.get("https://api.spotify.com/v1/me", headers=HEADERS)
    try: 
        return json.loads(res.content)['id']
    except Exception as e:
        logging.error(f"Failed to get spotify user id, {e}")
        return FAILURE


def add_tracks(playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    data = {
        "uris": [f"spotify:track:{track_id}" for track_id in track_ids]
    }
    res = requests.post(url, headers=HEADERS, json=data)
    if res.status_code != 201:
        logging.error(f"Adding tracks to playlist id: {playlist_id} failed, HTTP Status Code {res.status_code}")
        return False
    return True


def create_spotify_playlist(track_ids, playlist_name, token):
    HEADERS['Authorization'] = "Bearer " + token
    if not track_ids:
        logging.error("No tracks found on Spotify")
        return False

    playlist_id = create_playlist(get_user_id(), playlist_name)
    if playlist_id == FAILURE:
        return False
    return add_tracks(playlist_id, track_ids)


if __name__ == "__main__":
    tracks = [
        "ac dc thunderstruck",
        "kiss rock and roll",
        "jimi hendrix all along the watch tower"
    ]

    get_track_ids(tracks)

