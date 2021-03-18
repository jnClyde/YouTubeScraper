from Scraper import Scraper


def main():
    path = 'https://www.youtube.com/channel/UCu-__sHtOJpcjKoeJ60LoSA'
    YTScraper = Scraper(path)
    YTScraper.startScraper()

#---------------------------------------------------------------------------------------------------------------------------#

if (__name__ == "__main__"):
    main()

#---------------------------------------------------------------------------------------------------------------------------#
