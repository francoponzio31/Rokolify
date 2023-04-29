
class User(dict):
    def __init__(self, email:str, access_token_data:dict) -> None:
        self["email"] = email
        self["access_token_data"] = access_token_data
        self["guest_settings"] = {
            "time_to_re_add_same_track": 1800,
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
    "email": "user@gmail.com",
    "acces_token_data": {
        "access_token":"...",
        "token_type":"Bearer",
        "expires_in":"3600",
        "refresh_token":"...",
        "scope":"...",
        "requested_at":"2023-03-13 00:17:41"
    },
    "guest_settings": {
        "guest_permissions": {
            "allow_guest_access":False,
            "free_mode": true,
            "owner_playlists_access": true
        },
        "playlists_settings": {
            "playlist_id": {
                "allowed": true,
                "conditions":{
                    "days": [1,2,5],
                    "hour_range":[["10:30","14:15"], ["18:20","21:00"]]
                }
            },
            "playlist_id": {
                "allowed": true,
                "conditions":{}
            },
            "playlist_id": {
                "allowed": true,
                "conditions":{
                    "days": [2,5]
                }
            },
        },
        "tracks_recently_added_by_guests": {
            "track_id":{
                "added_at": "timestamp"
            }
        }
    }
}
"""
