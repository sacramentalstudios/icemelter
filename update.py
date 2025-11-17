import feedparser
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import os

print("Starting Ice Melter RSS update...")

RSS_FEEDS = {
    "Drop Site News": "https://dropsitenews.substack.com/feed",
    "The Intercept": "https://theintercept.com/feed/",
    "Ground News": "https://ground.news/rss"
}

def fetch():
    items = []
    for name, url in RSS_FEEDS.items():
        print(f"Fetching {name}...")
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"No entries in {name}")
                continue
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                desc = (entry.get('summary') or entry.get('description') or "")[:200] + "..."
                date = entry.get('published') or datetime.datetime.now().isoformat()
                items.append({
                    'title': f"[{name}] {title}",
                    'link': link,
                    'desc': desc,
                    'date': date
                })
                print(f"  + {title[:60]}...")
        except Exception as e:
            print(f"Error {name}: {e}")
    print(f"Total: {len(items)} stories")
    return items

def build(items):
    rss = ET.Element("rss", version="2.0")
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "Ice Melter — Indie News"
    ET.SubElement(ch, "link").text = "https://sacramentalstudios.github.io/ice-melter"
    ET.SubElement(ch, "description").text = "Truth that melts the ice."
    
    for i in sorted(items, key=lambda x: x['date'], reverse=True):
        item = ET.SubElement(ch, "item")
        ET.SubElement(item, "title").text = i['title']
        ET.SubElement(item, "link").text = i['link']
        ET.SubElement(item, "description").text = f"<![CDATA[<strong>{i['title'].split(']')[0][1:]}:</strong> {i['desc']}]]>"
        ET.SubElement(item, "pubDate").text = i['date']
        ET.SubElement(item, "guid").text = i['link']
    
    xml = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    print("RSS built.")
    return xml

items = fetch()
os.makedirs("docs", exist_ok=True)
with open("docs/feed.xml", "w", encoding="utf-8") as f:
    f.write(build(items))
print("Ice Melter feed updated!")
