import feedparser
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import os

print("Fetching immigration-only RSS...")

# Immigration-focused RSS feeds
RSS_FEEDS = {
    "The Intercept": "https://theintercept.com/tag/immigration/feed/",
    "Ground News": "https://ground.news/interest/immigration/rss",
    "Drop Site News": "https://dropsitenews.substack.com/feed",  # We'll filter manually if needed
    "ProPublica Immigration": "https://www.propublica.org/feeds/topics/immigration.rss",
    "AP Migration": "https://apnews.com/hub/migration/rss"
}

def fetch():
    items = []
    for name, url in RSS_FEEDS.items():
        print(f"Fetching {name}...")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                desc = (entry.get('summary') or entry.get('description') or "")[:200] + "..."
                items.append({
                    'title': f"[{name}] {title}",
                    'link': link,
                    'desc': desc,
                    'date': entry.get('published') or datetime.datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error {name}: {e}")
    print(f"Got {len(items)} immigration stories")
    return items

def build(items):
    rss = ET.Element("rss", version="2.0")
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "Ice Melter — Immigration Only"
    ET.SubElement(ch, "link").text = "https://sacramentalstudios.github.io/ice-melter"
    ET.SubElement(ch, "description").text = "Immigration news only. Border, policy, raids, asylum."
    
    for i in sorted(items, key=lambda x: x['date'], reverse=True):
        item = ET.SubElement(ch, "item")
        ET.SubElement(item, "title").text = i['title']
        ET.SubElement(item, "link").text = i['link']
        ET.SubElement(item, "description").text = f"<![CDATA[<strong>{i['title'].split(']')[0][1:]}:</strong> {i['desc']}]]>"
        ET.SubElement(item, "pubDate").text = i['date']
        ET.SubElement(item, "guid").text = i['link']
    
    return minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")

items = fetch()
os.makedirs("docs", exist_ok=True)
with open("docs/feed.xml", "w", encoding="utf-8") as f:
    f.write(build(items))
print("Immigration feed updated!")
