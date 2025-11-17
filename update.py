import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import os

try:
    import feedparser
    print("✓ feedparser imported successfully")
except ImportError as e:
    print(f"✗ Import error for feedparser: {e}")
    raise

# Official RSS URLs (tested — these work)
RSS_FEEDS = {
    "Drop Site News": "https://dropsitenews.substack.com/feed",
    "Ground News": "https://ground.news/rss",  # General RSS, includes Blindspot-style
    "The Intercept": "https://theintercept.com/feed/"
}

def fetch_rss_items():
    all_items = []
    print(f"Fetching from {len(RSS_FEEDS)} RSS feeds...")
    for source, rss_url in RSS_FEEDS.items():
        print(f"Trying {source} from {rss_url}...")
        try:
            feed = feedparser.parse(rss_url)
            if feed.bozo:  # Parse error?
                print(f"✗ Parse error for {source}: {feed.bozo_exception}")
                continue
            entries = feed.entries
            print(f"✓ Got {len(entries)} entries from {source}")
            for entry in entries[:3]:  # Top 3
                title = entry.title
                link = entry.link
                desc = (entry.summary or entry.description or "")[:200] + "..." if len(entry.summary or entry.description or "") > 200 else (entry.summary or entry.description or "")
                pub_date = entry.published if hasattr(entry, 'published') else datetime.datetime.now().isoformat()
                all_items.append({
                    'title': f"[{source}] {title}",
                    'link': link,
                    'description': desc,
                    'pubDate': pub_date
                })
                print(f"  - Added: {title[:50]}...")
        except Exception as e:
            print(f"✗ Full error for {source}: {e}")
    print(f"Total items fetched: {len(all_items)}")
    return all_items

def generate_merged_rss(items):
    print("Generating RSS XML...")
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Ice Melter — Merged Indie News"
    ET.SubElement(channel, "link").text = "https://sacramentalstudios.github.io/ice-melter"
    ET.SubElement(channel, "description").text = "Merged RSS from Drop Site, Ground News, The Intercept. Auto-updated every 15 mins."
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Sort by pub date (newest first)
    sorted_items = sorted(items, key=lambda x: x['pubDate'], reverse=True)[:15]

    for item in sorted_items:
        rss_item = ET.SubElement(channel, "item")
        ET.SubElement(rss_item, "title").text = item['title']
        ET.SubElement(rss_item, "link").text = item['link']
        ET.SubElement(rss_item, "description").text = f"<![CDATA[<strong>{item['title'].split(']')[0][1:]}:</strong><br/>{item['description']}]]>"
        ET.SubElement(rss_item, "pubDate").text = item['pubDate']
        ET.SubElement(rss_item, "guid").text = item['link']
    rough_string = ET.tostring(rss, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_str = reparsed.toprettyxml(indent="  ")
    print(f"✓ RSS generated with {len(sorted_items)} items")
    return xml_str

# Run it
print("Starting Ice Melter update...")
items = fetch_rss_items()
if not items:
    print("⚠️ No items fetched — feed will be empty!")
else:
    rss_xml = generate_merged_rss(items)
    os.makedirs("docs", exist_ok=True)
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"✓ Wrote {len(items)} items to docs/feed.xml")
print("Ice Melter update complete!")
