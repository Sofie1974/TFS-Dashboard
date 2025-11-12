import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup  # Import BeautifulSoup for scraping

# Set the page to use the full width
st.set_page_config(layout="wide")

# News API Logic
base_url = 'https://newsapi.org/v2/everything'
my_secret_key = "NEWS_API_KEY"

# News search terms
news_keywords = [
    '"The Future Society"',
    '"The Athens Roundtable"',
    '"AI and the Rule of Law"',
    '"The Global Governance of AI Roundtable"',
    '"GGAR"'
]

# Build the final search string for the News API
news_query = " OR ".join(news_keywords) # Use uppercase OR for NewsAPI

parameters = {
    'q': news_query,
    'sortBy': 'popularity',
    'apiKey': my_secret_key
}

# Set a custom User-Agent to be polite to the API
news_headers = {'User-agent': 'TFS Dashboard Bot 0.1'}

# Fetch the data from the API
response = requests.get(base_url, params=parameters, headers=news_headers)

# Reddit API Logic
reddit_url = "https://www.reddit.com/search.json"

# Reddit search terms
reddit_keywords = [
    '"The Future Society"',
    '"The Athens Roundtable"',
    '"AI and the Rule of Law"',
    '"The Global Governance of AI Roundtable"',
]

# Build the final search string for the Reddit 'API'
reddit_query = " OR ".join(reddit_keywords) # Reddit is flexible with 'or' or 'OR'

reddit_params = {
    'q': reddit_query,
    'sort': 'new'
}

# Set a custom User-Agent to be polite to the API
reddit_headers = {'User-agent': 'TFS Dashboard Bot 0.1'}

# Fetch the data from the API
reddit_response = requests.get(reddit_url, params=reddit_params, headers=reddit_headers)

# Widget title
st.title('TFS Operations Dashboard')

# --- Top Row: Charts ---

# Charts/visualizations
st.header('Athens Roundtable: At a Glance (2019-2024)')

# Create the dataset for the charts
data = {
    'Year': [2019, 2020, 2021, 2022, 2023, 2024],
    'Location': ['Athens, Greece', 'Virtual (NYC)', 'Virtual', 'Brussels, Belgium', 'Washington D.C., USA', 'Paris, France'],
    'Total Participants': [70, 1000, 1700, 1100, 1150, 965],
    'Countries Represented': [18, None, None, 112, 100, 108] # Using None for missing data
}
df = pd.DataFrame(data)
df.set_index('Year', inplace=True)

# Create 3 columns for the top row of charts, with padding
chart_col1, chart_col2, chart_col3 = st.columns(3, gap="large")

with chart_col1:
    # Put widget in a bordered container
    with st.container(border=True):
        # Chart 1: Participant Growth
        st.subheader('Total Participant Growth')
        st.line_chart(df['Total Participants'])

with chart_col2:
    # Put widget in a bordered container
    with st.container(border=True):
        # Chart 2: Global Reach (Countries)
        st.subheader('Global Reach (Countries)')
        # Fill missing data with 0 instead of dropping it
        countries_df = df['Countries Represented'].fillna(0)
        st.bar_chart(countries_df)
        # Add a caption to explain the zero-value bars
        st.caption("Country data for 2020 & 2021 is not available as events were held virtually.")

with chart_col3:
    # Put widget in a bordered container
    with st.container(border=True):
        # Chart 3: Host Locations
        st.subheader('International Host Locations')
        # Show the 'Location' column. Streamlit displays this well.
        st.dataframe(df[['Location']])

# Add a divider between the chart row and the feed row
st.divider()

# --- Bottom Row: Feeds ---

# Main loop with 3 columns - News, General Reddit, Targeted Reddit, with padding
col1, col2, col3 = st.columns(3, gap="large")

# Column 1 - New Articles
with col1:
    # Put widget in a bordered container
    with st.container(border=True):
        if response.status_code == 200:
            news_data = response.json()
            st.header("Latest News on AI Governance")
            # Loop through only the first 5 articles
            for article in news_data['articles'][:5]:
                # Start of Card 1
                st.write(f"**{article['title']}**")
                # Get Author or 'fallback'
                author = article.get('author') or article['source']['name']
                # Get and clean the date
                raw_date = article['publishedAt']
                clean_date = raw_date.split('T')[0]
                # Article by line
                st.caption(f"By {author} | Published: {clean_date}")
                # Article link
                st.write(f"[Read full article]({article['url']})")
                # Card separator
                st.divider()
                # End of Card 1
        # Status code error for News API
        else:
            st.error(f"News API Error: {response.status_code}")

# Column 2 - Reddit mentions
with col2:
    # Put widget in a bordered container
    with st.container(border=True):
        if reddit_response.status_code == 200:
            reddit_data = reddit_response.json()
            st.header("Latest Governance Info from Reddit")
            # Loop through only the first 5 posts
            for data in reddit_data['data']['children'][:5]:
                # Start card 2
                post_data = data['data']
                # Post title
                st.write(f"**{post_data['title']}**")
                # Post by line
                st.caption(f"Posted by u/{post_data['author']} in r/{post_data['subreddit']}")
                # Post link
                st.write(f"[Read thread](https://www.reddit.com{post_data['permalink']})")
                # Card divider
                st.divider()
        # Status code error for Reddit 'API'
        else:
            st.error(f"Reddit API Error: {reddit_response.status_code}")

# --- Column 3: Web Scraper for Brookings ---
with col3:
    # Put widget in a bordered container
    with st.container(border=True):
        st.header("Brookings AI Blog")

        # Define the URL to scrape
        scraper_url = "https://www.brookings.edu/topic/artificial-intelligence/"
        domain = "https://www.brookings.edu"  # Base domain for relative links

        # Add scraper headers
        scraper_headers = {'User-agent': 'TFS Dashboard Bot 0.1'}

        try:
            # Make the request for the page HTML
            scraper_response = requests.get(scraper_url, headers=scraper_headers)

            if scraper_response.status_code == 200:
                # Get the raw HTML content
                html_content = scraper_response.text

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all article links by class 'overlay-link'
                article_links = soup.find_all('a', class_='overlay-link')

                if not article_links:
                    # Handle case where no articles are found
                    st.warning("Could not find articles. (Structure might have changed)")
                else:
                    # Loop through only the first 5 links
                    for link_tag in article_links[:5]:

                        # Check for a valid link and href
                        if link_tag and link_tag.has_attr('href'):

                            # Get the title and URL
                            title = link_tag.text.strip()
                            url = link_tag['href']

                            # Fix relative URLs (add domain)
                            if not url.startswith('http'):
                                url = f"{domain}{url}"

                            # --- Start of Scraper Card ---
                            st.write(f"**{title}**")
                            st.write(f"[Read article]({url})")
                            st.divider()
                            # --- End of Scraper Card ---

            else:
                # Error handling for scraper
                st.error(f"Brookings Scraper Error: {scraper_response.status_code}")

        except requests.exceptions.RequestException as e:
            # Handle connection errors
            st.error(f"Failed to connect to Brookings: {e}")