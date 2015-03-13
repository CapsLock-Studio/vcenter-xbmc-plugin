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
__special__ = True if __special__ == 'true' else False

def build_url(query):
    return '%s?%s' % (__base__, urllib.urlencode(query))

def build_vcenter_url(url, ref=''):
    return furl(url).add({'token': __token__, 'code': __code__, 'special': 1 if __special__ else 0, 'ref': ref}).url

def href_get_id(url):
    full_sliced_url = url.split('?')
    for full_sliced in full_sliced_url:
        sliced = full_sliced.split('/')
        m = re.match('^([a-f0-9A-F]+)$', sliced[-1])
        if m:
            return m.group(1)
    return ''

def build_folder_data(folder=''):
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
    mode = __args__.get('mode', '')
    mode = mode[0] if type(mode) is list else mode
    if mode == 'main':
        folder = __args__.get('folder', '')
        folder = folder[0] if type(folder) is list else folder
        all_data = build_folder_data('' if folder is None else folder)
        build_data(all_data)
    elif mode == 'top':
        # change __folder_url__ with technical method
        top_base_url = 'recent/top'
        global __folder_url__
        __folder_url__ = '%s/%s' % (__url_base__, top_base_url)
        all_data = build_folder_data()
        build_data(all_data)
    else:
        build_folder_item(name='VCenter', param={'mode': 'main'})
        build_folder_item(name='Top Rated', param={'mode': 'top'})

    xbmcplugin.endOfDirectory(__handle__)

def build_data(all_data):
    for data in all_data:
        #  is folder
        if data.get('isFolder'):
            build_folder_item(name=data.get('name'), param={'folder': data.get('id'), 'mode': 'main'})
        # is video
        else:
            build_file_item(name=data.get('name'), id=data.get('id'), ref='funcs/stream')

def build_list_item(name):
    li = xbmcgui.ListItem(name, iconImage='')
    li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
    return li

def build_folder_item(name, param):
    li = build_list_item(name)
    url = build_url(param)
    xbmcplugin.addDirectoryItem(handle=__handle__, url=url, listitem=li, isFolder=True)

def build_file_item(name, id, ref):
    li = build_list_item(name)
    url = '%s/%s' % (__video_url__, id)
    url = build_vcenter_url(url, ref)
    xbmcplugin.addDirectoryItem(handle=__handle__, url=url, listitem=li)

if __name__ == '__main__':
    build()