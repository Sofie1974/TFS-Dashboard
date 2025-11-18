import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# Set the page to use the full width
st.set_page_config(layout="wide")

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

# Create 2 columns for our working scrapers
col1, col2 = st.columns([7, 3], gap="large")

# --- Column 1: AI Governance Presentation ---
with col1:
    # Put widget in a bordered container
    with st.container(border=True):
        st.header("The Politics of AI")

        # Read the HTML file for the presentation
        try:
            # We look for the file in the SAME folder as this .py file
            with open('ai_governance_presentation_v2.html', 'r', encoding='utf-8') as f:
                html_data = f.read()

            # Display the presentation
            # We give it 750px to account for the slide (720px) + padding/buttons
            components.html(html_data, height=750, scrolling=False)

        except FileNotFoundError:
            st.error("Could not find the presentation file (ai_governance_presentation_v2.html).")
            st.warning("Please make sure 'ai_governance_presentation_v2.html' is in the same folder as this .py file.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
#  Column 2: Web Scraper for Brookings
with col2:
    # Put widget in a bordered container
    with st.container(border=True):
        st.header("Brookings AI Blog")

        # Define the URL to scrape
        scraper_url = "https://www.brookings.edu/topic/artificial-intelligence/"
        domain = "https://www.brookings.edu"  # Base domain for relative links

        try:
            # Make the request for the page HTML
            scraper_response = requests.get(scraper_url)

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

                            #  Start of Scraper Card
                            st.write(f"**{title}**")
                            st.write(f"[Read article]({url})")
                            st.divider()
                            #  End of Scraper Card

            else:
                # Error handling for scraper
                st.error(f"Brookings Scraper Error: {scraper_response.status_code}")

        except requests.exceptions.RequestException as e:
            # Handle connection errors
            st.error(f"Failed to connect to Brookings: {e}")

# --- Third Row: Financial Analysis Presentation ---

# Add a divider for the new section
st.divider()

st.header("Operations Analysis: Financial Efficiency (2019-2023)")

# Put widget in a bordered container
with st.container(border=True):
    # Read the HTML file for the presentation
    try:
        # This looks for your *new* "export" presentation
        with open('tfs_financial_analysis_export.html', 'r', encoding='utf-8') as f:
            html_data = f.read()

        # Display the presentation
        # We give it a large height and scrolling to show all slides
        components.html(html_data, height=4500, scrolling=True)

    except FileNotFoundError:
        st.error("Could not find the presentation file (tfs_financial_analysis_export.html).")
        st.warning("Please make sure 'tfs_financial_analysis_export.html' is in the same folder as this .py file.")
    except Exception as e:
        st.error(f"An error occurred: {e}")