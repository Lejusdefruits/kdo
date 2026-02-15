import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import random
from backend.logic import get_generator

st.set_page_config(
    page_title="Our Mix",
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
        10% { opacity: 0.8; }
        90% { opacity: 0.8; }
        100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
    }

    .heart-container {
        position: fixed;
        bottom: -10vh;
        z-index: 99;
        cursor: pointer;
        animation: float 15s infinite linear;
        user-select: none;
    }

    .heart-icon {
        font-size: 25px;
        transition: transform 0.2s;
    }

    .heart-msg {
        position: absolute;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%) scale(0);
        background: rgba(255, 255, 255, 0.9);
        color: #5f2c82;
        padding: 5px 10px;
        border-radius: 10px;
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        transition: all 0.2s ease;
        pointer-events: none;
        font-weight: bold;
    }

    .heart-container:active .heart-msg,
    .heart-container:hover .heart-msg {
        transform: translateX(-50%) scale(1);
        opacity: 1;
    }
    
    .heart-container:active .heart-icon {
        transform: scale(1.3);
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
    """, unsafe_allow_html=True)

hearts_html = ""
messages = ["Love u", "caca", "pipi", "babygirl",
            "<3", "t'es jolie", "MON CHOUCHOU"]
emojis = ["💜", "🤍", "💚", "✨", "🦋"]

for i in range(25):
    left = random.randint(0, 100)
    duration = random.randint(10, 25)
    delay = random.randint(0, 10)
    size = random.randint(15, 30)
    emoji = random.choice(emojis)
    msg = random.choice(messages)

    hearts_html += f"""
    <div class="heart-container" style="left: {left}%; animation-duration: {duration}s; animation-delay: {delay}s;">
        <div class="heart-icon" style="font-size: {size}px;">{emoji}</div>
        <div class="heart-msg">{msg}</div>
    </div>
    """

st.markdown(hearts_html, unsafe_allow_html=True)

st.markdown("<h1>O U R &nbsp;&nbsp; M I X</h1>", unsafe_allow_html=True)
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

# Updated scopes including private/collab read
oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"
)

if st.sidebar.button("LOGOUT / RESET", type="primary"):
    if os.path.exists(".cache"):
        os.remove(".cache")
    st.session_state.token_info = None
    st.cache_data.clear()
    st.rerun()

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

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ Connection Troubleshooting"):
        st.write(f"**Redirect URI**: `{redirect_uri}`")
        st.write(
            "Ensure this URL is exactly the same in your Spotify Dashboard > Settings > Redirect URIs.")
        st.warning(
            "Note: Do not put your Spotify password in secrets.toml. The app uses OAuth2 (like 'Login with Google') for security.")

else:
    try:
        # Create single 'sp' instance and share it
        sp = spotipy.Spotify(auth=auth_token)

        # --- AUTO-RESET IF SCOPES ARE MISSING ---
        current_scopes = token_info.get('scope', '')
        # Debug display (remove later if needed)
        # st.caption(f"Debug: Active Scopes: {current_scopes}")

        required_scopes = ["playlist-modify-public", "playlist-modify-private"]
        missing_scopes = [
            s for s in required_scopes if s not in current_scopes]

        if missing_scopes:
            st.warning(
                f"⚠️ Updates found! Missing permissions: {missing_scopes}. Resetting connection...")
            if os.path.exists(".cache"):
                os.remove(".cache")
            st.session_state.token_info = None
            st.cache_data.clear()
            st.rerun()
        # ----------------------------------------

        user = sp.current_user()
        generator = get_generator(sp)

        st.write(f"Welcome, {user['display_name']}.")
        st.markdown("---")

        st.markdown("### 01. SELECT VIBE")

        vibes = ["Chill", "Party", "Love", "Throwback",
                 "Energy", "Discovery", "Time Capsule"]

        vibe = st.radio(
            "Vibe", vibes, label_visibility="collapsed", horizontal=True)
        st.caption(f"Selected: {vibe}")

        partner_id = None
        guest_url = None
        year = None

        if vibe == "Love":
            try:
                partner_id = st.secrets["PARTNER_PLAYLIST_ID"]
                if not partner_id or "YOUR" in partner_id:
                    st.warning(
                        "Please set 'PARTNER_PLAYLIST_ID' in secrets.toml")
                else:
                    st.info("Partner connected.")

                    if st.button("Calculate Affinity 💕"):
                        with st.spinner("Comparing tastes..."):
                            try:
                                score, common_artists = generator.calculate_affinity(
                                    partner_id)
                                st.metric("Musical Compatibility", f"{score}%")
                                st.progress(score / 100)

                                if common_artists:
                                    st.write(
                                        f"You both love: {', '.join([a.title() for a in common_artists[:5]])}")
                                else:
                                    st.write(
                                        "Opposites attract! No direct matches but good vibes.")
                            except spotipy.SpotifyException as e:
                                if e.http_status == 403:
                                    st.error("🚫 Access Forbidden (403).")
                                    st.warning(
                                        f"Spotify refuses to read this playlist ({partner_id}). Ensure it is PUBLIC or SHARED, or follow it in your library.")
                                else:
                                    st.error(f"Spotify Error: {e}")
                            except Exception as e:
                                st.error(f"Affinity Error: {e}")
            except Exception as e:
                st.error(f"Secret Error: {e}")

        elif vibe == "Party":
            guest_url = st.text_input(
                "Guest Playlist (Spotify URL)", placeholder="https://open.spotify.com/playlist/...")

        elif vibe == "Time Capsule":
            year = st.slider("Select Year", min_value=1950,
                             max_value=2025, value=2010)

        st.markdown("<br>", unsafe_allow_html=True)

        if 'preview_tracks' not in st.session_state:
            st.session_state.preview_tracks = None

        if st.button("Initialize Mix"):
            with st.spinner("Analyzing..."):
                try:
                    tracks = generator.generate_playlist_preview(
                        vibe, partner_id, guest_url, year)
                    if not tracks:
                        st.warning(
                            "No tracks found. Check input logic / discovery.")
                    else:
                        st.session_state.preview_tracks = tracks
                except Exception as e:
                    st.error(f"Generation Error: {e}")

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
                        st.error(f"Save Error: {e}")
                        st.warning("If error persists, try 'LOGOUT / RESET'.")

    except Exception as e:
        st.error(f"Critical Session Error: {e}")
        if st.button("Refresh"):
            st.session_state.token_info = None
            st.rerun()
