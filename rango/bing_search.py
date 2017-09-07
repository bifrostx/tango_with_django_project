import requests


def read_bing_key():

    bing_api_key = None

    try:
        with open('rango/bing.key', 'r') as f:
            bing_api_key = f.readline()
    except:
        raise IOError('bing.key file not found')

    return bing_api_key


def bing_search(query):

    url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
    # query string parameters
    payload = {'q': query, 'mkt': 'en-US', 'count': '10'}
    # custom headers
    key = read_bing_key()
    headers = {'Ocp-Apim-Subscription-Key': key}
    # make GET request
    r = requests.get(url, params=payload, headers=headers)
    # get JSON response
    d = r.json()
    results = []
    for result in d['webPages']['value']:
        results.append({'title': result['name'],
                        'link': result['displayUrl'],
                        'summary': result['snippet']})
    return results


def main():
    query = input("Please input keyword to search>")
    r = bing_search(query)
    return r

if __name__ == "__main__":
    main()


