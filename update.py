import requests, xml.etree.ElementTree as ET, datetime, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'IceMelterBot/1.0'}

SITES = [
    ("Drop Site", "https://dropsitenews.substack.com", ".post-preview-title a", ".post-preview-excerpt"),
    ("Ground News", "https://ground.news/blindspot", "[data-testid='story-title'] a", "[data-testid='story-summary']"),
    ("Intercept", "https://theintercept.com", "h3 a", ".post-excerpt")
]

def fetch():
    items = []
    for name, url, title_sel, desc_sel in SITES:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.select(title_sel)[:3]:
                link = urljoin(url, a.get('href', ''))
                desc_tag = a.find_next(desc_sel)
                desc = desc_tag.get_text(strip=True)[:200] + '...' if desc_tag else ''
                items.append({
                    'title': f"[{name}] {a.get_text(strip=True)}",
                    'link': link,
                    'desc': desc,
                    'date': datetime.datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error {name}: {e}")
    return items

def build_rss(items):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for t in ['title', 'link', 'description']:
        ET.SubElement(channel, t).text = {
            'title': 'Ice Melter — Indie News',
            'link': 'https://sacramentalstudios.github.io/ice-melter',
            'description': 'Truth that melts the ice.'
        }[t]
    ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    for i in items:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = i['title']
        ET.SubElement(item, 'link').text = i['link']
        ET.SubElement(item, 'description').text = f"<![CDATA[<strong>{i['title'].split(']')[0][1:]}:</strong> {i['desc']}]]>"
        ET.SubElement(item, 'pubDate').text = i['date']
        ET.SubElement(item, 'guid').text = i['link']
    return ET.tostring(rss, encoding='utf-8', method='xml').decode()

items = fetch()
os.makedirs('docs', exist_ok=True)
open('docs/feed.xml', 'w', encoding='utf-8').write(build_rss(items))
print("Ice Melter feed updated!")
