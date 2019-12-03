import requests
import regex
import time

from youtube import get_yt_comments, get_yt_video_info

MIN_TRACKS = 5
yt_mobile_regex = r"http(?:s?):\/\/(?:www\.)?youtu.be/(\S*)"
contains_tracklist_regex = r"tracklist[^\n]*\n"

comment_regexps = {
    "single_track_per_line": [
        (r"\d{1,2}[\.| -—]\W*\d{1,2}:\d{2}:\d{2}\W*\s(.*(?:-|—).*)", "1. (XX:XX:XX) "),
        (r"\d{1,2}[\.| -—]\W*\d{1,2}:\d{2}\W*\s(.*(?:-|—).*)", "1. (XX:XX) "),
        (r"[\[\(]\d{1,2}[\]\)]\W*\s(.*(?:-|—).*)", "[XX]"),
        (r"[\[\(]?\d{1,2}:\d{2}:\d{2}[\]\)]?\W*\s(.*(?:-|—).*)", "(XX:XX:XX)"),
        (r"[\[\(]?\d{1,2}:\d{2}[\]\)]?\W*\s(.*(?:-|—).*)", "(XX:XX)"),
        (r"\d{1,2}\.\W*\s(.*(?:-|—).*)", "01."),
        (r"\d{2}\W*\s(.*(?:-|—).*)", "01 ")
    ],
    "multi_track_per_line": [
        (r"\d{1,2}\.", "1. song1 2.song2"),
        (r"[\[\(]?\d{1,2}:\d{2}:\d{2}[\]\)]?", "(00:00:00) song1 (00:00:00) song2"),
        (r"[\[\(]?\d{1,2}:\d{2}[\]\)]?", "(00:00) song1 (00:00) song2"),
    ],
    "single_track_multi_line": [
        (r"^[\[\(]?\d{1,2}:\d{2}:\d{2}[\]\)]?\W*\n(.*)\n", "(00:00:00)\n"),
        (r"^[\[\(]?\d{1,2}:\d{2}[\]\)]?\W*\n(.*)\n", "(00:00)\n"),
    ],
    "single_track_per_line_description_only": [
        (r"^([^-\n]* - [^-\n]*)(?: - (?:[^-\n]*))?\n", "The tracklist:\n")
    ]
}


def scan_yt_comments(url):
    for comment in get_yt_comments(url):
        if len(comment.split("\n")) == 1:
            tracklist = find_single_line_tracklist(comment)
        else:
            tracklist = find_multi_line_tracklist(comment)
        if tracklist:
            return [track.replace("-", "") for track in tracklist]
    print("Tracklist not found in comments")
    return None


def scan_yt_description(description):
    tracklist = find_multi_line_tracklist(description)
    if tracklist:
        return tracklist

    try:
        _, tracklist_text = regex.split(contains_tracklist_regex, description, flags=regex.IGNORECASE)
        tracklist = match(tracklist_text, comment_regexps["single_track_per_line_description_only"], regex.MULTILINE)
    except ValueError:
        print("No Tracklist in description")
        pass
    if tracklist:
        return tracklist

    return None


def scan_yt(url):
    match = regex.match(yt_mobile_regex, url)
    if match:
        url = f"https://youtube.com/watch?v={match.group(1)}"

    tracklist = scan_yt_comments(url)
    title, description = get_yt_video_info(url)
    if not tracklist:
        tracklist = scan_yt_description(description)
    if not tracklist:
        return title, None
    return title, [
        process_track(track) for track in tracklist
    ]


def process_track(track):
    # Remove remix info
    track = regex.sub("(\(.*\)|\[.*\])", "", track).strip()
    # Remove any extra track info and replace unicode — with -
    track = "".join(track.replace("—", "-").split("-")[:2])
    #Remove multiple spaces
    track = regex.sub(' +', ' ', track)
    # remove feat
    # track = track.replace("feat", "").replace
    return track


def find_single_line_tracklist(comment):
    for pattern, _ in comment_regexps["multi_track_per_line"]:
        result = regex.split(pattern, comment)
        result_str = "".join(result)
        dash_count, em_dash_count = result_str.count("-"), result_str.count("—")
        if len(result) > MIN_TRACKS and (dash_count > MIN_TRACKS or em_dash_count > MIN_TRACKS):
            return result[1:]
    return None
 

def find_multi_line_tracklist(comment, regexps=None):
    for pattern, _ in comment_regexps["single_track_per_line"]:
        matches = regex.findall(pattern, comment)
        if len(matches) > MIN_TRACKS:
            return matches

    for pattern, _ in comment_regexps["single_track_multi_line"]:
        matches = regex.findall(pattern, comment)
        if len(matches) > MIN_TRACKS:
            return matches

    return None

def match(comment, regexps, flags):
    for pattern, _ in regexps:
        matches = regex.findall(pattern, comment, flags=flags)
        if len(matches) > MIN_TRACKS:
            return matches
    return None

if __name__ == "__main__":
    print(scan_yt("https://www.youtube.com/watch?v=AJvCnFqSViA&t=742s"))