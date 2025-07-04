
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Netflix Content Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #E50914;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #E50914;
    }
</style>
""", unsafe_allow_html=True)

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_titles.csv', encoding='utf-8')
    
    # Data cleaning
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    
    # Fill missing values
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna('Unknown')
    
    # Remove rows with missing duration
    df = df.dropna(subset=['duration'])
    
    # Extract duration in minutes for movies
    def extract_duration(duration_str):
        if 'min' in str(duration_str):
            return int(duration_str.split(' ')[0])
        else:
            return None
    
    df['duration_minutes'] = df['duration'].apply(extract_duration)
    
    # Extract season count for TV shows
    def extract_seasons(duration_str):
        if 'Season' in str(duration_str):
            return int(duration_str.split(' ')[0])
        else:
            return None
    
    df['seasons_count'] = df['duration'].apply(extract_seasons)
    
    return df

# Load data
df = load_data()

# Main title
st.markdown('<h1 class="main-header">🎬 Netflix Content Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")
content_type = st.sidebar.multiselect(
    "Select Content Type:",
    options=df['type'].unique(),
    default=df['type'].unique()
)

year_range = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=int(df['release_year'].min()),
    max_value=int(df['release_year'].max()),
    value=(2010, int(df['release_year'].max()))
)

# Filter data based on selections
filtered_df = df[
    (df['type'].isin(content_type)) &
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
]

# Key Metrics
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Titles", len(filtered_df))
with col2:
    st.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
with col3:
    st.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
with col4:
    st.metric("Countries", filtered_df['country'].nunique())

# Content Distribution
st.header("📈 Content Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    # Content type distribution
    fig_pie = px.pie(
        filtered_df, 
        names='type', 
        title='Content Type Distribution',
        color_discrete_sequence=['#E50914', '#221F1F']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Top 10 countries
    country_counts = filtered_df['country'].value_counts().head(10)
    fig_bar = px.bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation='h',
        title='Top 10 Countries by Content Count',
        color_discrete_sequence=['#E50914']
    )
    fig_bar.update_layout(xaxis_title="Number of Titles", yaxis_title="Country")
    st.plotly_chart(fig_bar, use_container_width=True)

# Time Series Analysis
st.header("📅 Content Addition Trends")

# Content added over time
yearly_data = filtered_df.groupby(['year_added', 'type']).size().reset_index(name='count')
yearly_data = yearly_data.dropna()

fig_line = px.line(
    yearly_data, 
    x='year_added', 
    y='count', 
    color='type',
    title='Netflix Content Addition Over Time',
    color_discrete_sequence=['#E50914', '#221F1F']
)
st.plotly_chart(fig_line, use_container_width=True)

# Genre Analysis
st.header("🎭 Genre Analysis")

# Process genres (listed_in column)
all_genres = []
for genres in filtered_df['listed_in'].dropna():
    all_genres.extend([genre.strip() for genre in genres.split(',')])

genre_counts = pd.Series(all_genres).value_counts().head(15)

fig_genre = px.bar(
    x=genre_counts.values,
    y=genre_counts.index,
    orientation='h',
    title='Top 15 Genres on Netflix',
    color_discrete_sequence=['#E50914']
)
fig_genre.update_layout(xaxis_title="Number of Titles", yaxis_title="Genre")
st.plotly_chart(fig_genre, use_container_width=True)

# Rating Analysis
st.header("🔞 Content Rating Distribution")

col1, col2 = st.columns(2)

with col1:
    # Rating distribution
    rating_counts = filtered_df['rating'].value_counts()
    fig_rating = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        title='Content Rating Distribution',
        color_discrete_sequence=['#E50914']
    )
    fig_rating.update_layout(xaxis_title="Rating", yaxis_title="Number of Titles")
    st.plotly_chart(fig_rating, use_container_width=True)

with col2:
    # Duration analysis for movies
    movies_df = filtered_df[filtered_df['type'] == 'Movie'].dropna(subset=['duration_minutes'])
    if not movies_df.empty:
        fig_duration = px.histogram(
            movies_df,
            x='duration_minutes',
            title='Movie Duration Distribution',
            nbins=30,
            color_discrete_sequence=['#E50914']
        )
        fig_duration.update_layout(xaxis_title="Duration (minutes)", yaxis_title="Number of Movies")
        st.plotly_chart(fig_duration, use_container_width=True)

# Top Directors and Cast
st.header("🎬 Top Directors and Cast")

col1, col2 = st.columns(2)

with col1:
    # Top directors
    all_directors = []
    for directors in filtered_df['director'].dropna():
        if directors != 'Unknown':
            all_directors.extend([director.strip() for director in directors.split(',')])
    
    if all_directors:
        director_counts = pd.Series(all_directors).value_counts().head(10)
        fig_directors = px.bar(
            x=director_counts.values,
            y=director_counts.index,
            orientation='h',
            title='Top 10 Directors',
            color_discrete_sequence=['#E50914']
        )
        st.plotly_chart(fig_directors, use_container_width=True)

with col2:
    # Top cast members
    all_cast = []
    for cast in filtered_df['cast'].dropna():
        if cast != 'Unknown':
            all_cast.extend([actor.strip() for actor in cast.split(',')])
    
    if all_cast:
        cast_counts = pd.Series(all_cast).value_counts().head(10)
        fig_cast = px.bar(
            x=cast_counts.values,
            y=cast_counts.index,
            orientation='h',
            title='Top 10 Cast Members',
            color_discrete_sequence=['#E50914']
        )
        st.plotly_chart(fig_cast, use_container_width=True)

# Release Year Analysis
st.header("📆 Release Year Trends")

release_year_counts = filtered_df['release_year'].value_counts().sort_index()
fig_release = px.line(
    x=release_year_counts.index,
    y=release_year_counts.values,
    title='Content by Release Year',
    color_discrete_sequence=['#E50914']
)
fig_release.update_layout(xaxis_title="Release Year", yaxis_title="Number of Titles")
st.plotly_chart(fig_release, use_container_width=True)

# Data Table
st.header("📋 Data Explorer")
st.subheader("Sample Data")
st.dataframe(
    filtered_df[['title', 'type', 'country', 'release_year', 'rating', 'duration', 'listed_in']].head(20),
    use_container_width=True
)

# Summary Statistics
st.header("📈 Summary Statistics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Content Type Summary")
    type_summary = filtered_df['type'].value_counts()
    st.write(type_summary)

with col2:
    st.subheader("Rating Summary")
    rating_summary = filtered_df['rating'].value_counts()
    st.write(rating_summary)

# Footer
st.markdown("---")
st.markdown("**Data Source:** Netflix Movies and TV Shows Dataset | **Dashboard Created with:** Streamlit & Plotly")
