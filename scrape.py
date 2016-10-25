#!/usr/bin/env python3

# Considerations: trawl first, then do the downloads?  Consider multithreading?

from bs4 import BeautifulSoup, SoupStrainer
from pprint import pprint
from urllib.request import urlopen, Request
import logging
from string import punctuation
import os

URL_ROOT = 'https://unattendedconsequences.simplecast.fm/'
EPISODES_ROOT = 'https://unattendedconsequences.simplecast.fm/episodes'
TEST_EPISODE = ('https://unattendedconsequences.simplecast.fm/episodes/'
                '46481-derrida-is-the-biggest-wanker')


# Example episode block:
'''
<time class="podcast-episode-date" datetime="2016-10-24">24 October 2016</time>
<h3 class="podcast-episode-title"><a href="/episodes/50539-i-m-not-here-to-judge-you-chickenf-ckers">I'm Not Here to Judge You Chickenf*ckers</a></h3>
'''


def main():
    prepare()
    scrape_top()


def prepare():
    '''Make sure that TODO: consider adding a folder for files?  Verify
folder structure?'''
    if os.path.exists('episodes') and not os.path.isdir('episodes'):
        raise RuntimeError("File 'episodes' exists and is not a directory."
                           "  Downloaded files have nowhere to be saved.")
    if not os.path.exists('episodes'):
        os.mkdir('episodes')


def scrape_top():
    '''Begins at the Unattended Consequences episodes root, identifies
episode blocks, and downloads the episodes found to the local
directory.
    '''
    url_source = urlopen(EPISODES_ROOT)
    soup = BeautifulSoup(url_source)
    items = [item
             for item in soup.find_all('header')
             if item.find_all('time') and item.find_all('h3')]
    for item in items:
        # Build a naturally sorted filename out of the datetime and
        # episode title.
        datetime = item.find('time')['datetime']
        internal_url = item.find('a')['href']
        title = item.find('a').text
        sanitized = sanitize_title(title)
        full_url = URL_ROOT + internal_url
        intended_filename = (
            "episodes/UC_{date}_{sanitized}.mp3"
            .format(date=datetime, sanitized=sanitized))
        logging.debug('Found:\n'
                      ' Date: {}\n'
                      ' Link: {}\n'
                      ' Title: {}\n'
                      ' Outfile: {}'.format(datetime, full_url, title,
                                            intended_filename))
        # Check to see if it's there already
        if os.path.exists(intended_filename):
            logging.info("File {!r} already exists.  Skipping.".format(
                intended_filename))
            continue
        logging.debug("Fetching mp3 links from {!r}...".format(full_url))
        mp3_hrefs = get_mp3_links_from_page(full_url)
        assert len(mp3_hrefs) == 1, "Problematic links!"
        logging.debug("Downloading episode...")
        download_mp3(mp3_hrefs[0], intended_filename)
        

def download_mp3(href, out_filename=None):
    logging.info("Downloading link {!r}".format(href))
    req = Request(href, headers={'User-Agent' : 'Magic Browser'})
    logging.debug("Opening href...")
    url = urlopen(req)
    logging.debug("Reading opened url...")
    data = url.read()
    logging.debug("Data read.  Saving to {!r}.".format(out_filename))
    with open(out_filename, 'wb') as out:
        out.write(data)
        

def get_mp3_links_from_page(url):
    url_source = urlopen(url)
    link_strainer = SoupStrainer("a")
    soup = BeautifulSoup(url_source)
    items = soup.find_all(link_strainer)
    downloads = [item for item in items if 'download' in item.text.lower()]
    targets = [item.attrs['href']
               for item in downloads
               if item.attrs['href'][-4:].lower() == '.mp3']
    return targets



def sanitize_title(title):
    '''Cleans a title to a valid filename.  This simple simply removes
punctuation and replaces spaces with underscore.'''
    for p in punctuation:
        title = title.replace(p, '')
    title = title.replace(' ', '_')
    return title


def check_for_new():
    '''Placeholder for future cron check.  In theory, it could just run
main(), since existing files get skipped.'''
    ...
        

# Working utility script
def get_top_soup():
    url_source = urlopen(EPISODES_ROOT)
    soup = BeautifulSoup(url_source)
    return soup


logging.getLogger('').setLevel(logging.DEBUG)

if __name__=="__main__":
    main()
    
