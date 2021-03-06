﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _main_brightcove
import simplejson
import sys
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

SITE = 'amc'
NAME = 'AMC'
DESCRIPTION = "AMC reigns as the only cable network in history to ever win the Emmy' Award for Outstanding Drama Series three years in a row, as well as the Golden Globe' Award for Best Television Series - Drama for three consecutive years.  Whether commemorating favorite films from every genre and decade or creating acclaimed original programming, the AMC experience is an uncompromising celebration of great stories.  AMC's original stories include 'Mad Men,' 'Breaking Bad,' 'The Walking Dead,' 'The Killing' and 'Hell on Wheels.'  AMC further demonstrates its commitment to the art of storytelling with AMC's Docu-Stories, a slate of unscripted original series, as well as curated movie franchises like AMC's Can't Get Enough and AMC's Crazy About.  Available in more than 97 million homes (Source: Nielsen Media Research), AMC is owned and operated by AMC Networks Inc. and its sister networks include IFC, Sundance Channel and WE tv.  AMC is available across all platforms, including on-air, online, on demand and mobile.  AMC: Story Matters HereSM."
SHOWS = 'http://www.amctv.com/videos'
VIDEOURL = 'http://www.amctv.com/index.php'
CONST = '353d86e482b6e9ad425cfd0fbac5d21174cb0d55'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_menu = BeautifulSoup(master_data, 'html.parser').find('select', id = 'rb-video-browser-show').find_all('option', title = True)
	for master_item in master_menu:
		master_name = master_item.text
		season_url = master_item['value']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons():
	season_data = _connection.getURL(SHOWS)
	season_tree = BeautifulSoup(season_data, 'html.parser')
	season_videotypes = season_tree.find('select', id = 'rb-video-browser-content_type').find_all('option')
	season_shows = season_tree.find('select', id = 'rb-video-browser-show').find_all('option')
	for season_item in season_shows:
		if season_item['value'] == _common.args.url:
			season_category = season_item['title'].replace('[','').replace(']','').replace('"','').split(',')
			for season_videoitem in season_videotypes:
				if season_videoitem['value'] in season_category:
					season_name = season_videoitem.string
					season_url = 'rb-video-browser-num_items=100&module_id_base=rb-video-browser'
					season_url += '&rb-video-browser-show=' + season_item['value']
					season_url += '&rb-video-browser-content_type=' + season_videoitem['value']
					_common.add_directory(season_name, SITE, 'episodes', season_url)
	_common.set_view('seasons')

def episodes():
	episode_values = {	'video_browser_action' : 'filter',
						'params[type]' : 'all',
						'params[filter]' : _common.args.url,
						'params[page]' : '1',
						'params[post_id]' : '71306',      
						'module_id_base' : 'rb-video-browser' }
	episode_data = _connection.getURL(VIDEOURL, episode_values)
	episode_tree = simplejson.loads(episode_data)['html']['date']
	episode_menu = BeautifulSoup(episode_tree, 'html.parser').find_all('li')
	for episode_item in episode_menu:
		episode_name = episode_item.a.img['title']
		episode_plot = episode_item.a.img['alt'].replace('/n',' ')
		episode_thumb = episode_item.a.img['src']
		url = episode_item.a['href']		
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={	'title' : episode_name,
						'plot' : episode_plot }
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	stored_size = 0
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_player_key = video_tree.find('param', attrs = {'name' : 'playerKey'})['value']
	video_content_id = video_tree.find('param', attrs = {'name' : '@videoPlayer'})['value']
	video_player_id = video_tree.find('param', attrs = {'name' : 'playerID'})['value']
	renditions = _main_brightcove.get_episode_info(video_player_key, video_content_id, video_url, video_player_id, CONST)
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	for item in renditions['programmedContent']['videoPlayer']['mediaDTO']['IOSRenditions']:
		bitrate = int(item['encodingRate'])
		if bitrate > hbitrate and bitrate <= sbitrate and item['audioOnly'] == False:
			hbitrate = bitrate
			video_url2 = item['defaultURL']
	finalurl = video_url2
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
