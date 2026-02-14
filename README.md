# Spotify Mixer 🎧

Une application Streamlit pour générer des playlists personnalisées basées sur votre "Vibe".

## Installation

1.  Cloner ce dépôt.
2.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (Important !)

Pour que l'application puisse se connecter à Spotify, vous devez configurer les clés API.

1.  Allez sur le [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2.  Créez une nouvelle application.
3.  Notez le `Client ID` et le `Client Secret`.
4.  Dans les paramètres de l'application sur le dashboard Spotify, ajoutez l'URI de redirection :
    - Pour le local : `http://localhost:8501`
    - Pour Streamlit Cloud : `https://votre-app.streamlit.app`

### En local

Remplissez le fichier `.streamlit/secrets.toml` :

```toml
[general]
SPOTIPY_CLIENT_ID = "votre_client_id"
SPOTIPY_CLIENT_SECRET = "votre_client_secret"
SPOTIPY_REDIRECT_URI = "http://localhost:8501"
```

## Lancer l'application

```bash
streamlit run app.py
```

## Structure du projet

- `.streamlit/secrets.toml` : Contient vos secrets (ne jamais commiter ce fichier sur GitHub !).

## 🚀 Déploiement (Pour l'avoir sur tous les téléphones)

Pour que votre copine puisse l'utiliser sur son téléphone, il faut mettre l'application en ligne sur **Streamlit Cloud** (c'est gratuit).

### Étape 1 : Mettre le code sur GitHub
1.  Créez un compte sur [GitHub.com](https://github.com).
2.  Créez un **Nouveau Repository** (Public ou Privé).
3.  Envoyez vos fichiers (`app.py`, `requirements.txt`, `backend/`, `README.md`) sur ce repository.
    *   ⚠️ **IMPORTANT** : N'envoyez PAS le fichier `.streamlit/secrets.toml` ! Il doit rester secret.

### Étape 2 : Connecter Streamlit Cloud
1.  Allez sur [share.streamlit.io](https://share.streamlit.io/).
2.  Cliquez sur "New app".
3.  Sélectionnez votre repository GitHub et le fichier `app.py`.

### Étape 3 : Configurer les Secrets (CRUCIAL)
Avant de lancer l'app, cliquez sur "Advanced Settings..." (ou une fois l'app créée, dans les "Settings" -> "Secrets").
Vous devez copier-coller le contenu de votre fichier local `.streamlit/secrets.toml` dans la zone de texte des secrets de Streamlit Cloud :

```toml
[general]
SPOTIPY_CLIENT_ID = "..."
SPOTIPY_CLIENT_SECRET = "..."
SPOTIPY_REDIRECT_URI = "https://votre-app-nom.streamlit.app"
PARTNER_PLAYLIST_ID = "..."
```

### Étape 4 : Mettre à jour Spotify
1.  Une fois l'app déployée, vous aurez une URL du type `https://spotify-mixer-kdo.streamlit.app`.
2.  Retournez sur le [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
3.  Dans "Edit Settings", ajoutez cette NOUVELLE URL dans les **Redirect URIs**.
    *   Attention : L'URL doit être exacte (pas de `/` à la fin sauf si Streamlit l'ajoute).
4.  Sauvegardez.

Maintenant, vous pouvez envoyer le lien à votre copine ! 🎁
