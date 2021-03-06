#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _main_viacom
import re
import simplejson
import sys
import urllib

pluginHandle = int(sys.argv[1])

SITE = 'nick'
NAME = 'Nickelodeon'
DESCRIPTION = "Nickelodeon, now in its 31st year, is the number-one entertainment brand for kids. It has built a diverse, global business by putting kids first in everything it does. The company includes television programming and production in the United States and around the world, plus consumer products, online, recreation, books and feature films. Nickelodeon's U.S. television network is seen in more than 100 million households and has been the number-one-rated basic cable network for 16 consecutive years."
BASE = 'http://nick.com'
FULLEPISODES = 'http://www.nick.com/apps/api/v2/content-collection?apiKey=gve7v8ti&rows=40&series=%s&start=0&types=episodes'
SHOWS = 'http://www.nick.com/apps/api/v2/editorial-content-categories/stars?apiKey=gve7v8ti'
CLIPS = 'http://www.nick.com/apps/api/v2/content-collection?apiKey=gve7v8ti&killDBSequenceNumber=&rows=40&series=%s&start=0&types=video'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS, header = {'X-Forwarded-For' : '12.13.14.15'})
	showdata = simplejson.loads(master_data)
	for data in showdata:
		master_name = data['title'].replace('&', 'and')
		season_url = data['urlKey']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(FULLEPISODES % season_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try: count = int(simplejson.loads(season_data)['meta']['count'])
	except: count = 0
	if count > 0:
		season_url2 = FULLEPISODES % season_url + '&start=0&rows=' + str(count)
		_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
	season_data2 = _connection.getURL(CLIPS % season_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try: count = int(simplejson.loads(season_data2)['meta']['count'])
	except: count = 0
	if count > 0:
		season_url3 = CLIPS % season_url + '&start=0&rows=' + str(count)
		_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	episode_menu = simplejson.loads(episode_data)['results']
	for episode_item in episode_menu:
		try:
			show_name = episode_item['seriesTitle']
		except:
			show_name = ''
		episode_name = episode_item['title']
		url = 'http://legacy.nick.com/videos/clip/%s.html'
		url = url % episode_item['urlKey']
		try:
			episode_plot = episode_item['description']
		except:
			episode_plot = ''
		image = episode_item['images'][0]['assets'][0]['path']
		episode_thumb = 'http://nick.com'+image
		try:
			episode_duration = _common.format_seconds(episode_item['duration'])
		except:
			episode_duration = -1
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'durationinseconds' : episode_duration,
						'tvshowtitle' : show_name }
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	_main_viacom.play_video(BASE, video_url2)

def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	return _main_viacom.list_qualities(BASE, video_url2)
