# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor

import json
import random
import re

from ..compat import (
    compat_parse_qs,
    compat_str,
)
from ..utils import (
    js_to_json,
    strip_jsonp,
    urlencode_postdata,
)


class WeiboIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?weibo\.com/[0-9]+/(?P<id>[a-zA-Z0-9]+)'
    _TESTS = [{
        'url': 'https://weibo.com/6275294458/Fp6RGfbff?type=comment',
        'info_dict': {
            'id': 'Fp6RGfbff',
            'ext': 'mp4',
            'title': 'You should have servants to massage you,... 来自Hosico_猫 - 微博',
        }
    }, {
        # DASH formats - https://github.com/ytdl-org/youtube-dl/issues/27320
        'url': 'https://weibo.com/5720474518/JxfyRbDh6?type=repost',
        'info_dict': {
            'id': 'JxfyRbDh6',
            'ext': 'mp4',
            'title': '#张亚东访谈KDA#击穿次元壁！张亚东访谈K... 来自英雄联盟 - 微博',
        },
        'params': {
            'format': 'bestvideo',
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # to get Referer url for genvisitor
        webpage, urlh = self._download_webpage_handle(url, video_id)

        visitor_url = urlh.geturl()

        if 'passport.weibo.com' in visitor_url:
            # first visit
            visitor_data = self._download_json(
                'https://passport.weibo.com/visitor/genvisitor', video_id,
                note='Generating first-visit data',
                transform_source=strip_jsonp,
                headers={'Referer': visitor_url},
                data=urlencode_postdata({
                    'cb': 'gen_callback',
                    'fp': json.dumps({
                        'os': '2',
                        'browser': 'Gecko57,0,0,0',
                        'fonts': 'undefined',
                        'screenInfo': '1440*900*24',
                        'plugins': '',
                    }),
                }))

            tid = visitor_data['data']['tid']
            cnfd = '%03d' % visitor_data['data']['confidence']

            self._download_webpage(
                'https://passport.weibo.com/visitor/visitor', video_id,
                note='Running first-visit callback',
                query={
                    'a': 'incarnate',
                    't': tid,
                    'w': 2,
                    'c': cnfd,
                    'cb': 'cross_domain',
                    'from': 'weibo',
                    '_rand': random.random(),
                })

            webpage = self._download_webpage(
                url, video_id, note='Revisiting webpage')

        title = self._html_search_regex(
            r'<title>(.+?)</title>', webpage, 'title')

        video_formats = compat_parse_qs(self._search_regex(
            r'video-sources=\\\"(.+?)\"', webpage, 'video_sources'))

        formats = []
        supported_resolutions = (480, 720)
        for res in supported_resolutions:
            vid_urls = video_formats.get(compat_str(res))
            if not vid_urls or not isinstance(vid_urls, list):
                continue

            vid_url = vid_urls[0]
            formats.append({
                'url': vid_url,
                'height': res,
            })

        media_ids = self._search_regex(
            # for single-media posts only
            r' action-data=\\"protocol=(?:.*?,)?dash(?:,.*?)?&type=feedvideo&objectid=(\d+:[\da-f]+)&',
            webpage, 'media ids', default=None)
        if media_ids:
            dash_data = self._download_json('https://weibo.com/aj/video/getdashinfo?media_ids=%s' % media_ids,
                                            media_ids, 'Downloading DASH mp4 urls')
            for media in dash_data['data']['list'][0]['details']:
                if 'play_info' not in media:
                    continue
                pinf = media['play_info']
                if not pinf['url']:
                    continue
                formats.append({
                    'url': pinf['url'],
                    'format_id': pinf.get('label'),
                    'width': pinf.get('width') if 'video/' in pinf.get('mime') else None,
                    'height': pinf.get('height') if 'video/' in pinf.get('mime') else None,
                    ('vbr' if 'video/' in pinf.get('mime') else 'abr'): pinf.get('bitrate'),
                    'fps': pinf.get('fps') if 'video/' in pinf.get('mime') else None,
                    'vcodec': pinf.get('video_codecs') if 'video/' in pinf.get('mime') else 'none',
                    'acodec': pinf.get('audio_codecs') if 'audio/' in pinf.get('mime') else 'none',
                    'asr': pinf.get('audio_sample_rate') if 'audio/' in pinf.get('mime') else None,
                    'filesize': pinf.get('size'),
                })

        self._sort_formats(formats, field_preference=('height', 'vbr', 'abr'))

        uploader = self._og_search_property(
            'nick-name', webpage, 'uploader', default=None)

        return {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'formats': formats
        }


class WeiboMobileIE(InfoExtractor):
    _VALID_URL = r'https?://m\.weibo\.cn/status/(?P<id>[0-9]+)(\?.+)?'
    _TEST = {
        'url': 'https://m.weibo.cn/status/4189191225395228?wm=3333_2001&sourcetype=weixin&featurecode=newtitle&from=singlemessage&isappinstalled=0',
        'info_dict': {
            'id': '4189191225395228',
            'ext': 'mp4',
            'title': '午睡当然是要甜甜蜜蜜的啦',
            'uploader': '柴犬柴犬'
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # to get Referer url for genvisitor
        webpage = self._download_webpage(url, video_id, note='visit the page')

        weibo_info = self._parse_json(self._search_regex(
            r'var\s+\$render_data\s*=\s*\[({.*})\]\[0\]\s*\|\|\s*{};',
            webpage, 'js_code', flags=re.DOTALL),
            video_id, transform_source=js_to_json)

        status_data = weibo_info.get('status', {})
        page_info = status_data.get('page_info')
        title = status_data['status_title']
        uploader = status_data.get('user', {}).get('screen_name')

        return {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'url': page_info['media_info']['stream_url']
        }
