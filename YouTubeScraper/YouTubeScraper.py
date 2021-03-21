from Scraper import Scraper


def main():
    # path = 'https://www.youtube.com/channel/UCu-__sHtOJpcjKoeJ60LoSA'
    # name = 'Черный кабинет'
    # yt_scraper = Scraper(path, name)
    # yt_scraper.start_scraper()

    path1 = 'https://www.youtube.com/channel/UCIupfj3rki6dfjQqFKbXzMA'
    name1 = 'Cut the crab'
    yt_scraper1 = Scraper(path1, name1)
    yt_scraper1.start_scraper()

    path2 = 'https://www.youtube.com/user/KINOKRITIKA'
    name2 = 'Илья Бунин'
    yt_scraper2 = Scraper(path2, name2)
    yt_scraper2.start_scraper()


# ---------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------------------------------------------------------#
