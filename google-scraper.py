#!/usr/bin/env python
# coding: utf-8

# ### Web Scraping the `Motherload of Search`
# 
# Web scraping is not all rosy, especially when dealing directly with `Google`. 
# 
# The functions created here however work together to create as much a seamless process as possible. The techniques all major in trying to avoid getting banned by the target website. 

# #### Scrape Google Search suggestions and autocomplete

# In[15]:


def get_autocomplete(query):
    import requests, json 
    URL=f"http://suggestqueries.google.com/complete/search?client=firefox&q={query}" 
    headers = {'User-agent':'Mozilla/5.0'} 
    response = requests.get(URL, headers=headers) 
    result = json.loads(response.content.decode('utf-8')) 
    return result[1]


# ##### Use Case

# In[16]:


k = get_autocomplete("Sudan")
k


# #### Multipage Web Scraper utitlity functions

# In[17]:


from collections import defaultdict
from urllib.parse import quote
from httpx import Client, Limits
from parsel import Selector
import random
import pandas as pd
limits = Limits(max_keepalive_connections=10000, max_connections=1000)
"""setting up five different user agents in the headers object from which one is chosen at random"""
client = Client(
    headers={
        "User-Agent": random.choice(
            [
                
                'Mozilla/5.0 (Windows NT 10.0; Win 64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            ]),
        
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
        "Dnt": "1",
        "Upgrade-Insecure-Requests": "1",
        "Referer" : "https://news.google.com/",
    },
    follow_redirects=True,
    http2=True,
    limits=limits
)

def parse_search_results(selector: Selector):
    """parse search results from google search page"""
    results = []
    for element in selector.xpath("//h1[contains(text(),'Search Results')]/following-sibling::div[1]/div"):
        page_title = element.xpath(".//h3/text()").get()
        site_title = element.xpath(".//div//div/span/text()").get()
        url = element.xpath(".//h3/../@href").get()
        text = "".join(element.xpath(".//div[@data-sncf=1]//text()").getall())
        if not page_title or not url:
            continue
        url = url.split("://")[1].replace("www.", "")
        results.append([page_title, site_title, url, text])
    return results

import time
def scrape_search(query: str, page=1):
    """scrape search results for a given keyword"""
    # retrieve the SERP
    url = f"https://www.google.com/search?hl=en&q={quote(query)}" + (f"&start={10*(page-1)}" if page > 1 else "")
    results = defaultdict(list)
    response = client.get(url, )
    assert response.status_code == 200,f"Failed response with status code -> {response.status_code}"
    # parse SERP for search result data
    selector = Selector(response.text)
    results["search"].extend(parse_search_results(selector))
    time.sleep(1)
    return dict(results)


# In[18]:


def resultSetup(minNumOfPages, maxNumOfPages, searchKey, sleep = 10):
    results = []
    for page in range(minNumOfPages,maxNumOfPages+1):
        page_result = scrape_search(searchKey, page=page)
        results.append(page_result["search"])
        print(f"{page}/{maxNumOfPages} scraped for search : {searchKey}")
        time.sleep(10)
    result_list = [item for sublist in results for item in sublist]
    
    dataframe = pd.DataFrame(result_list, columns = ["page_title", "site_title", "page_link", "short_description_of_page"])
    return dataframe
    


# #### Use Case

# In[19]:


sudanese_data = pd.DataFrame()


# In[20]:


# Scrape from 4 pages with a 10 second delay between each request
scraped_results = resultSetup(1, 4, "Sudan", 10)
# Appending our result to the full df
sudanese_data.append(scraped_results)


# In[ ]:




