import streamlit as st
import pickle
import pandas as pd
import requests
import difflib

# Custom CSS Styling
st.markdown("""
<style>

/* Top header */
header {
    background: rgba(15, 23, 42, 0.85) !important;
}

/* Toolbar */
[data-testid="stToolbar"] {
    right: 2rem;
}

/* Hamburger menu + deploy button */
[data-testid="stHeader"] {
    background: rgba(15, 23, 42, 0);
}

/* Main menu icons */
button[kind="header"] {
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #0f172a, #1e293b);
}


/* Main background */
.stApp {
    background: linear-gradient(to right, #0f172a, #1e3a8a);
    color: white;
}

/* Title styling */
h1 {
    font-family: 'Trebuchet MS', sans-serif;
    font-weight: bold;
}

/* Button styling */
div.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    font-size: 18px;
    transition: all 0.3s ease;
}

/* Button hover animation */
div.stButton > button:hover {
    background-color: #1d4ed8;
    transform: scale(1.05);
    box-shadow: 0px 0px 15px rgba(37, 99, 235, 0.8);
}

/* Selectbox styling */
div[data-baseweb="select"] {
    color: black;
}

/* Poster animation */
img {
    border-radius: 15px;
    transition: transform 0.3s ease;
}

img:hover {
    transform: scale(1.05);
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

img {
    animation: float 4s ease-in-out infinite;
}

</style>
""", unsafe_allow_html=True)


# Load data
movies = pd.read_pickle("models/movies.pkl")

with open("models/similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

# TMDB API Key
API_KEY = st.secrets["API_KEY"]
API_KEY = "6a453da8e590c7d114e3ca819036c7cf"

# Fetch poster from TMDB

def fetch_poster(movie_id):

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

        response = requests.get(url, timeout=10)

        data = response.json()

        poster_path = data.get('poster_path')

        if poster_path is not None:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path

        # Fallback poster
        return "https://via.placeholder.com/500x750/0f172a/ffffff?text=No+Poster"

    except Exception as e:
        print("Error:", e)
        return "https://via.placeholder.com/500x750/0f172a/ffffff?text=Connection+Error"

# Recommendation function
# Recommendation function
# Recommendation function
def recommend(movie):

    # Fuzzy matching
    close_matches = difflib.get_close_matches(movie, movies['title'].values)

    if not close_matches:
        return [], []

    movie = close_matches[0]

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(movies.iloc[i[0]].title)

        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# Streamlit UI
# Page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Title
st.markdown(
    "<h1 style='text-align: center; color: red;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align: center;'>Find movies similar to your favorites</h4>",
    unsafe_allow_html=True
)

st.write("")

# Movie selector
selected_movie = st.selectbox(
    "🎥 Choose a movie",
    movies['title'].values
)

typed_movie = st.text_input(
    "🔍 Or type a movie name"
)
# Recommendation button
# Recommendation button
if st.button("Recommend"):

    movie_name = typed_movie if typed_movie else selected_movie

    names, posters = recommend(movie_name)

    st.write("")
    st.subheader("Recommended Movies")

    if len(names) == 0:
        st.error("Movie not found. Try another name.")

    else:

        col1, col2, col3, col4, col5, col6= st.columns(6)

        with col1:
            st.image(posters[0], use_container_width=True)
            st.caption(names[0])

        with col2:
            st.image(posters[1], use_container_width=True)
            st.caption(names[1])

        with col3:
            st.image(posters[2], use_container_width=True)
            st.caption(names[2])

        with col4:
            st.image(posters[3], use_container_width=True)
            st.caption(names[3])

        with col5:
            st.image(posters[4], use_container_width=True)
            st.caption(names[4])
        
        with col6:
            st.image("https://via.placeholder.com/500x750/0f172a/ffffff?text=More+Coming+Soon", use_container_width=True)
            st.caption("More Coming Soon")