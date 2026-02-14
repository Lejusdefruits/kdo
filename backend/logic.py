import spotipy
import random


class PlaylistGenerator:
    def __init__(self, sp):
        self.sp = sp

    def get_user_top_tracks(self, limit=20, time_range='medium_term'):
        results = self.sp.current_user_top_tracks(
            limit=limit, time_range=time_range)
        return results['items']

    def get_playlist_tracks(self, playlist_id):
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = results['items']
            return [t['track'] for t in tracks if t['track']]
        except Exception:
            return []

    def get_recommendations(self, seed_tracks, limit=50):
        try:
            seed_ids = [t['id'] for t in seed_tracks[:5]]
            results = self.sp.recommendations(
                seed_tracks=seed_ids, limit=limit)
            return results['tracks']
        except Exception:
            return []

    def calculate_affinity(self, partner_playlist_id):
        try:
            top_artists_data = self.sp.current_user_top_artists(
                limit=50, time_range='long_term')
            my_artists = {a['name'].lower() for a in top_artists_data['items']}

            partner_tracks = self.get_playlist_tracks(partner_playlist_id)
            partner_artists = set()
            for t in partner_tracks:
                for a in t['artists']:
                    partner_artists.add(a['name'].lower())

            common = my_artists.intersection(partner_artists)
            score = 0
            if partner_artists:
                score = int((len(common) / len(my_artists))
                            * 100) if my_artists else 0
                score = min(100, score * 3)

            if 0 < score < 50:
                score += 30
            elif score == 0 and common:
                score = 20

            return score, list(common)
        except Exception:
            return 0, []

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

        elif vibe == "Discovery":
            top_tracks = self.get_user_top_tracks(
                limit=5, time_range='short_term')
            final_tracks = self.get_recommendations(top_tracks, limit=50)

        elif vibe == "Time Capsule" and year:
            try:
                results = self.sp.search(
                    q=f'year:{year}', type='track', limit=50)
                final_tracks = results['tracks']['items']
                random.shuffle(final_tracks)
            except:
                final_tracks = []

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
            random.shuffle(final_tracks)

        return final_tracks[:50]

    def create_playlist_from_tracks(self, user_id, tracks, vibe, custom_message=None):
        playlist_name = f"Mix {vibe}"
        description = f"Generated for {vibe} vibe"

        if custom_message:
            description += f" - {custom_message}"

        playlist = self.sp.user_playlist_create(
            user_id, playlist_name, public=False, description=description)
        playlist_id = playlist['id']

        track_uris = [t['uri'] for t in tracks]

        if track_uris:
            unique_uris = []
            seen = set()
            for uri in track_uris:
                if uri not in seen:
                    unique_uris.append(uri)
                    seen.add(uri)

            for i in range(0, len(unique_uris), 100):
                self.sp.playlist_add_items(playlist_id, unique_uris[i:i+100])

        return playlist['external_urls']['spotify']


def get_generator(token):
    sp = spotipy.Spotify(auth=token)
    return PlaylistGenerator(sp)
