import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from backend.logic import get_generator

# Configuration minimaliste
st.set_page_config(
    page_title="mon cadeau ❤️",
    page_icon="💌",
    layout="centered"
)

# CSS pour le thème rose et les coeurs
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
        color: #5e3b4d;
    }
    
    /* Background Gradient Rose */
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #ffe6ea 100%);
    }
    
    /* Boutons Arrondis et Roses */
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #ff8fa3;
        color: white;
        border: none;
        font-weight: 600;
        font-size: 16px;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
        box-shadow: 0 4px 6px rgba(255, 143, 163, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #ff6b85;
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(255, 143, 163, 0.4);
        color: white;
    }

    /* Inputs plus doux */
    .stTextInput>div>div>input {
        border-radius: 20px;
        border: 1px solid #ffd1dc;
        background-color: white;
        color: #5e3b4d;
    }
    
    /* Titres */
    h1 {
        color: #d65a75;
        font-weight: 700 !important;
        text-align: center;
    }
    
    h3 {
        color: #ea8a9f;
        font-weight: 500 !important;
    }

    /* Track Preview Card */
    .track-card {
        background: white;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 8px;
        border: 1px solid #ffe6ea;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
    }

    .big-link {
        display: block;
        background-color: #ff8fa3;
        color: white !important;
        padding: 15px;
        border-radius: 30px;
        text-align: center;
        font-weight: 600;
        text-decoration: none;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(255, 143, 163, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# Header avec Coeurs
st.markdown("<h1 style='font-size: 3em;'>💌 spotify mixer 💌</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ea8a9f;'>spécialement pour toi</p>",
            unsafe_allow_html=True)

if 'token_info' not in st.session_state:
    st.session_state.token_info = None

# Gestion Secrets
try:
    client_id = st.secrets["SPOTIPY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
    redirect_uri = st.secrets["SPOTIPY_REDIRECT_URI"]
except FileNotFoundError:
    st.error("configuration manquante")
    st.stop()

# Auth
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
        st.error("erreur connexion")
        st.stop()

auth_token = None
if st.session_state.token_info:
    token_info = st.session_state.token_info
    if oauth.is_token_expired(token_info):
        token_info = oauth.refresh_access_token(token_info['refresh_token'])
        st.session_state.token_info = token_info
    auth_token = token_info['access_token']

# --- APP LOGIC ---

if not auth_token:
    auth_url = oauth.get_authorize_url()
    st.markdown(f"<br><br>", unsafe_allow_html=True)
    st.markdown(f'''
        <a href="{auth_url}" target="_blank" style="text-decoration:none;">
            <div style="background:#ff8fa3; color:#fff; padding:15px; border-radius:30px; text-align:center; font-weight:600; box-shadow: 0 4px 10px rgba(255,143,163,0.3);">
                ✨ se connecter
            </div>
        </a>
    ''', unsafe_allow_html=True)

else:
    sp = spotipy.Spotify(auth=auth_token)
    user = sp.current_user()
    generator = get_generator(auth_token)

    st.write(f"coucou {user['display_name'].lower()} 💕")
    st.markdown("---")

    # ÉTAPE 1 : CHOIX VIBE
    st.markdown("### 1. choisis l'ambiance")

    cols = st.columns(4)
    vibes = [
        ("☕", "chill"),
        ("🚗", "roadtrip"),
        ("🎉", "soirée"),
        ("❤️", "love")
    ]

    # Custom Radio (Hack ou juste propre)
    vibe = st.radio("vibe", [v[1] for v in vibes], label_visibility="collapsed",
                    horizontal=True, format_func=lambda x: f" {x}")
    st.caption(f"mode sélectionné : {vibe}")

    # Inputs Conditionnels
    partner_id = None
    guest_url = None

    if vibe == "love":
        # Check secret
        try:
            partner_id = st.secrets["PARTNER_PLAYLIST_ID"]
            if partner_id and "YOUR" not in partner_id:
                st.info("💕 avec la playlist de ton chéri")
        except:
            pass

    elif vibe == "soirée":
        guest_url = st.text_input("lien playlist d'un ami (optionnel)")

    st.markdown("<br>", unsafe_allow_html=True)

    # État pour la prévisualisation
    if 'preview_tracks' not in st.session_state:
        st.session_state.preview_tracks = None

    if st.button("✨ préparer le mix ✨"):
        with st.spinner("préparation de la magie..."):
            tracks = generator.generate_playlist_preview(
                vibe, partner_id, guest_url)
            st.session_state.preview_tracks = tracks

    # ÉTAPE 2 : PREVIEW & SAVE
    if st.session_state.preview_tracks:
        st.markdown("### 2. aperçu du mix")

        # Afficher quelques titres
        preview_container = st.container()
        with preview_container:
            for track in st.session_state.preview_tracks[:5]:
                artists = ", ".join([a['name'].lower()
                                    for a in track['artists']])
                name = track['name'].lower()
                st.markdown(f"""
                <div class="track-card">
                    <span style="font-size:20px;">🎶</span>
                    <div>
                        <div style="font-weight:600;">{name}</div>
                        <div style="color:#999; font-size:12px;">{artists}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if len(st.session_state.preview_tracks) > 5:
                st.caption(
                    f"... et {len(st.session_state.preview_tracks)-5} autres titres")

        st.markdown("### 3. personnalisation")
        msg = st.text_input("un petit mot pour la description ?",
                            placeholder="profite bien mon coeur...")

        if st.button("💖 valider et créer sur spotify 💖"):
            with st.spinner("envoi vers spotify..."):
                try:
                    url = generator.create_playlist_from_tracks(
                        user['id'],
                        st.session_state.preview_tracks,
                        vibe,
                        custom_message=msg
                    )
                    st.balloons()
                    st.success("c'est tout bon !")
                    st.markdown(f'''
                        <a href="{url}" target="_blank" class="big-link">
                            écouter maintenant 🎧
                        </a>
                    ''', unsafe_allow_html=True)
                except Exception as e:
                    st.error("oups erreur")
