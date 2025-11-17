import datetime
import os

# Just update the timestamp in feed.xml
feed_path = "docs/feed.xml"
with open(feed_path, "r", encoding="utf-8") as f:
    content = f.read()

now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
content = content.split("<lastBuildDate>")[0] + f"<lastBuildDate>{now}</lastBuildDate>" + content.split("</lastBuildDate>")[1]

with open(feed_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Feed timestamp updated: {now}")
