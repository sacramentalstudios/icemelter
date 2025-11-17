from requests_html import HTMLSession
import xml.etree.ElementTree as ET
import datetime, os
from urllib.parse import urljoin

session = HTMLSession()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

SITES = [
    ("Drop Site", "https://dropsitenews.substack.com", "https://dropsitenews.substack.com/feed", "item title", "item description"),
    ("Ground News", "https://ground.news/blindspot", None, ".story-title a", ".story-summary"),
    ("Intercept", "https://theintercept.com", None, "h3 a", ".post-excerpt")
]

def fetch():
    items = []
    for name, url, feed_url, title_sel, desc_sel in SITES:
        try:
            if feed_url:  # Use RSS for Substack (bypasses block)
                r = session.get(feed_url)
                soup = r.html.html  # Rendered HTML
                soup_obj = BeautifulSoup(soup, 'html.parser')
                for entry in soup_obj.select(title_sel)[:3]:
                    title = entry.get_text(strip=True)
                    link = entry.get('href', urljoin(feed_url, entry.get('href', '')))
                    desc = soup_obj.select_one(f"{title_sel} + {desc_sel}").get_text(strip=True)[:200] + '...' if soup_obj.select(f"{title_sel} + {desc_sel}") else ''
                    items.append({'title': f"[{name}] {title}", 'link': link, 'desc': desc, 'date': datetime.datetime.now().isoformat()})
            else:  # HTML scrape with JS render
                r = session.get(url)
                r.html.render(timeout=20)  # Render JS
                for a in r.html.find(title_sel)[:3]:
                    title = a.text.strip()
                    link = a.attrs.get('href', '')
                    if link: link = urljoin(url, link)
                    desc_elem = a.find_next(desc_sel)
                    desc = desc_elem[0].text.strip()[:200] + '...' if desc_elem else ''
                    items.append({'title': f"[{name}] {title}", 'link': link, 'desc': desc, 'date': datetime.datetime.now().isoformat()})
        except Exception as e:
            print(f"Error {name}: {e}")
    return items

def build_rss(items):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'Ice Melter — Indie News'
    ET.SubElement(channel, 'link').text = 'https://sacramentalstudios.github.io/ice-melter'
    ET.SubElement(channel, 'description').text = 'Truth that melts the ice.'
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
with open('docs/feed.xml', 'w', encoding='utf-8') as f:
    f.write(build_rss(items))
print(f"Ice Melter updated with {len(items)} items!")
