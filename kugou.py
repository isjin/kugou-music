#!/usr/bin/env python
# coding:utf8
import os
import shutil
from multiprocessing import Pool
import url_parser
import re
import json


class KuGou(object):
    def __init__(self):
        self.urlparser = url_parser.UrlParser()
        self.url_list = self.music_urls()
        self.download_path = './music/'
        self.old_urls = self.old_urls_init()

    @staticmethod
    def old_urls_init():
        old_urls = []
        if os.path.exists('old_urls.txt'):
            with open('old_urls.txt', 'r') as f:
                lines = f.readlines()
            for line in lines:
                old_urls.append(str(line).strip())
        return old_urls

    @staticmethod
    def music_urls():
        url_musics = []
        f = open('./music.txt', 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            url_music = str(line).strip()
            url_musics.append(url_music)
        return url_musics

    def download_mp3(self, dwonload_url, path, filename):
        media_name = './temp/' + str(filename) + '.mp3'
        open_path = path + str(filename) + '.mp3'
        if os.path.exists(open_path) is False:
            command_1 = 'ffmpeg -i "%s" -acodec copy -vn "%s"' % (dwonload_url, media_name)
            os.system(command_1)
            size = self.get_size(media_name)
            if size >= 1000000:
                shutil.move(media_name, open_path)
            else:
                os.remove(media_name)
        return

    @staticmethod
    def get_size(file):
        return os.path.getsize(file)

    def existed_file(self, file):
        if os.path.exists(file) is True:
            file = str(file).replace('.mp3', '_2.mp3')
            file = self.existed_file(file)
        return file

    def main(self, url_music):
        # url_music='http://www.kugou.com/song/#hash=BEDD046FB30A0C443CD6F854574B065E&album_id=9175221'
        hash_value = re.split(r'[#]', str(url_music))[1]
        url_json = 'http://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback' \
                   '=jQuery19108163565913646271_1541204734807&%s' % hash_value
        music_json = self.urlparser.soup_request(url_json)
        music_json = re.sub(r'jQuery\d+_\d+|[()]', '', str(music_json))
        music_json = json.loads(str(music_json)[0:-1])
        download_url = music_json['data']['play_url']
        song_name = music_json['data']['song_name']
        author_name = music_json['data']['author_name']
        music_name = author_name + '-' + song_name
        print(url_music, music_name)
        self.download_mp3(download_url, self.download_path, music_name)
        self.old_url(url_music)

    def old_url(self, url_old):
        if url_old not in self.old_urls:
            f = open('old_urls.txt', 'a+')
            f.write(url_old + '\n')
            f.close()

    def get_urls(self):
        f = open('./music.txt', 'r')
        music_list_url = f.readline()
        f.close()
        # music_list_url = "http://www.kugou.com/yy/special/single/550704.html"
        urls = []
        soup = self.urlparser.soup_request(music_list_url)
        data = soup.find_all('div', class_="list1")
        soup = self.urlparser.lxml_html(data)
        lis = soup.find_all('li')
        for li in lis:
            url_info = li.a
            value = str(url_info.get('data')).split('|')
            song_url = "http://www.kugou.com/song/#hash=%s&album_id=%s" % (value[0], value[1])
            urls.append(song_url)
        return urls

    def iterater_url(self):
        urls = self.get_urls()
        for song_url in urls:
            yield song_url

    def main_song_album(self):
        pa = Pool()
        for song_url in self.iterater_url():
            pa.apply_async(self.main, (song_url,))
        pa.close()
        pa.join()


if __name__ == '__main__':
    app = KuGou()
    p = Pool()
    for url in app.url_list:
        # app.main(url)
        p.apply_async(app.main, (url,))
    p.close()
    p.join()
