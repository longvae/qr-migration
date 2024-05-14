import requests
import urllib.parse


#url = 'https://disneyparks.disney.go.com/'
url = 'https://qr-test.1dydx.com/test10'

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1',
}

try:
    response = requests.head(url, headers=headers, allow_redirects=True)
    print(response.url)
except requests.RequestException as e:
    print(e)

