
class User(dict):
    def __init__(self, email:str, name:str, given_name:str, family_name:str, profile_picture_url:str) -> None:
        self["email"] = email
        self["name"] = name
        self["given_name"] = given_name
        self["family_name"] = family_name
        self["profile_picture"] = profile_picture_url
        self["spotify_access_token_data"] = {}
        self["guest_access_links"] = []
        self["guest_settings"] = {
            "time_to_re_add_same_track": 20,  # Tiempo expresado en minutos
            "guest_permissions": {
                "allow_guest_access": True,
                "free_mode": True,
                "owner_playlists_access": True,
            },
            "playlists_settings": {},
            "tracks_recently_added_by_guests": {},
        }


"""
Ejemplo de documento de usuario:

{
    "email": "user@gmail.com",      # El email sirve como identificador del usuario
    "name": "franco ponzio",
    "given_name": "franco",
    "family_name": "ponzio",
    "profile_picture": "profile_picture_url",
    "spotify_access_token_data": {
        "access_token":"...",
        "token_type":"Bearer",
        "expires_in":"3600",
        "refresh_token":"...",
        "scope":"...",
        "requested_at":"2023-03-13 00:17:41"
    },
    "guest_access_links": [
        {
            "id": uuid,
            "host_email": "user@gmail.com",
            "description": "description",
            "created_on": "%d/%m/%Y %H:%M",
            "expiration_datetime": "%d/%m/%Y %H:%M" or None
            "timezone": "America/Buenos_Aires",
            "token": "AQRa_SzLpYAavoqvYihMLYTiJgEJPGpncvdjfE"
        }
    ],
    "guest_settings": {
        "time_to_re_add_same_track": 20,    # (mins)
        "cooldown_time_to_add": 30,     # (segs)
        "guest_permissions": {
            "allow_guest_access":False,
            "free_mode": true,
            "owner_playlists_access": true
        },
        "playlists_settings": {
            "playlist_id": {
                "allowed": true,
                "conditions":[
                    {
                        "id": uuid,
                        "day": int,
                        "init_time": str ("HH:MM"),
                        "end_time": str ("HH:MM"),
                        "timezone": str,
                    }
                ]
            },
            "playlist_id": {
                "allowed": true,
                "conditions": []
            },
        },
        "tracks_recently_added_by_guests": {
            "track_id":{
                "added_at": "timestamp"
            },
            "track_id":{
                "added_at": "timestamp"
            },
        },
        "recent_guest_interventions": {
            "guest_id":{
                "last_song_added":"track_uri",
                "added_at": "timestamp"
            },
            "guest_id":{
                "last_song_added":"track_uri",
                "added_at": "timestamp"
            },
        }
    }
}
"""
