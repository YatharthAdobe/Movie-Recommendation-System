import os
import pandas as pd
import streamlit as st
import pickle
import requests
import base64

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=ac51b3cdc21e339fa20e9d897446b7e2&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']

def recommend_for_single_user(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("The entered movie not found. Please check the movie title.")
        return [], []

    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:23]
    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster from api
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

def recommend_for_two_people(movie1, movie2):
    try:
        movie1_index = movies[movies['title'] == movie1].index[0]
        movie2_index = movies[movies['title'] == movie2].index[0]
    except IndexError:
        st.error("One or both of the entered movies not found. Please check the movie titles.")
        return [], []

    distances1 = similarity[movie1_index]
    distances2 = similarity[movie2_index]

    avg_distances = (distances1 + distances2) / 2

    movie_list = sorted(list(enumerate(avg_distances)), reverse=True, key=lambda x: x[1])[1:23]
    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster from api
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

def display_recommendations(names, posters):
    num_columns = 4
    num_rows = len(names) // num_columns + (1 if len(names) % num_columns > 0 else 0)

    for row in range(num_rows):
        cols = st.columns(num_columns)
        for col in range(num_columns):
            index = row * num_columns + col
            if index < len(names):
                with cols[col]:
                    st.text(names[index])
                    st.image(posters[index])

movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("bg.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/jpeg;base64,{img}");
background-position: center;
background-size: cover;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
st.title('Movie Recommender Engine')
st.markdown('Can’t decide between thousands of movies available for streaming?')
st.markdown('Finally, the answer to "What should we watch tonight?"')

# User options
option = st.radio("Select recommendation type:", ["Solo Watcher", "Two People"])

if option == "Solo Watcher":
    selected_movie_name = st.selectbox("Select your favorite movie:", movies['title'].values)
    if st.button('Recommend'):
        names, posters = recommend_for_single_user(selected_movie_name)
        display_recommendations(names, posters)

elif option == "Two People":
    selected_movie_name1 = st.selectbox("Select the first person's favorite movie:", movies['title'].values)
    selected_movie_name2 = st.selectbox("Select the second person's favorite movie:", movies['title'].values)
    if st.button('Recommend'):
        names, posters = recommend_for_two_people(selected_movie_name1, selected_movie_name2)
        display_recommendations(names, posters)
