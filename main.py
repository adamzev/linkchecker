import mimetypes
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, SoupStrainer


def is_url_image(url):
    mimetype, _ = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))


def get_links(doc):
    links = SoupStrainer('a')
    return [tag['href'] for tag in BeautifulSoup(
        doc, "html.parser", parse_only=links) if tag.get('href')]


def recurse_links(base_domain, to_visit, visited):
    broken = []
    # base: to visit is empty, just return
    if not to_visit:
        return []
    current_addr = to_visit.pop()
    print(f"{len(visited)} of {len(visited) + len(to_visit)} | {current_addr}")
    if is_url_image(current_addr):
        print("checking head")
        response = requests.head(current_addr)
    else:
        response = requests.get(current_addr)
    if response.status_code != requests.codes.ok:
        print("____________________________")
        print(response.status_code, current_addr)
        print("____________________________")
        broken = [current_addr]
    clean_links = []
    if current_addr.startswith(base_domain):
        raw_links = get_links(response.text)
        for link in raw_links:
            # split on a pound sign and just take the first part to avoid links within pages
            link = link.split('#', 1)[0]
            if link[0:4] == "http":
                clean_links.append(link)
            elif link[0:6] == "mailto":
                pass
            else:

                clean = urljoin(current_addr, link)
                clean_links.append(clean)

    to_visit.update(clean_links)
    visited.add(current_addr)
    time.sleep(0.4)
    return broken + recurse_links(base_domain, to_visit - visited, visited)


def main():
    broken = recurse_links("http://www.tutordelphia.com",
        set(["http://www.tutordelphia.com"]), set())
    print(broken)


if __name__ == "__main__":
    main()
