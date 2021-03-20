import os
import collections
import requests
import re
import pafy
import pandas as pd
import time
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import NoSuchElementException


class Scraper:

    def __init__(self, path):
        self._path = path

    def set_path(self, p):
        self._path = p

    def get_path(self):
        return self._path

    # ----------------------------------------------------------------------------------------------------------------------------------------#

    # Google chrome settings
    @staticmethod
    def driver_setting():
        options = webdriver.ChromeOptions()
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver

    # ----------------------------------------------------------------------------------------------------------------------------------------#

    @staticmethod
    def print_list(data):
        for item in data:
            print(item)
        print('Size of list = ' + str(len(data)))

    @staticmethod
    def print_collect(data):
        for item in data:
            print('key = ' + item + ': value = ' + str(data[item]))
        print('Size of collect = ' + str(len(data)))

    @staticmethod
    def clean_str(line):
        rubbish = ['[', ']', '\'', '\xa0',
                   'отмето', 'отметк', 'просмотро', 'просмотров', 'просмотра', 'просомтр',
                   'комментарий', 'комментариев', 'комментария']
        for rub in rubbish:
            if rub in line:
                line = line.replace(rub, '')
        if line.endswith(' '): line = line[:-1]
        return line

    def clean_title(self, title):
        lines = title.splitlines()
        # print(lines)
        try:
            if len(lines) == 3:
                return self.clean_str(lines[1])
            elif len(lines) == 1:
                return self.clean_str(lines[0])
            elif len(lines) == 4:
                return self.clean_str(lines[2])
        except:
            return 'none'

    # ----------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def write_csv(data, path):
        df = pd.DataFrame(data)
        df.to_csv(path, sep=';', encoding='utf-8-sig', index=False)

    # ----------------------------------------------------------------------------------------------------------------------------------------

    def get_pl_links(self, driver):
        data_cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, r"""//*[
        @id="video-title"]""")))
        playlists = collections.defaultdict(list)
        for item in data_cards:
            title = self.clean_str(item.text.lower())
            link = self.clean_str(str(item.get_attribute("href")))
            playlists[title].append(link)
        return playlists

    def get_videos(self, driver, link):
        link = link.replace('[', '').replace(']', '').replace('\'', '')
        driver.get(link)
        data_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, r"""//*[@id="wc-endpoint"]""")))
        video_links = collections.defaultdict(list)
        flag = True
        for item in data_cards:
            try:
                title = self.clean_title(item.text.lower())
                if 'none' in title:
                    flag = False
                else:
                    link = self.clean_str(str(item.get_attribute("href")))
                    video_links[title].append(link)
            except:
                flag = False
        return video_links

    def get_all_links(self, pl_links, driver):
        result = collections.defaultdict(list)
        count = 0
        for playlist in pl_links:
            link = pl_links[playlist][0]
            videos = self.get_videos(driver, link)
            for video in videos:
                result[video + ' playlist:' + playlist].append(videos[video][0])
        return result


    def getVideoInfo(self, link, driver):
        driver.get(link)

        date = (WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, r"""//*[@id="date"]/yt-formatted-string""")))).text

        driver.execute_script('window.scrollTo(0, 500);')
        try:
            count_comments = self.clean_str((WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, r"""//*[@id="count"]/yt-formatted-string""")))).text)
        except:
            count_comments = 0

        f = requests.get(link)
        f_text = f.text
        count_like = self.clean_str(re.findall(r"[0-9\s]+\sотмет[а-я]", f_text)[0])
        count_dislike = self.clean_str(re.findall(r"[0-9\s]+\sотмет[а-я]", f_text)[2])
        views = self.clean_str(re.findall(r"[0-9\s]+\sпросмотр[а-я]", f_text)[2])

        video = pafy.new(link)
        duration = video.length
        return [count_like, count_dislike, views, duration, date]

    def get_all_info(self, driver, videos):
        result = []
        size = str(len(videos))
        count = 1
        for video in videos:
            link = self.clean_str(str(videos[video]))
            info = self.getVideoInfo(link, driver)
            title = video.split(' playlist:')
            cur_result = [title[0], title[1]] + info
            result.append(cur_result)
            print(str(count) + '/' + size)
            count += 1
        return result




    # ----------------------------------------------------------------------------------------------------------------------------------------#

    def start_scraper(self):
        # 1 - start driver(Google Chrome)
        driver = self.driver_setting()
        print('done - 1')

        # 2 - go to playlists page
        driver.get(self._path + '/playlists')
        print('done - 2')

        # 3 - get links by all playlists
        playlistsLinks = self.get_pl_links(driver)
        print('done - 3')

        # 4 - get links by videos in all playlist
        all_videos = self.get_all_links(playlistsLinks, driver)
        print('done - 4')

        #5 - get all info
        result = self.get_all_info(driver, all_videos)
        self.print_list(result)
        print('done - 5')

        self.write_csv(result, 'result.csv')
        print('done - all')


        # 4 - get links by video in current playlist
        # title = 'история жизни гениальных авторов'
        # link = self.clean_str(str(playlistsLinks[title]))
        # videos_link = self.get_videos(driver, link)
        # self.print_collect(videos_link)

        # test
        # title = 'атака титанов'
        # link = self.clean_str(str(playlistsLinks[title]))
        # videosLinks = self.get_videos(driver, link)
        # # self.printCollect(videosLinks)
        #
        # videoTitle = 'атака титанов - аниме, которое тебя шокирует! / обзор и анализ сериала ч.1'
        # videolink = self.clean_str(str(videosLinks[videoTitle]))
        # print(videolink)
        # self.getVideoInfo(videolink, driver)
