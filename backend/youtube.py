import os
from urllib.parse import urlparse, parse_qs


import regex
import googleapiclient.discovery

DEFAULT_KWARGS_COMMENTS = {
    "part": "snippet",
    "maxResults": 80,
    "order": "relevance",
    "textFormat": "plainText"
}

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv("YOUTUBE_DATA_API_KEY")


def extract_video_id(url):
    try:
        video_id = parse_qs(urlparse(url).query)['v'][0]
        return video_id
    except Exception as e:
        print(f"Could not extract video id, {e}")
        return None


def get_yt_comments(url):
    video_id = extract_video_id(url)
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        **DEFAULT_KWARGS_COMMENTS,
        videoId=video_id
    )
    response = request.execute()

    return [
        comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        for comment in response["items"]
    ]


def get_yt_video_info(url):
    video_id = extract_video_id(url)
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response['items'][0]['snippet']['title'], response['items'][0]['snippet']['description']


if __name__=="__main__":
    print(get_yt_video_info("https://www.youtube.com/watch?v=A9sOb_r6Hy0"))