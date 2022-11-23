from datetime import datetime, timedelta 
import time
import requests, pandas, lxml
from lxml import html


def subdomain(symbol, start, end, filter_='history'):
    subdoma='/quote/{0}/history?period1={1}&period2={2}&interval=1d&includeAdjustedClose=false'
    subdomain = subdoma.format(symbol, start, end, filter_)
    return subdomain
 
def header_function(subdomain):
    hdrs =  {"authority": "finance.yahoo.com",
          "method": "GET",
          "path": subdomain,
          "scheme": "https",
          "accept": "text/html",
          "accept-encoding": "gzip, deflate, br",
          "accept-language": "en-US,en;q=0.9",
          "cache-control": "no-cache",
          "dnt": "1",
          "pragma": "no-cache",
          "sec-fetch-mode": "navigate",
          "sec-fetch-site": "same-origin",
          "sec-fetch-user": "?1",
          "upgrade-insecure-requests": "1",
          "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"}

    return hdrs
    
def scrape_page(url, header):
    page = requests.get(url, headers=header)
    element_html = html.fromstring(page.content) #Read the webpage content using the lxml.html module
    table = element_html.xpath('//table') #Use the xpath method to isolate the price history table
    table_tree = lxml.etree.tostring(table[0], method='xml') # Turn the table element into a byte string with etree module
    panda = pandas.read_html(table_tree)
    return panda

def scrape_with_limit(lastNdays, symbol):
    if lastNdays < 100:
        dt_start = datetime.today() - timedelta(days=150)
        dt_end = datetime.today()
        start = str(int(time.mktime(dt_start.timetuple())))
        end = str(int(time.mktime(dt_end.timetuple())))
        sub = subdomain(symbol, start, end)
        header = header_function(sub)
        price_history = scrape_page('https://finance.yahoo.com' + sub, header)[0].head(100)
        return price_history
    else:
        df = pd.DataFrame()
        for i in range(0, lastNdays + 100, 100): # + extra 100 to avoid miss 'ten days' data
            dt_start = datetime.today() - timedelta(days=i + 150)
            dt_end = datetime.today() - timedelta(days=i)
            start = str(int(time.mktime(dt_start.timetuple())))
            end = str(int(time.mktime(dt_end.timetuple())))
            sub = subdomain(symbol, start, end)
            header = header_function(sub)
            price_history = scrape_page('https://finance.yahoo.com' + sub, header)[0].head(100)
            df = pd.concat([df,price_history])
        return df.head(lastNdays)
if __name__ == '__main__':
    symbol = 'AAPL'
    re = scrape_with_limit(365, symbol)
#     dt_start = datetime.today() - timedelta(days=250)
#     dt_end = datetime.today() - timedelta(days=100)
#     start = str(int(time.mktime(dt_start.timetuple())))
#     end = str(int(time.mktime(dt_end.timetuple())))
#     sub = subdomain(symbol, start, end)
#     header = header_function(sub)
#     price_history = scrape_page('https://finance.yahoo.com' + sub, header)
