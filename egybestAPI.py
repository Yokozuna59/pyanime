from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium import common
import json
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import sys



class EgybestAPI() :
    
    BASE_URL = "https://mega.egybest.dev/"
    HTML_PARSER = "html.parser"


    def search(query) :
        search_url = "https://mega.egybest.dev/explore/" 
        result_page = requests.get(search_url, params = {"q": query})
        
        soup = BeautifulSoup(result_page.content, EgybestAPI.HTML_PARSER)
        
        results_divs = soup.find("div", id="movies").findAll("a", class_="movie")
        
        results = []
        
        for result_div in results_divs :
            result = {}
            
            result["link"] = result_div["href"]
            result["title"] = result_div.find("span", class_="title").text
            
            results.append(result)
        
        return results
    
    
    
    
    def is_movie(result) :
        return not EgybestAPI.contains_seasons(result)
    
    
    def contains_seasons(result) :
        link = result["link"]
        result_page = requests.get(link)
        
        soup = BeautifulSoup(result_page.content, EgybestAPI.HTML_PARSER)
        
        mboxes = soup.find_all("div", class_="mbox")
        
        for mbox in mboxes :
            strong_tag = mbox.find("strong")
            if strong_tag != None :
                if "مواسم" in strong_tag.text :
                    return True
        
        return False
    
    
    
    def get_seasons(result) :
        link = result["link"]
        result_page = requests.get(link)
        
        soup = BeautifulSoup(result_page.content, EgybestAPI.HTML_PARSER)
        
        mboxes = soup.find("div", id="mainLoad").find_all("div", class_="mbox")
        
        for mbox in mboxes :
            strong_tag = mbox.find("strong")
            if strong_tag != None :
                if "مواسم" in strong_tag.text :
                    mboxes = mbox 
                    break
        
        seasons_tags = mboxes.find("div", class_="contents movies_small").find_all("a")
        
        seasons = []
        
        for season_tag in seasons_tags :
            season = {}
            
            season["link"] = season_tag["href"]
            season["title"] = season_tag.find("span", class_="title").text
            
            seasons.append(season)
            
        return seasons[::-1]
        
        
        
        
    def get_episodes(result) :
        link = result["link"]
        result_page = requests.get(link)
        
        soup = BeautifulSoup(result_page.content, EgybestAPI.HTML_PARSER)
        
        mboxes = soup.find("div", id="mainLoad").find_all("div", class_="mbox")
        
        for mbox in mboxes :
            strong_tag = mbox.find("strong")
            if strong_tag != None :
                if "حلقات" in strong_tag.text :
                    mboxes = mbox 
                    break
        
        episode_tags = mboxes.find("div", class_="movies_small") if mboxes.find("div", class_="contents movies_small") == None else mboxes.find("div", class_="contents movies_small")
        episode_tags = episode_tags.find_all("a")
        
        episodes = []
        
        for episode_tag in episode_tags :
            episode = {}
            
            episode["link"] = episode_tag["href"]
            episode["title"] = episode_tag.find("span", class_="title").text
            
            episodes.append(episode)
        
        return episodes[::-1]
        
    
    
    def get_m3u8_link(result) :
        link = result["link"]
        result_page = requests.get(link)
        
        soup = BeautifulSoup(result_page.content, EgybestAPI.HTML_PARSER)
        
        frame_link = EgybestAPI.BASE_URL[:-1] + soup.find("iframe", class_="auto-size")["src"]
        
        driver_name = "chromedriver.exe" if sys.platform == "win32" else "chromedriver"
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        service = Service(f"drivers/{driver_name}")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(service=service, options=options, desired_capabilities=caps)
        driver.get(frame_link)

        driver.find_element_by_xpath('/html/body/div/i').click()
        
        pageLoaded = False
        while not pageLoaded :
            try :
                soup = BeautifulSoup(driver.page_source, EgybestAPI.HTML_PARSER)
                source = soup.find("video", id = "video_html5_api").find("source")["src"]
                pageLoaded = True
            except AttributeError :
                time.sleep(0.75)
                continue
            
        
        source = "https://mega.egybest.dev" + source
        
        
        m3u8_file = requests.get(source)
        m3u8_file = m3u8_file.text.split("\n")
        
        m3u8_file = list(filter(lambda x : x != "", m3u8_file))
        return m3u8_file[-1]
        
        
        