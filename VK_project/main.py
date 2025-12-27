import requests
import argparse
from urllib.parse import urlparse
from environs import Env


def is_shorten_link(token, url):
    parsed_url = urlparse(url)
    link_key = parsed_url.path.lstrip('/')
    payload = {
        'v': '5.199',
        'access_token': token,
        'key': link_key,
        'interval': 'forever',
        'extended': 0,
    }
    response = requests.get('https://api.vk.ru/method/utils.getLinkStats', params=payload)
    response.raise_for_status()
    link_stats = response.json()
    return 'response' in link_stats
        

def shorten_link(token, url):
    payload = {
        'v': '5.199', 
        'access_token': token,
        'url': url,
    }
    response = requests.get('https://api.vk.ru/method/utils.getShortLink', params=payload)
    response.raise_for_status() 
    short_link = response.json()
    if 'error' in short_link:
        error_message = short_link['error'].get('error_msg', 'Unknown VK API error')
        raise requests.exceptions.HTTPError(f"VK API Error: {error_message}")
    if 'response' in short_link and 'short_url' in short_link['response']:
        return short_link['response']['short_url']
    else:
        raise ValueError("Unexpected response format from VK API")


def count_clicks(token, short_url):
    parsed_url = urlparse(short_url)
    link_key = parsed_url.path.lstrip('/')  
    payload = {
        'v': '5.199',
        'access_token': token,
        'key': link_key,
        'interval': 'forever',
        'extended': 0,
    }
    response = requests.get('https://api.vk.ru/method/utils.getLinkStats', params=payload)
    response.raise_for_status() 
    link_stats = response.json()
    if 'error' in link_stats:
        error_message = link_stats['error'].get('error_msg', 'Unknown VK API error')
        raise requests.exceptions.HTTPError(f"VK API Error: {error_message}")
    if 'response' in link_stats and 'stats' in link_stats['response']:
        stats = link_stats['response']['stats']
        if stats and len(stats) > 0:
            total_clicks = sum(interval_stats.get('views', 0) for interval_stats in stats)
            return total_clicks
    return 0


def main():
    env = Env()
    env.read_env()
    token = env('VK_TOKEN')
    parser = argparse.ArgumentParser(
        description='Сокращение ссылок и подсчет кликов через VK API'
    )
    parser.add_argument(
        'user_url',
        help='URL для сокращения или подсчета кликов'
    )
    args = parser.parse_args()
    print(args.user_url)
    try:
        if is_shorten_link(token, args.user_url):
            clicks_count = count_clicks(token, args.user_url)
            print(f"Total clicks: {clicks_count}")
        else:
            short_url = shorten_link(token, args.user_url)
            print(f"Short URL: {short_url}")
    except requests.exceptions.HTTPError as error:
        print(f'Can not get data from server:\n{error}')
    except Exception as error:
        print(f'An unexpected error occurred:\n{error}')
        
        
if __name__ == '__main__':
    main()