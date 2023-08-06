import cachetools.func
import requests
import re
from . import api
from .. videoinfo import VideoInfo
from ..exceptions import InvalidVideoIdException

mobile_user_agent = 'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36'
headers_mobile ={
    'User-Agent': mobile_user_agent,
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-YouTube-Client-Name': '2',
    'X-YouTube-Client-Version': '2.20180830',
}


channel_id_re = re.compile(r'videos\.xml\?channel_id=([a-zA-Z0-9_-]{24})"')
ch_id_pattern_0 = re.compile(r'(^UC[\w-]+)')
ch_id_pattern_1 = re.compile(r'/channel/(UC[\w-]+)')
ch_id_pattern_2 = re.compile(r'(youtube\.com.+)')


@cachetools.func.lru_cache(maxsize=128)
def get_channel_id(base_url):
    match = re.search(ch_id_pattern_0, base_url)
    if match:
        return match.group(1)

    match = re.search(ch_id_pattern_1, base_url)
    if match:
        return match.group(1)

    match = re.search(ch_id_pattern_2, base_url)
    if match:
        client = requests.Session()
        base_url = 'https://m.' + match.group(1)
        response = client.get(base_url + '/about?pbj=1',
                              headers=headers_mobile).text
        match = channel_id_re.search(response)
        if match:
            return match.group(1)
    return None


def get_videos(channel_id):
    cache = set()
    counter = 0
    for items in api.get_video_items(channel_id):
        for item in items:
            if not item:
                return
            video = parse(item)
            if video.get('id') in cache:
                counter += 1
                if counter > 20:
                    return
                continue
            cache.add(video.get('id'))
            yield video


def parse(item):
    video = dict()
    try:
        video["id"] = item["snippet"]["resourceId"]["videoId"]
        video["title"] = video["time_published"] = item["snippet"]["title"]
        video["time_published"] = item["snippet"]["publishedAt"]
        video["author"] = item["snippet"]["channelTitle"]
        info = VideoInfo(video["id"])
        video['duration'] = info.get_duration()
        return video
    except KeyError as e:
        print(type(e), str(e))
        video.update(error=True)
        return video
    except InvalidVideoIdException as e:
        print(str(e))
        video.update(error=True)
        return video