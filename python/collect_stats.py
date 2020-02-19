import time
import requests
from bs4 import BeautifulSoup

def collect_table(stat: str, season: int, time_period: str = "eon", tournament="str"):
    """This is the function for scraping a table from the PGA site.

    An example site is available here: 
    https://www.pgatour.com/content/pgatour/stats/stat.109.y2020.eon.t005.html

    Parameters
    ----------
    stat: str
        This is the specific stat you're looking at. It forms the 
    """