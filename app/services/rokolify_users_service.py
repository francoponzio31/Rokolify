from ..db_connection import connect_to_db
from datetime import datetime


db = connect_to_db()
collection = db["users"]

# ? User functions ---------------------------------------------------------
def get_user_data(owner_email):
    user = collection.find_one({"email":owner_email})
    if user:
        return user
    else:
        return None


def add_user(user_data):
    created_user = collection.insert_one(user_data)
    return {"created_user_id":str(created_user.inserted_id)}


def update_user(owner_email, new_values):
    collection.update_one({"email":owner_email}, {"$set":new_values})
    return {"updated_user_email":owner_email}


# ? Guest permissions --------------------------------------------------------
def update_guest_permission(owner_email, permission, new_value):
    collection.update_one({"email":owner_email}, {"$set":{f"guest_settings.guest_permissions.{permission}": new_value}})
    return {"updated_user_email":owner_email}


# ? Playlist access settings -------------------------------------------------
def update_playlists_access_settings(owner_email, new_settings):

    user_data = get_user_data(owner_email)
    playlists_settings = user_data["guest_settings"]["playlists_settings"]

    for playlist_id in new_settings:
        if playlist_id not in playlists_settings:
            playlists_settings[playlist_id] = {}

        if "allowed" in new_settings[playlist_id]:
            playlists_settings[playlist_id]["allowed"] = new_settings[playlist_id]["allowed"]

    collection.update_one({"email":owner_email}, {"$set":{f"guest_settings.playlists_settings": playlists_settings}})

    updated_user_data = get_user_data(owner_email)
    updated_playlists_settings = updated_user_data["guest_settings"]["playlists_settings"]

    return updated_playlists_settings


# ? App register for recently added tracks by guests ---------------------------------------
def check_if_track_was_recently_added_by_guests(user_data, track_uri):

    recently_added_tracks = user_data["guest_settings"]["tracks_recently_added_by_guests"]
    minutes_to_re_add = user_data["guest_settings"]["time_to_re_add_same_track"]   # Tiempo para volver a agregar la misma canción, expresado en minutos

    # Se chequea si la cancion fue agregada recientemente por un invitado:
    track_was_recently_added = False
    if track_uri in recently_added_tracks:
        seconds_since_added = (datetime.now() - recently_added_tracks[track_uri]["added_at"]).total_seconds()
        minutes_since_added = seconds_since_added // 60
        if minutes_since_added < minutes_to_re_add:
            track_was_recently_added = True

    return track_was_recently_added
    

def add_recently_added_track_by_guest(user_data, track_uri):
    
    """
    Se actualiza la lista de canciones agregadas recientemente por usuarios (filtrando las que ya estan habilitadas apra ser agregadas nuevamente) y se agrega la cancion pasada por parametro.
    """
    
    recently_added_tracks = user_data["guest_settings"]["tracks_recently_added_by_guests"]
    minutes_to_re_add = user_data["guest_settings"]["time_to_re_add_same_track"]   # Tiempo para volver a agregar la misma canción, expresado en minutos

    # Se filtra la lista de canciones agregadas recientemente por usuarios eliminando las que fueron agregadas hace mas tiempo del tiempo configurado 
    updated_recently_added_tracks = {}
    for track in recently_added_tracks:
        time_since_added = (datetime.now() - recently_added_tracks[track]["added_at"]).total_seconds()
        if time_since_added < minutes_to_re_add:
            updated_recently_added_tracks[track] = recently_added_tracks[track]

    # Se agrega la canción pasada por parametro:
    updated_recently_added_tracks[track_uri] = {"added_at": datetime.now()}

    collection.update_one({"email":user_data["email"]}, {"$set":{f"guest_settings.tracks_recently_added_by_guests": updated_recently_added_tracks}})