import os
import feedparser
from notion_client import Client
from datetime import datetime
import pytz

def main():
    """Fetch RSS feeds and add articles to Notion database"""
    
    # Get environment variables
    notion_api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_api_key or not database_id:
        print("⚠️ Missing required environment variables: NOTION_API_KEY or NOTION_DATABASE_ID")
        return
    
    # Initialize Notion client
    notion = Client(auth=notion_api_key)
    
    # List of RSS feeds to monitor (tech news sources)
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
    ]
    
    print("📡 Fetching RSS feeds...")
    articles_added = 0
    
    for feed_url in rss_feeds:
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            print(f"✅ Fetched {len(feed.entries)} articles from {feed.feed.get('title', feed_url)}")
            
            # Process only the latest 5 articles per feed
            for entry in feed.entries[:5]:
                try:
                    title = entry.get("title", "No Title")
                    link = entry.get("link", "")
                    published = entry.get("published", "")
                    description = entry.get("summary", "")[:500]  # Limit description length
                    
                    # Check if article already exists
                    existing = notion.databases.query(
                        database_id=database_id,
                        filter={
                            "property": "URL",
                            "url": {
                                "equals": link
                            }
                        }
                    )
                    
                    if existing.get("results"):
                        continue  # Article already exists
                    
                    # Add article to Notion
                    notion.pages.create(
                        parent={"database_id": database_id},
                        properties={
                            "Title": {
                                "title": [
                                    {
                                        "text": {
                                            "content": title
                                        }
                                    }
                                ]
                            },
                            "URL": {
                                "url": link
                            },
                            "Status": {
                                "select": {
                                    "name": "Pending"
                                }
                            },
                            "Source": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": feed.feed.get('title', 'RSS Feed')
                                        }
                                    }
                                ]
                            }
                        }
                    )
                    articles_added += 1
                    print(f"  ➕ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️ Error processing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching feed {feed_url}: {e}")
            continue
    
    print(f"\n🎉 Completed! Added {articles_added} new articles to Notion database.")

if __name__ == "__main__":
    main()
