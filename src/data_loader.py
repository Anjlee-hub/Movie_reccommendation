import pandas as pd
import ast
import nltk
from nltk.stem.porter import PorterStemmer

# Initialize stemmer
ps = PorterStemmer()

movies = pd.read_csv("data/tmdb_5000_movies.csv")
credits = pd.read_csv("data/tmdb_5000_credits.csv")

# Merge
movies = movies.merge(credits, on='title')

# Select important columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Remove nulls
movies.dropna(inplace=True)

# Convert JSON to list
def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# Take only top 3 actors
def convert3(text):
    L = []
    counter = 0

    for i in ast.literal_eval(text):
        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break

    return L

movies['cast'] = movies['cast'].apply(convert3)

# Extract director
def fetch_director(text):
    L = []

    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
            break

    return L

movies['crew'] = movies['crew'].apply(fetch_director)

# Remove spaces
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

# Convert overview into list
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Create tags
movies['tags'] = (
    movies['overview']
    + movies['genres']
    + movies['keywords']
    + movies['cast']
    + movies['crew']
)

# Final dataframe
new_df = movies[['movie_id', 'title', 'tags']].copy()

# Convert list to string
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))

# Convert to lowercase
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

# Stemming function
def stem(text):
    y = []

    for i in text.split():
        y.append(ps.stem(i))

    return " ".join(y)

# Apply stemming
new_df['tags'] = new_df['tags'].apply(stem)

print(new_df.head())

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Convert text to vectors
cv = CountVectorizer(max_features=5000, stop_words='english')

vectors = cv.fit_transform(new_df['tags']).toarray()

# Compute similarity
similarity = cosine_similarity(vectors)

print("\nSimilarity shape:", similarity.shape)

# Recommendation function
def recommend(movie):

    # Find movie index
    movie_index = new_df[new_df['title'] == movie].index[0]

    # Get similarity scores
    distances = similarity[movie_index]

    # Sort movies
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    # Print recommendations
    for i in movies_list:
        print(new_df.iloc[i[0]].title)

# Test
print("\nRecommendations for Avatar:\n")
recommend("Avatar")

# Save files
import pickle

new_df.to_pickle("models/movies.pkl")

pickle.dump(similarity, open("models/similarity.pkl", "wb"))