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

    collection.update_one({"email":owner_email}, {"$set":{"guest_settings.playlists_settings": playlists_settings}})

    updated_user_data = get_user_data(owner_email)
    updated_playlists_settings = updated_user_data["guest_settings"]["playlists_settings"]

    return updated_playlists_settings


def check_if_playlist_is_allowed_by_user(user_data, playlist_id):
    
    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]

    # Si hay una configuración seteada para la playlist se evalua:
    if playlist_id in playlists_access_settings:

        if playlists_access_settings[playlist_id].get("allowed") is True:
            return True

        # (Aca se pueden validar playlists por otras condiciones como horarios o dias)

    # Si no hay nada configurado para la playlist simplemente se agrega:
    else:   
        return True


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
    

def check_if_guest_is_allowed_to_add_to_queue(user_data, guest_id):

    cooldown_time_to_add = user_data["guest_settings"].get("cooldown_time_to_add", 0)   # Tiempo para que un invitado pueda volver a agregar una canción, expresado en segundos
    recent_guest_interventions = user_data["guest_settings"].get("recent_guest_interventions", [])

    # Se chequea si la cancion fue agregada recientemente por un invitado:
    guest_cooldown_has_ended = True
    if guest_id in recent_guest_interventions:
        seconds_since_added = (datetime.now() - recent_guest_interventions[guest_id]["added_at"]).total_seconds()
        if seconds_since_added < cooldown_time_to_add:
            guest_cooldown_has_ended = False

    return guest_cooldown_has_ended


def add_recently_added_track_by_guest(user_data, guest_id, track_uri):
    
    """
    Se actualiza la lista de canciones agregadas recientemente por invitados y la lista de intervenciones por invitados (filtrando las que ya estan habilitadas para ser agregadas nuevamente) y se agrega la cancion pasada por parametro.
    """
    
    time_to_re_add_same_track = user_data["guest_settings"].get("time_to_re_add_same_track", 0)   # Tiempo para volver a agregar la misma canción, expresado en minutos
    recently_added_tracks = user_data["guest_settings"].get("tracks_recently_added_by_guests", [])

    # Se filtra la lista de canciones agregadas recientemente por usuarios eliminando las que fueron agregadas hace mas tiempo del tiempo configurado 
    updated_recently_added_tracks = {}
    for track in recently_added_tracks:
        time_since_added = (datetime.now() - recently_added_tracks[track]["added_at"]).total_seconds()
        minutes_since_added = time_since_added // 60    # Tiempo desde que se agrego la canción en minutos
        if minutes_since_added < time_to_re_add_same_track:
            updated_recently_added_tracks[track] = recently_added_tracks[track]
    # Se agrega la canción pasada por parametro:
    updated_recently_added_tracks[track_uri] = {"added_at": datetime.now()}


    cooldown_time_to_add = user_data["guest_settings"].get("cooldown_time_to_add", 0)   # Tiempo para que un invitado pueda volver a agregar una canción, expresado en segundos
    recent_guest_interventions = user_data["guest_settings"].get("recent_guest_interventions", [])

    # Se filtra la lista de canciones agregadas recientemente por usuarios eliminando las que fueron agregadas hace mas tiempo del tiempo configurado 
    updated_recent_guest_interventions = {}
    for guest in recent_guest_interventions:
        time_since_added = (datetime.now() - recent_guest_interventions[guest]["added_at"]).total_seconds()   # Tiempo desde que se agrego la canción en segundos
        if time_since_added > cooldown_time_to_add:
            updated_recent_guest_interventions[guest] = recent_guest_interventions[guest]
    # Se agrega la canción pasada por parametro:
    updated_recent_guest_interventions[guest_id] = {
        "last_song_added": track_uri,
        "added_at": datetime.now()
    }

    collection.update_one({"email":user_data["email"]}, {"$set":{
        "guest_settings.tracks_recently_added_by_guests": updated_recently_added_tracks,
        "guest_settings.recent_guest_interventions": updated_recent_guest_interventions
    }})
