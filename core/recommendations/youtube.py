#!/usr/bin/env python
import urllib
import requests
from bs4 import BeautifulSoup


def youtube_recommendations(url):
    # do it in a thread friendly way.
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    videos = soup.find_all('a', {"class":'content-link'})
    for video in videos:

        url = "https://www.youtube.com" + video.get('href')

        if 'googleads' in url:
            continue
        title = video.text
        if 'doubleclick' in title or 'list=' in url or 'album review' in title.lower():
            continue
        title = title.split('\n\n    ')[1][:-3]
        yield (url, title)


def getYoutubeURLFromSearch(searchString):
    """
    https://github.com/schollz/playlistfromsong/blob/master/playlistfromsong/__main__.py
    :param searchString:
    :return:
    """
    urlToGet = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(searchString)  # NOQA
    r = requests.get(urlToGet)
    soup = BeautifulSoup(r.content, 'html.parser')
    videos = soup.find_all('h3', class_='yt-lockup-title')
    for video in videos:
        link = video.find_all('a')[0]
        url = "https://www.youtube.com" + link.get('href')
        if 'googleads' in url:
            continue
        title = link.text
        if 'doubleclick' in title or 'list=' in url or 'album review' in title.lower():
            continue
        return url

    return ""



if __name__ == "__main__":
    g = youtube_recommendations("https://www.youtube.com/watch?v=2ICQrU63g2k&t=0s")
    for i in g:
        print(i)

