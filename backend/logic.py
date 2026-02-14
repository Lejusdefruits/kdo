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

    def generate_playlist_preview(self, vibe, partner_id=None, guest_playlist_url=None):
        my_top_tracks = self.get_user_top_tracks(limit=30)
        my_tracks = [t for t in my_top_tracks]

        secondary_tracks = []

        if vibe == "romantique" and partner_id:
            secondary_tracks = self.get_playlist_tracks(partner_id)

        elif vibe == "soirée" and guest_playlist_url:
            secondary_tracks = self.get_playlist_tracks(guest_playlist_url)

        final_tracks = []

        if secondary_tracks:
            random.shuffle(my_tracks)
            random.shuffle(secondary_tracks)

            max_len = max(len(my_tracks), len(secondary_tracks))
            for i in range(max_len):
                if i < len(my_tracks):
                    final_tracks.append(my_tracks[i])
                if i < len(secondary_tracks):
                    final_tracks.append(secondary_tracks[i])
        else:
            final_tracks = my_tracks
            random.shuffle(final_tracks)

        # Return simpler objects for preview
        return final_tracks[:50]

    def create_playlist_from_tracks(self, user_id, tracks, vibe, custom_message=None):
        playlist_name = f"mix {vibe} 💖"
        description = f"playlist générée pour le mode {vibe}"

        if custom_message:
            description += f" - {custom_message}"

        playlist = self.sp.user_playlist_create(
            user_id, playlist_name, public=False, description=description)
        playlist_id = playlist['id']

        track_uris = [t['uri'] for t in tracks]

        if track_uris:
            # remove duplicates
            unique_uris = []
            seen = set()
            for uri in track_uris:
                if uri not in seen:
                    unique_uris.append(uri)
                    seen.add(uri)

            # Add in chunks of 100
            for i in range(0, len(unique_uris), 100):
                self.sp.playlist_add_items(playlist_id, unique_uris[i:i+100])

        return playlist['external_urls']['spotify']


def get_generator(token):
    sp = spotipy.Spotify(auth=token)
    return PlaylistGenerator(sp)
