# notion_tweet_uploader

Automated system to fetch RSS feeds, add articles to Notion database, and generate tweets using AI.

## Features

- 📡 Fetch articles from RSS feeds (TechCrunch, The Verge, Wired)
- 📝 Add articles to Notion database
- 🤖 Generate engaging tweets using Perplexity AI
- ⏰ Automated with GitHub Actions (runs hourly)

## Setup

### 1. Prerequisites

- A Notion account with an integration and database
- A Perplexity API key (for tweet generation)
- GitHub repository secrets configured

### 2. Notion Database Structure

Create a Notion database with the following properties:

- **Title** (title): Article title
- **URL** (url): Article link
- **Status** (select): Options: "Pending", "Tweet Generated"
- **Source** (rich_text): RSS feed source
- **Tweet** (rich_text): Generated tweet content

### 3. Environment Variables

Configure the following secrets in your GitHub repository:

- `NOTION_API_KEY`: Your Notion integration token
- `NOTION_DATABASE_ID`: Your Notion database ID
- `PERPLEXITY_API_KEY`: Your Perplexity API key

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NOTION_API_KEY="your_notion_api_key"
export NOTION_DATABASE_ID="your_database_id"
export PERPLEXITY_API_KEY="your_perplexity_key"

# Run RSS fetcher
python src/rss_to_notion.py

# Generate tweets
python src/generate_tweets.py --limit 5
```

## How It Works

### RSS to Notion (`rss_to_notion.py`)

1. Fetches articles from configured RSS feeds
2. Checks if article already exists in Notion (by URL)
3. Adds new articles to Notion with "Pending" status

### Generate Tweets (`generate_tweets.py`)

1. Queries Notion for articles with "Pending" status
2. Generates engaging tweets using Perplexity AI
3. Updates articles with generated tweets and changes status to "Tweet Generated"

## GitHub Actions Workflow

The workflow runs automatically every hour and:
1. Fetches new articles from RSS feeds
2. Generates tweets for pending articles

You can also trigger it manually from the Actions tab.

## Customization

### Add More RSS Feeds

Edit `src/rss_to_notion.py` and add feeds to the `rss_feeds` list:

```python
rss_feeds = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://your-favorite-blog.com/feed/",
]
```

### Modify Tweet Generation

Edit the prompt in `src/generate_tweets.py` to customize tweet style, tone, or requirements.

## License

MIT