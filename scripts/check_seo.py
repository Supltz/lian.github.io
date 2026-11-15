"""Check the built site's discovery metadata before deployment."""

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonical = None
        self.title = ''
        self.schemas = []
        self.in_title = False
        self.in_schema = False
        self.schema_text = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta[attrs.get('name', '')] = attrs.get('content', '')
        elif tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')
        elif tag == 'title':
            self.in_title = True
        elif tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_text = ''

    def handle_data(self, text):
        if self.in_title:
            self.title += text
        if self.in_schema:
            self.schema_text += text

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'script' and self.in_schema:
            self.schemas.append(json.loads(self.schema_text))
            self.in_schema = False


def check(destination):
    home = 'https://supltz.github.io/lian.github.io/'
    html = (destination / 'index.html').read_text()
    head = Head()
    head.feed(html)
    assert head.canonical == home, 'Homepage canonical is incorrect'
    assert 'Tangzheng Lian' in head.title and "King's College London" in head.title
    assert head.meta.get('description', '').startswith('Tangzheng Lian')
    assert head.meta.get('google-site-verification'), 'Search Console verification tag is missing'
    assert 'noindex' not in head.meta.get('robots', '').lower()
    assert 'cv.pdf' not in html and 'Teaching Assistant' not in html
    assert not (destination / 'cv.pdf').exists(), 'Private CV must not be published'
    profile = next(s for s in head.schemas if s.get('@type') == 'ProfilePage')
    person = profile['mainEntity']
    assert person['@type'] == 'Person' and person['name'] == 'Tangzheng Lian'
    assert person['url'] == home
    assert len(person['sameAs']) == 3 and len(set(person['sameAs'])) == 3
    assert all(url.startswith('https://') for url in person['sameAs'])
    image = urlparse(person['image']).path.removeprefix(urlparse(home).path)
    assert (destination / image).is_file(), 'Structured-data portrait does not exist'
    namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap = ET.parse(destination / 'sitemap.xml')
    urls = [node.text for node in sitemap.findall('sm:url/sm:loc', namespace)]
    assert home in urls, 'Homepage is missing from sitemap'
    assert urljoin(home, 'publications/') in urls
    assert urljoin(home, 'blog/first-research-note/') in urls
    assert len(urls) == len(set(urls)), 'Sitemap contains duplicate URLs'
    for url in urls:
        assert url.startswith(home), 'Sitemap URL points outside the site'
        assert 'cv.pdf' not in url and '404.html' not in url
        relative = url.removeprefix(home)
        assert (destination / relative / 'index.html').is_file(), url
    robots = (destination / 'robots.txt').read_text()
    assert 'Sitemap: ' + urljoin(home, 'sitemap.xml') in robots
    assert 'Disallow: /' not in robots
    print(f'PASS: title, description, canonical, verification, Person schema, {len(urls)} sitemap URLs, robots declaration and CV removal.')


if __name__ == '__main__':
    check(Path(sys.argv[1] if len(sys.argv) > 1 else 'public'))
