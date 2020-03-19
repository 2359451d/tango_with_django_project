import json
import requests

# add key1 to file bing.key
# acquire the key
def read_bing_key():
   
    bing_api_key = None
   
    try:
        with open('bing.key','r') as f:
            bing_api_key = f.readline().strip()
    except:
        try:
            with open('../bing.key','r') as f:
                bing_api_key = f.readline().strip()
        except:
            raise IOError('bing.key file not found')

    if not bing_api_key:
        raise KeyError('Bing key not found')
    return bing_api_key

def run_query(search_term):
    # search_terms -> string
    # default: return top 10 results
    bing_key = read_bing_key()
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    headers = {'Ocp-Apim-Subscription-Key': bing_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    # # Issue the request, given the details above.
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    # return the response as json format
    search_results = response.json()

    # parse the json content

    results = []
    for result in search_results['webPages']['value']:
        results.append({
            'title': result['name'],
            'link': result['url'],
            'summary':result['snippet']})
    return results

# run the script
# def main():
#     search_terms = input("Please enter the query content:")
#     results = run_query(search_terms)
#     for result in results:
#         print("Title: {0}, url: {1}, content: {2}".format(result['title'],result['link'],result['summary']))
#         print("-------------------->")

# if __name__=='__main__':
#     main()