import os 
import collections
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


class Scraper():
   
    def __init__(self, path):
        self._path = path

    def set_path(self, p):
        self._path = p

    def get_path(self):
        return self._path

#----------------------------------------------------------------------------------------------------------------------------------------#

    #Google chrome settings
    def driverSetting(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(options=options) 
        driver.maximize_window()
        return driver

#----------------------------------------------------------------------------------------------------------------------------------------#

    def printList(self, data):
        for item in data:
            print(item)
        print('Size of list = ' + str(len(data)))

    def printCollect(self, data):
        for item in data:
            print('key = ' + item + ': value = ' + str(data[item]))
        print('Size of collect = ' + str(len(data)))

    def cleanStr(self, line):
        rubbish = ['[', ']', '\'']
        for rub in rubbish:
            if (rub in line):
                line = line.replace(rub, '')
        return line

    def cleanTitle(self, title):
        lines = title.splitlines()
        #print(lines)
        try:
            if (len(lines) == 3): return self.cleanStr(lines[1])
            elif (len(lines) == 1): return self.cleanStr(lines[0])
            elif (len(lines) == 4): return self.cleanStr(lines[2])
        except:
            return 'none'
        

#----------------------------------------------------------------------------------------------------------------------------------------#

    def getPLLinks(self, driver):
        dataCards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, r"""//*[@id="video-title"]""")))
        playlists = collections.defaultdict(list)        
        for item in dataCards:
            title = (item.text).lower()
            link = self.cleanStr(str(item.get_attribute("href")))
            playlists[title].append(link)
        return playlists

    def getLinksInPL(self, driver, PLlink):
        driver.get(PLlink)
        dataCards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, r"""//*[@id="wc-endpoint"]""")))
        videoLinks = collections.defaultdict(list)
        flag = True
        for item in dataCards:
            try:
                title = self.cleanTitle((item.text).lower())
                if (title == 'none'): continue
                link = self.cleanStr(str(item.get_attribute("href")))
                videoLinks[title].append(link)
                #print(title + ' ' + link)
            except: flag = False
        return videoLinks
   
    def getVideoInfo(self, link, driver):
        driver.get(link)
        #videoTitle = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="container"]/h1/yt-formatted-string""")))).text
        #print('title: ' + str(videoTitle))
        
        #date = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="date"]/yt-formatted-string""")))).text
        #print('date:' + str(date))
        
        #style-scope ytd-toggle-button-renderer style-text
        ##text
        #style-scope ytd-toggle-button-renderer style-text
        #btn = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="top-level-buttons"]/ytd-toggle-button-renderer[1]/a"""))))
        btn = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, r"style-scope ytd-toggle-button-renderer style-text"))))
        #sleep(5)
        aria_label = btn.find_element_by_css_selector('span').get_attribute("aria-label")
        print(aria_label)
            #likes = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[7]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[1]/a/yt-formatted-string"""))))
            #areaLabel = likes.find_element_by_css_selector('span').get_attribute("aria-label")
        #print('likesCount: ' + str(aria_label))
        
        #try:
         #   dislikes = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="text"]""")))).text
          #  print('dislikesCount:' + str(dislikes))
        #except:
         #   print(False)

        #try:
         #   comments = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="count"]/yt-formatted-string/span[1]""")))).text
          #  print('commentsCount:' + str(comments))
        #except:
         #   print(False)
        
        #try:
         #   time = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, r"""//*[@id="overlays"]/ytd-thumbnail-overlay-time-status-renderer/span""")))).text
          #  print('time:' + str(time))
        #except:
          #  print(False)
        
        print('----------------------------------')
        #print(str(data) + ' ' + str(likes) + ' ' + str(dislikes) + ' ' + str(comments) + ' ' + str(time)) 
        
#----------------------------------------------------------------------------------------------------------------------------------------#

    def startScraper(self):
        #1 - start driver(Google Chrome)
        driver = self.driverSetting()

        #2 - go to playlists page 
        driver.get(self._path + '/playlists')
       
        #3 - get links by all playlists
        playlistsLinks = self.getPLLinks(driver)

        #test
        title = 'атака титанов'
        link = self.cleanStr(str(playlistsLinks[title]))
        videosLinks = self.getLinksInPL(driver, link)
        #self.printCollect(videosLinks)

        videoTitle = 'атака титанов - аниме, которое тебя шокирует! / обзор и анализ сериала ч.1'
        videolink = self.cleanStr(str(videosLinks[videoTitle]))
        print(videolink)
        self.getVideoInfo(videolink, driver)
        #print(videolink)


        
        