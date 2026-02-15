import spotipy
import random
import re


class PlaylistGenerator:
    def __init__(self, sp):
        self.sp = sp

    def _extract_id(self, url_or_id):
        if not url_or_id:
            return None
        # Clean query params first
        url_or_id = url_or_id.split('?')[0]
        # Extract ID from URL if present (e.g. .../playlist/ID)
        match = re.search(r'playlist/([a-zA-Z0-9]+)', url_or_id)
        if match:
            return match.group(1)
        # Handle URI format (spotify:user:playlist:ID)
        if 'spotify:playlist:' in url_or_id:
            return url_or_id.split(':')[-1]
        return url_or_id.strip()

    def get_user_top_tracks(self, limit=20, time_range='medium_term'):
        try:
            results = self.sp.current_user_top_tracks(
                limit=limit, time_range=time_range)
            return results['items']
        except:
            return []

    def get_playlist_tracks(self, playlist_id):
        clean_id = self._extract_id(playlist_id)
        if not clean_id:
            return []

        try:
            # Use playlist_items (newer endpoint)
            results = self.sp.playlist_items(
                clean_id, additional_types=['track'])
            tracks = results['items']

            # Simple pagination to get at least 100 tracks if available
            while results['next'] and len(tracks) < 100:
                results = self.sp.next(results)
                tracks.extend(results['items'])

            return [t['track'] for t in tracks if t.get('track')]
        except Exception:
            # Fallback to direct API call if wrapper fails
            try:
                results = self.sp._get(
                    f"playlists/{clean_id}/tracks", limit=50)
                return [t['track'] for t in results['items'] if t.get('track')]
            except Exception:
                return []

    def calculate_affinity(self, partner_playlist_id):
        # Fetch Top Artists from ALL time ranges for better accuracy
        ranges = ['short_term', 'medium_term', 'long_term']
        my_artists = set()

        for time_range in ranges:
            try:
                data = self.sp.current_user_top_artists(
                    limit=50, time_range=time_range)
                for item in data.get('items', []):
                    my_artists.add(item['name'].lower())
            except:
                pass

        clean_id = self._extract_id(partner_playlist_id)
        if not clean_id:
            return 0, []

        partner_tracks = self.get_playlist_tracks(clean_id)
        if not partner_tracks:
            return 0, []

        partner_artists = set()
        for t in partner_tracks:
            # Handle track['artists'] list safely
            if 'artists' in t:
                for a in t['artists']:
                    partner_artists.add(a['name'].lower())

        common = my_artists.intersection(partner_artists)

        # Calculate Score
        if not my_artists:
            return 0, []

        # Base score: % of playlist artists that match my known favorites
        # We divide by len(partner_artists) because we want to know
        # "How much of THIS playlist do I like?"
        if not partner_artists:
            return 0, []

        score = int((len(common) / len(partner_artists)) * 100)

        # Boost logic: if > 20% match, we curve it up to make it feel better
        if score > 20:
            score = min(100, score + 20)
        if score > 80:  # If it's really high, just give 100
            score = 100

        return score, list(common)

    def generate_playlist_preview(self, vibe, partner_id=None, guest_playlist_url=None, year=None):
        final_tracks = []

        if vibe == "Chill":
            final_tracks = self.get_user_top_tracks(
                limit=50, time_range='medium_term')
            random.shuffle(final_tracks)

        elif vibe == "Throwback":
            final_tracks = self.get_user_top_tracks(
                limit=50, time_range='long_term')
            random.shuffle(final_tracks)

        elif vibe == "Energy":
            final_tracks = self.get_user_top_tracks(
                limit=50, time_range='short_term')
            random.shuffle(final_tracks)

        elif vibe == "Time Capsule" and year:
            results = self.sp.search(q=f'year:{year}', type='track', limit=10)
            if not results or 'tracks' not in results or not results['tracks']['items']:
                final_tracks = []
            else:
                final_tracks = results['tracks']['items']
                random.shuffle(final_tracks)

        elif vibe == "Love" and partner_id:
            my_tracks = self.get_user_top_tracks(
                limit=30, time_range='medium_term')
            partner_tracks = self.get_playlist_tracks(partner_id)

            random.shuffle(my_tracks)
            random.shuffle(partner_tracks)

            max_len = max(len(my_tracks), len(partner_tracks))
            for i in range(max_len):
                if i < len(my_tracks):
                    final_tracks.append(my_tracks[i])
                if i < len(partner_tracks):
                    final_tracks.append(partner_tracks[i])

        elif vibe == "Party" and guest_playlist_url:
            my_tracks = self.get_user_top_tracks(
                limit=30, time_range='short_term')
            guest_tracks = self.get_playlist_tracks(guest_playlist_url)

            random.shuffle(my_tracks)
            random.shuffle(guest_tracks)

            max_len = max(len(my_tracks), len(guest_tracks))
            for i in range(max_len):
                if i < len(my_tracks):
                    final_tracks.append(my_tracks[i])
                if i < len(guest_tracks):
                    final_tracks.append(guest_tracks[i])

        else:
            final_tracks = self.get_user_top_tracks(
                limit=50, time_range='medium_term')

            # --- CHILL VIBE LOGIC ---
            if vibe == "Chill":
                final_tracks = self._filter_by_vibe(
                    final_tracks, target_energy=0.5, target_valence=0.5)
            # ------------------------

            random.shuffle(final_tracks)

        return final_tracks[:50]

    def _filter_by_vibe(self, tracks, target_energy, target_valence):
        """Filter tracks based on Spotify Audio Features."""
        if not tracks:
            return []

        track_ids = [t['id'] for t in tracks]
        # Chunk into 100s for audio_features API
        features = []
        for i in range(0, len(track_ids), 100):
            chunk = track_ids[i:i+100]
            features.extend(self.sp.audio_features(chunk))

        filtered = []
        for t, f in zip(tracks, features):
            if f:
                # Chill criteria: Low Energy (< 0.6)
                if f['energy'] < 0.6:
                    filtered.append(t)

        return filtered if filtered else tracks  # Fallback to all if too strict

    def create_playlist_from_tracks(self, user_id, tracks, vibe, playlist_name_input=None):
        if playlist_name_input:
            playlist_name = playlist_name_input
        else:
            playlist_name = f"Mix {vibe}"

        description = f"Generated for {vibe} vibe"

        # Try direct API call to /me/playlists to match docs and avoid user ID issues
        # (Equivalent to POST https://api.spotify.com/v1/me/playlists)
        try:
            playlist = self.sp.user_playlist_create(
                user_id, playlist_name, public=True, description=description)
        except Exception:
            # Fallback: strict adherence to docs using /me/playlists
            data = {
                "name": playlist_name,
                "public": True,
                "description": description
            }
            playlist = self.sp._post("me/playlists", payload=data)

        playlist_id = playlist['id']

        track_uris = [t['uri'] for t in tracks]

        if track_uris:
            unique_uris = []
            seen = set()
            for uri in track_uris:
                if uri not in seen:
                    unique_uris.append(uri)
                    seen.add(uri)

            # Split into chunks of 100 (API limit)
            for i in range(0, len(unique_uris), 100):
                batch = unique_uris[i:i+100]
                # Direct API call as per docs: POST https://api.spotify.com/v1/playlists/{playlist_id}/items
                try:
                    self.sp._post(
                        f"playlists/{playlist_id}/items",
                        payload={"uris": batch}
                    )
                except Exception as e:
                    print(f"Error adding batch {i}: {e}")
                    # Try fallback specific to some token types
                    self.sp.playlist_add_items(playlist_id, batch)

        return playlist['external_urls']['spotify']

# Updated: Accepts sp client directly


def get_generator(sp):
    return PlaylistGenerator(sp)
