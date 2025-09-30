import os
import argparse
import requests
from notion_client import Client

def generate_tweet_with_perplexity(article_title, article_url, api_key):
    """Generate a tweet using Perplexity API"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Generate an engaging tweet about this article:
Title: {article_title}
URL: {article_url}

Requirements:
- Keep it under 280 characters
- Make it interesting and engaging
- Include relevant hashtags (max 2)
- Don't include the URL in the tweet text
- Write in English"""

    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        tweet = data["choices"][0]["message"]["content"].strip()
        
        # Remove quotes if present
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]
        
        return tweet
        
    except Exception as e:
        print(f"  ⚠️ Error generating tweet with Perplexity: {e}")
        return None

def main():
    """Generate tweets for pending articles in Notion database"""
    
    parser = argparse.ArgumentParser(description="Generate tweets from Notion articles")
    parser.add_argument("--limit", type=int, default=5, help="Number of articles to process")
    args = parser.parse_args()
    
    # Get environment variables
    notion_api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not notion_api_key or not database_id:
        print("⚠️ Missing required environment variables: NOTION_API_KEY or NOTION_DATABASE_ID")
        return
    
    if not perplexity_api_key:
        print("⚠️ Missing PERPLEXITY_API_KEY - will not generate tweets")
        return
    
    # Initialize Notion client
    notion = Client(auth=notion_api_key)
    
    print(f"🐦 Generating tweets for articles (limit: {args.limit})...")
    
    try:
        # Query pending articles
        results = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Status",
                "select": {
                    "equals": "Pending"
                }
            },
            page_size=args.limit
        )
        
        articles = results.get("results", [])
        print(f"📄 Found {len(articles)} pending articles")
        
        tweets_generated = 0
        
        for article in articles:
            try:
                # Extract article details
                properties = article["properties"]
                
                # Get title
                title_data = properties.get("Title", {}).get("title", [])
                title = title_data[0]["text"]["content"] if title_data else "No Title"
                
                # Get URL
                url = properties.get("URL", {}).get("url", "")
                
                print(f"\n📝 Processing: {title[:50]}...")
                
                # Generate tweet
                tweet = generate_tweet_with_perplexity(title, url, perplexity_api_key)
                
                if tweet:
                    # Update article in Notion with generated tweet
                    notion.pages.update(
                        page_id=article["id"],
                        properties={
                            "Status": {
                                "select": {
                                    "name": "Tweet Generated"
                                }
                            },
                            "Tweet": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": tweet[:2000]  # Notion limit
                                        }
                                    }
                                ]
                            }
                        }
                    )
                    print(f"  ✅ Generated tweet: {tweet}")
                    tweets_generated += 1
                else:
                    print(f"  ❌ Failed to generate tweet")
                    
            except Exception as e:
                print(f"  ⚠️ Error processing article: {e}")
                continue
        
        print(f"\n🎉 Completed! Generated {tweets_generated} tweets.")
        
    except Exception as e:
        print(f"❌ Error querying Notion database: {e}")

if __name__ == "__main__":
    main()
