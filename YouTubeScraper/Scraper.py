from datetime import datetime
import collections
import requests
import re
import pafy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:

    def __init__(self, path, name):
        self._path = path
        self._name = name

    def set_path(self, p, n):
        self._path = p
        self._name = n

    def get_path(self):
        return self._path

    def get_name(self):
        return  self._name

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
                   'комментарий', 'комментариев', 'комментария', 'Дата премьеры: ']
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
        except: return 'none'

    # ----------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def write_csv(data, name):
        df = pd.DataFrame(data)
        df.to_csv('result ' + name + '.csv', sep=';', encoding='utf-8-sig', index=False)

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
            except: flag = False
        return video_links

    def get_all_links(self, pl_links, driver):
        result = collections.defaultdict(list)
        for playlist in pl_links:
            link = pl_links[playlist][0]
            videos = self.get_videos(driver, link)
            for video in videos:
                result[video + ' playlist:' + playlist].append(videos[video][0])
        return result

    def get_video_info(self, link):
        driver = self.driver_setting()
        driver.get(link)
        try:
            date = (WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, r"""//*[@id="date"]/yt-formatted-string""")))).text
        except: date = ''

        driver.execute_script('window.scrollTo(0, 500);')
        try:
            count_comments = self.clean_str((WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, r"""//*[@id="count"]/yt-formatted-string""")))).text)
        except: count_comments = 0

        f = requests.get(link)
        f_text = f.text
        try: count_like = self.clean_str(re.findall(r"[0-9\s]+\sотмет[а-я]", f_text)[0])
        except: count_like = 0
        try: count_dislike = self.clean_str(re.findall(r"[0-9\s]+\sотмет[а-я]", f_text)[2])
        except: count_dislike = 0
        try: views = self.clean_str(re.findall(r"[0-9\s]+\sпросмотр[а-я]", f_text)[2])
        except: views = 0

        try:
            video = pafy.new(link)
            duration = video.length
            driver.quit()
        except: duration = 0
        driver.quit()
        return [count_like, count_dislike, views, count_comments, duration, date]

    def get_all_info(self, videos):
        result = []
        size = str(len(videos))
        count = 1
        for video in videos:
            link = self.clean_str(str(videos[video]))
            info = self.get_video_info(link)
            title = video.split(' playlist:')
            cur_result = [title[0], title[1]] + info
            result.append(cur_result)
            print(str(count) + '/' + size)
            count += 1
        return result

    # ----------------------------------------------------------------------------------------------------------------------------------------#

    def start_scraper(self):

        print('Start parser')
        print(datetime.now())
        # 1 - start driver(Google Chrome)
        driver = self.driver_setting()
        print('done - driver settings')

        # 2 - go to playlists page
        driver.get(self._path + '/playlists?view=1&sort=dd&shelf_id=0')
        print('done - get playlist path')

        # 3 - get links by all playlists
        playlists_links = self.get_pl_links(driver)
        print('done - get playlists links')

        # 4 - get links by videos in all playlists
        all_videos = self.get_all_links(playlists_links, driver)
        print('done - get all links in all playlists')
        driver.quit()

        # 5 - get all info
        result = self.get_all_info(all_videos)
        print('done - get all info')

        self.write_csv(result, self.get_name())
        print('done - write in csv')
        print('End')
        print(datetime.now())
