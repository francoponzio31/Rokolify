from ..db_connection import connect_to_db
from datetime import datetime
import pytz


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
def set_allow_playlist_settings(owner_email, playlist_id, allow_value):
    user_data = get_user_data(owner_email)
    playlists_settings = user_data["guest_settings"]["playlists_settings"]
    
    if playlist_id not in playlists_settings:
        playlists_settings[playlist_id] = {
            "allowed": allow_value,
            "conditions": []
        }

    else:
        playlists_settings[playlist_id]["allowed"] = allow_value

    collection.update_one({"email": owner_email}, {"$set":{"guest_settings.playlists_settings": playlists_settings}})


def add_allow_playlist_condition(owner_email, playlist_id, new_condition):
    user_data = get_user_data(owner_email)
    playlists_settings = user_data["guest_settings"]["playlists_settings"]
    
    if playlist_id not in playlists_settings:
        playlists_settings[playlist_id] = {
            "allowed": True,
            "conditions": [new_condition]
        }

    else:
        playlists_settings[playlist_id]["conditions"].append(new_condition)

    collection.update_one({"email": owner_email}, {"$set":{"guest_settings.playlists_settings": playlists_settings}})


def delete_allow_playlist_condition(owner_email, playlist_id, condition_id):

    user_data = get_user_data(owner_email)
    playlists_settings = user_data["guest_settings"]["playlists_settings"]
    
    if playlist_id in playlists_settings:
        for index, condition in enumerate(playlists_settings[playlist_id]["conditions"]):
            if condition["id"] == condition_id:
                playlists_settings[playlist_id]["conditions"].pop(index)
                break

    collection.update_one({"email": owner_email}, {"$set":{"guest_settings.playlists_settings": playlists_settings}})


def check_if_playlist_is_allowed_by_user(user_data, playlist_id):
    
    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]

    # Si hay una configuración seteada para la playlist se evalua
    if playlist_id in playlists_access_settings:

        if playlists_access_settings[playlist_id].get("allowed") is False:
            return False
        
        if playlists_access_settings[playlist_id].get("conditions"):
            for condition in playlists_access_settings[playlist_id]["conditions"]:
                if _playlist_allow_condition_evaluation(condition) is True:
                    return True
                
            # Si ninguna de la condiciones se evaluó como verdadera se retorna False
            return False
        
        # Si "allowed" no es False, y no hay condiciones configuradas
        else:
            return True

    # Si no hay nada configurado para la playlist simplemente se considera habilitada
    return True


def _playlist_allow_condition_evaluation(playlist_allow_condition):
    """ La estructura esperada de una condición de habilitación de playlist es:
        {
            "id": uuid,
            "day": int,
            "init_time": str ("HH:MM"),
            "end_time": str ("HH:MM"),
            "timezone": str,
        }
    """
    # Obtener los datos de la condición
    day = playlist_allow_condition.get("day")
    init_time_str = playlist_allow_condition.get("init_time")
    end_time_str = playlist_allow_condition.get("end_time")
    timezone_str = playlist_allow_condition.get("timezone")

    # Convertir la hora de inicio y fin a objetos time
    init_time = datetime.strptime(init_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()

    try:
        # Obtener la zona horaria del diccionario
        timezone = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        # En caso de error al obtener la zona horaria, establecer la zona de Buenos Aires
        timezone = pytz.timezone("America/Buenos_Aires")

    # Obtener la hora actual en la zona horaria dada
    current_time = datetime.now(timezone).time()

    # Obtener el día de la semana actual (0 para lunes, 1 para martes, etc.)
    current_day = datetime.now(timezone).weekday()

    # Validar si se cumplen las condiciones
    if (day == current_day or day == -1) and init_time <= current_time <= end_time:
        return True
    else:
        return False


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
