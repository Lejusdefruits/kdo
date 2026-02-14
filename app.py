import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from backend.logic import get_generator

st.set_page_config(
    page_title="Spotify Mixer",
    page_icon="💜",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #f0f0f0;
        background-color: #121212;
    }
    
    .stApp {
        background: linear-gradient(135deg, #5f2c82 0%, #49a09d 100%);
    }
    
    @keyframes float {
        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
        50% { opacity: 0.6; }
        100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
    }

    .heart-bg {
        position: fixed;
        bottom: -10vh;
        color: rgba(255, 255, 255, 0.3);
        font-size: 20px;
        opacity: 0;
        z-index: 0;
        animation: float 15s infinite linear;
    }

    .stButton>button {
        width: 100%;
        border-radius: 30px; 
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        font-family: 'Montserrat', sans-serif;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 14px;
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
        transition: all 0.4s ease;
        backdrop-filter: blur(5px);
    }
    
    .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.3);
        color: #fff;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);
        border-color: #fff;
    }

    .stTextInput>div>div>input {
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        background-color: rgba(0,0,0,0.3);
        color: white;
        font-family: 'Montserrat', sans-serif;
    }
    
    h1 {
        font-family: 'Playfair Display', serif;
        color: #fff;
        font-weight: 700 !important;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    
    h3 {
        font-family: 'Playfair Display', serif;
        color: #e0e0e0;
        font-weight: 400 !important;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        padding-bottom: 10px;
    }

    .track-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 10px;
        border-left: 4px solid #49a09d;
        display: flex;
        align-items: center;
        gap: 15px;
        backdrop-filter: blur(5px);
    }

    .big-link {
        display: block;
        background-color: #fff;
        color: #5f2c82 !important;
        padding: 15px;
        text-align: center;
        font-weight: 600;
        text-decoration: none;
        margin-top: 30px;
        border-radius: 30px;
        letter-spacing: 2px;
        text-transform: uppercase;
        transition: all 0.3s;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .big-link:hover {
        background-color: #f0f0f0;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    </style>
    
    <div class="heart-bg" style="left: 5%; animation-duration: 12s; font-size: 25px;">💜</div>
    <div class="heart-bg" style="left: 15%; animation-duration: 15s; font-size: 15px; animation-delay: 2s;">💚</div>
    <div class="heart-bg" style="left: 25%; animation-duration: 18s; font-size: 30px; animation-delay: 5s;">🤍</div>
    <div class="heart-bg" style="left: 35%; animation-duration: 10s; font-size: 20px; animation-delay: 1s;">💜</div>
    <div class="heart-bg" style="left: 45%; animation-duration: 20s; font-size: 18px; animation-delay: 7s;">💚</div>
    <div class="heart-bg" style="left: 55%; animation-duration: 14s; font-size: 22px; animation-delay: 3s;">🤍</div>
    <div class="heart-bg" style="left: 65%; animation-duration: 16s; font-size: 28px; animation-delay: 6s;">💜</div>
    <div class="heart-bg" style="left: 75%; animation-duration: 11s; font-size: 16px; animation-delay: 0s;">💚</div>
    <div class="heart-bg" style="left: 85%; animation-duration: 19s; font-size: 24px; animation-delay: 4s;">🤍</div>
    <div class="heart-bg" style="left: 95%; animation-duration: 13s; font-size: 19px; animation-delay: 2s;">💜</div>
    <div class="heart-bg" style="left: 10%; animation-duration: 22s; font-size: 14px; animation-delay: 8s;">💚</div>
    <div class="heart-bg" style="left: 50%; animation-duration: 25s; font-size: 32px; animation-delay: 9s;">🤍</div>
    <div class="heart-bg" style="left: 80%; animation-duration: 17s; font-size: 21px; animation-delay: 5s;">💜</div>
    """, unsafe_allow_html=True)

st.markdown("<h1>S P O T I F Y &nbsp;&nbsp; M I X E R</h1>",
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if 'token_info' not in st.session_state:
    st.session_state.token_info = None

try:
    client_id = st.secrets["SPOTIPY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
    redirect_uri = st.secrets["SPOTIPY_REDIRECT_URI"]
except FileNotFoundError:
    st.error("Configuration missing.")
    st.stop()

oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read user-top-read playlist-modify-public playlist-modify-private"
)

query_params = st.query_params
if "code" in query_params and not st.session_state.token_info:
    try:
        code = query_params["code"]
        token_info = oauth.get_access_token(code)
        st.session_state.token_info = token_info
        st.rerun()
    except Exception:
        st.error("Connection error.")
        st.stop()

auth_token = None
if st.session_state.token_info:
    token_info = st.session_state.token_info
    if oauth.is_token_expired(token_info):
        token_info = oauth.refresh_access_token(token_info['refresh_token'])
        st.session_state.token_info = token_info
    auth_token = token_info['access_token']


if not auth_token:
    auth_url = oauth.get_authorize_url()
    st.markdown(f"<br><br>", unsafe_allow_html=True)
    st.markdown(f'''
        <a href="{auth_url}" target="_blank" style="text-decoration:none;">
            <div style="
                background: linear-gradient(45deg, #49a09d, #5f2c82);
                color: white; 
                padding: 15px; 
                text-align: center; 
                text-transform: uppercase; 
                letter-spacing: 2px;
                font-size: 14px;
                border-radius: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: 0.3s;
            ">
                Connect Spotify
            </div>
        </a>
    ''', unsafe_allow_html=True)

else:
    try:
        sp = spotipy.Spotify(auth=auth_token)
        user = sp.current_user()
        generator = get_generator(auth_token)

        st.write(f"Welcome, {user['display_name']}.")
        st.markdown("---")

        st.markdown("### 01. SELECT VIBE")

        vibes = ["Chill", "Party", "Love", "Throwback", "Energy", "Discovery"]

        vibe = st.radio(
            "Vibe", vibes, label_visibility="collapsed", horizontal=True)
        st.caption(f"Selected: {vibe}")

        partner_id = None
        guest_url = None

        if vibe == "Love":
            try:
                partner_id = st.secrets["PARTNER_PLAYLIST_ID"]
                if partner_id and "YOUR" not in partner_id:
                    st.info("Partner connected.")
            except:
                pass

        elif vibe == "Party":
            guest_url = st.text_input(
                "Guest Playlist (Spotify URL)", placeholder="https://open.spotify.com/playlist/...")

        st.markdown("<br>", unsafe_allow_html=True)

        if 'preview_tracks' not in st.session_state:
            st.session_state.preview_tracks = None

        if st.button("Initialize Mix"):
            with st.spinner("Analyzing..."):
                tracks = generator.generate_playlist_preview(
                    vibe, partner_id, guest_url)
                st.session_state.preview_tracks = tracks

        if st.session_state.preview_tracks:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 02. PREVIEW")

            with st.container():
                for track in st.session_state.preview_tracks[:5]:
                    artists = ", ".join([a['name'] for a in track['artists']])
                    name = track['name']
                    st.markdown(f"""
                    <div class="track-card">
                        <span style="color: #49a09d;">●</span>
                        <div>
                            <div style="font-weight:600; color: #fff;">{name}</div>
                            <div style="color:#bbb; font-size:12px; text-transform:uppercase;">{artists}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 03. DETAILS")
            msg = st.text_input("Personal Message",
                                placeholder="E.g. For our winter nights...")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Save Collection"):
                with st.spinner("Syncing..."):
                    try:
                        url = generator.create_playlist_from_tracks(
                            user['id'],
                            st.session_state.preview_tracks,
                            vibe,
                            custom_message=msg
                        )
                        st.success("Successfully Created.")
                        st.markdown(f'''
                            <a href="{url}" target="_blank" class="big-link">
                                OPEN IN SPOTIFY
                            </a>
                        ''', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error details: {e}")

    except Exception as e:
        st.error("Session Expired.")
        if st.button("Refresh"):
            st.session_state.token_info = None
            st.rerun()
