"""
A bit of a hacky way to generate a demo of the booking system frontend.
"""

import os
import re
import time
from multiprocessing import Process

import requests

# Global variables to keep track of things
links = ['/']
visited = []
skip = ['/etikettserver', '/inventar/print/*', '/logout']
skipped = []
cookies = {}


def launch_app():
    """
    Launch the app with the environment variables set above.

    This needs to be called in a separate process, as it blocks the main thread.
    """
    os.environ['DEBUG'] = 'true'
    os.environ['MOCK_DATA'] = 'true'
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(root, 'BookingSystem', 'app.py')
    os.system(f'python {app_path}')


def get_html(url):
    """Get the html from the given url, and append the new links to the links list."""
    r = requests.get(f'http://localhost:5000{url}', allow_redirects=True, cookies=cookies)
    html = r.text
    new_links = get_links(html)

    for l in new_links:
        if l not in links:
            links.append(l)

    visited.append(url)
    for s in skipped:
        html = html.replace(s, '#')

    # Prepend every relative link for GitHub Pages
    html = html.replace('href="/', 'href="/FeideUtstyrbase/')
    html = html.replace('src="/', 'src="/FeideUtstyrbase/')
    html = html.replace('https://localhost/', 'https://sondregronas.github.io/FeideUtstyrbase/')

    return html


def get_links(html):
    """
    Get all the links from the given html, and return them as a list without duplicates.

    Add skipped links to the skipped list (if they match the skip regex).
    Skips all static resources.
    """
    global skipped

    links = re.compile(r'href="(\/[^"]*)"').findall(html)
    for s in skip:
        old = links.copy()
        links = [x for x in links if not re.match(s.replace('*', '.*'), x)]
        if len(links) != len(old):
            skipped.extend(list(set(old) - set(links)))
            skipped = list(set(skipped))
    return list(set([x for x in links if not re.match(r'/static/.*', x)]))


def generate_demo():
    """Generate the demo by crawling the site."""
    while visited != links:
        for link in links:
            if link not in visited:
                if '?' in link:
                    visited.append(link)
                    continue

                html = get_html(link)
                if link == '/':
                    path = 'index.html'
                else:
                    path = link[1:]
                    if '.' not in path:
                        path += '/index.html'

                os.makedirs(os.path.dirname(f'demo/{path}'), exist_ok=True)
                with open(f'demo/{path}', 'w+', encoding='utf-8') as f:
                    f.write(html)
                    abspath = os.path.abspath(f.name)
                    print(f'Wrote {abspath}')


def set_demo_bulletin():
    """Set the bulletin to the given text."""
    global cookies

    data = {
        'bulletin_title': 'Static Admin Preview',
        'bulletin': f'Nothing is functional, no data is stored. (Automatically generated {time.strftime("%d.%m.%Y")})'
    }
    cookies = requests.get('http://localhost:5000/demo-login', allow_redirects=True).cookies
    requests.put('http://localhost:5000/bulletin', data=data, cookies=cookies)


if __name__ == '__main__':
    p = Process(target=launch_app)
    p.start()
    # Wait for the app to start
    time.sleep(5)
    set_demo_bulletin()
    generate_demo()
    p.terminate()
