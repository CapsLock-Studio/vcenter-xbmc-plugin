# -*- coding: utf-8 -*-
import os, sys, inspect

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], 'resources/lib')))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import re
from furl import furl
from pyquery import PyQuery as pq
from lxml.html import HTMLParser, fromstring

UTF8_PARSER = HTMLParser(encoding='utf-8')
__id__ = 'plugin.video.vcenter'
__host__ = 'center.no-ip.info'
__port__ = 22560
__folder_base_url__ = 'viewer/folder'
__video_base_url__ = 'funcs/count-click'
__base__ = sys.argv[0]
__handle__ = int(sys.argv[1])
__args__ = dict(urlparse.parse_qs(sys.argv[2][1:]))
__url_base__ = 'http://%s:%d' % (__host__, __port__)
__folder_url__ = '%s/%s' % (__url_base__, __folder_base_url__)
__video_url__ = '%s/%s' % (__url_base__, __video_base_url__)
__token__ = '735034694f57413275406b524d5638763440615068445769596e56617336725677574e69784e5170317379744d5a5871555946744f61586548384b576a347636374c524a577066697a69732d'
__code__ = '6d4b6e697a695953305168556b4f6b46624379486d412d2d'
__addon__ = xbmcaddon.Addon(__id__)
__special__ = __addon__.getSetting('special')
__special__ = True if __special__ is 'true' else False

def build_url(query):
    return '%s?%s' % (__base__, urllib.urlencode(query))

def build_vcenter_url(url, ref=''):
    return furl(url).add({'token': __token__, 'code': __code__, 'special': 1 if __special__ else 0, 'ref': ref}).url

def href_get_id(url):
    full_sliced_url = url.split('?')
    for full_sliced in full_sliced_url:
        sliced = full_sliced.split('/')
        for s in sliced:
            m = re.match('^([a-f0-9A-F]+)$', s)
            if m:
                return m.group(1)
    return ''

def get_folder_data(folder=''):
    url = '%s/%s' % (__folder_url__, folder)
    url = build_vcenter_url(url)
    res = requests.get(url)
    html_body = res.text
    d = pq(fromstring(html_body, parser=UTF8_PARSER))
    result = []
    videos = d('.video')
    folders = d('.folder')
    for f in folders.items():
        result.append({'name': f.text(), 'id': href_get_id(f.attr('href')), 'isFolder': True})
    for v in videos.items():
        result.append({'name': v.text(), 'id':  href_get_id(v.attr('href')), 'isFolder': False})
    return result

def build():
    __folder__ = __args__.get('folder', '')
    __folder__ = __folder__[0] if type(__folder__) is list else __folder__
    __data__ = get_folder_data('' if __folder__ is None else __folder__)

    for data in __data__:
        #  is folder
        if data.get('isFolder'):
            url = build_url({'folder': data.get('id')})
            li = xbmcgui.ListItem(data.get('name'), iconImage='')
            li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=__handle__, url=url, listitem=li, isFolder=True)
        # is video
        else:
            url = '%s/%s' % (__video_url__, data.get('id'))
            url = build_vcenter_url(url, 'funcs/stream')
            li = xbmcgui.ListItem(data.get('name'), iconImage='')
            li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=__handle__, url=url, listitem=li)

    xbmcplugin.endOfDirectory(__handle__)

if __name__ == '__main__':
    build()