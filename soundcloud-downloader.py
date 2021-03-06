﻿#!/usr/bin/python
# 13/04/13
import urllib, urllib2, sys, re

if len(sys.argv) <= 1:
	exit("You need to enter a soundcloud URI\nI.E:\n $./ %s http://soundcloud/user/song" % sys.argv[0])

def get_dl_url(htmlsource):
	# regular expression for the string we will search for in htmlsource 
	regexp = '<img\sclass="waveform"\ssrc="http://[^/]*/(\w*)_m.png"\sunselectable="on"\s/>'
	
	# find the first match that occurs, if any
	match = re.search(regexp, htmlsource)
	
	if match:
		# if we found a match, retrieve the song ID
		songid = match.group(1)	
		# create a new stream hyperlink with the song ID
		url = "http://media.soundcloud.com/stream/%s" % songid
	else:
		sys.exit("No waveform image found at %s. Exiting." % sys.argv[1])
	
	return url

def get_title(htmlsource):
	# regular expression for the string we will search for in htmlsource
	regexp = "<title>(.*?)by\s([\w'\s]*)\son\sSoundCloud.*</title>"

	match = re.search(regexp, htmlsource)
	
	if match:
		# if we found a match, retrieve the title of the song
		#title = "%s - %s.mp3" % (match.group(1), match.group(2)) #\1 Songtitle \2 Artist
		title = [match.group(1), match.group(2)]
	else:
		sys.exit("No title data for song at %s. Exiting." % sys.argv[1])
	
	return title

def main():
	print "Getting Information... "
	
	# retrieve the URL of the song to download, from the final command-line argument
	soundcloud_url = sys.argv[-1]
	
	try:
		# open our song's URL for reading
		html = urllib2.urlopen(soundcloud_url)
	except ValueError:
		# the user supplied URL is invalid or could not be retrieved 
		sys.exit("Error: The URL '%s' can not be retrieved" % soundcloud_url)
		
	# store the contents (source) of our song's URL
	htmlsource = html.read()
	html.close()
	
	# get our song's title from its HTML contents
	songinfo = get_title(htmlsource)
	title  = "%s - %s.mp3" % (songinfo[0], songinfo[1])
	
	# get our song's actual download URL from its HTML contents
	url = get_dl_url(htmlsource)
	
	print "Downloading File '%s'" % title
	
	# copy the download URL's content (the full song) to a file 
	# with a filename that matches our song's title
	filename, headers = urllib.urlretrieve(url=url, filename=title, reporthook=report)
	print "\n\nDownload Complete"
	print "Attempting to add ID3 tags"
	add_id3_tags(title, songinfo[0], songinfo[1])

def report(block_no, block_size, file_size):
	global download_progress
	download_progress += block_size
	
	sys.stdout.write("\rDownloading (%.2fMB/%.2fMB): %.2f%% / 100%%" 
		% (download_progress/1024.00/1024.00, file_size/1024.00/1024.00, 100 * float(download_progress)/float(file_size)) )
	sys.stdout.flush()

def add_id3_tags(filename, title, artist):
	try:
		from ID3 import *
	except ImportError:
		print "ID3 Tags will not be added to the MP3 as the ID3 module is not installed\n# sudo apt-get install python-id3"
		return 1
		
	try:
		id3info = ID3(filename)
		id3info['TITLE'] = title
		id3info['ARTIST'] = artist
		print "ID3 tags added"
	except InvalidTagError, message:
		print "Invalid ID3 tag:", message
	
	return 0

if __name__ == '__main__':
	download_progress = 0
	main()
