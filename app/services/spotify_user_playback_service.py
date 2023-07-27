import requests
import json


"""
Este modulo contiene funciones que permiten obtener información o manipular el reproductor de la cuenta de spotify.
"""


def get_available_devices(spotify_access_token):

    """
    Retorna una lista con datos de los reproductores activos.
    """

    url = "https://api.spotify.com/v1/me/player/devices"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        devices = data["devices"]
        return True, devices
    
    else:
        return False, {"status_code": response.status_code}


def get_playback_state(spotify_access_token):

    """
    Retorna datos del reproductor activo actualmente. Debe existir un reproductor activo para que la request tenga éxito.
    """

    url = "https://api.spotify.com/v1/me/player"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def pause_playback(spotify_access_token):

    """
    Pausa la reproducción del reproductor activo. Debe existir un reproductor activo reproduciendose.
    """

    url = "https://api.spotify.com/v1/me/player/pause"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)

    if response.status_code in (200, 204):
        # La solicitud fue exitosa
        data = response.status_code
        return True, data
    
    
    else:
        return False, {"status_code": response.status_code}


def resume_playback(spotify_access_token):

    """
    Reanuda la reproducción del reproductor activo. Debe existir un reproductor activo pausado.
    """

    url = "https://api.spotify.com/v1/me/player/play"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)

    if response.status_code in (200, 204):
        # La solicitud fue exitosa
        data = response.status_code
        return True, data
    
    
    else:
        return False, {"status_code": response.status_code}


def push_to_player(spotify_access_token, element_type, uri, device_id=None):

    """
    Inserta una canción o playlist para reproducrise inmediatamente. Al ejecutarse limpia la cola de reproducción.
    """

    if device_id:
        url = f"https://api.spotify.com/v1/me/player/play?device_id={device_id}"
    else:
        url = "https://api.spotify.com/v1/me/player/play"        

    if element_type == "playlist":
        body = {"context_uri": uri}
    elif element_type == "track":
        body =  {"uris": [uri]}
    else:
        return False, {"error": "Argumentos inválidos"}
    
    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers, data=json.dumps(body))

    if response.status_code in (200, 204):
        # La solicitud fue exitosa
        data = response.status_code
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def get_user_queue(spotify_access_token):

    #!: La respuesta de la api solo trae los primeros 20 elementos de las cola de reproducción.

    #TODO: error al tener pocos items en la cola, se repiten

    """
    Retorna información sobre la cola de reproducción del usuario.
    """

    url = "https://api.spotify.com/v1/me/player/queue"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def add_item_to_queue(spotify_access_token, item_uri, device_id=None):

    """
    Añade una canción a la cola de reproducción.
    """

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    if device_id:
        url = f"https://api.spotify.com/v1/me/player/queue?uri={item_uri}&device_id={device_id}"
    else:
        url = f"https://api.spotify.com/v1/me/player/queue?uri={item_uri}"

    response = requests.post(url, headers=headers)

    if response.status_code == 204:
        return True, {"message": "Item agregdo a la cola", "status_code": response.status_code}

    return False, {"status_code": response.status_code}

def add_playlist_to_queue(spotify_access_token, playlist_id, device_id=None):

    #TODO: Desarrollar esta funcion para automatizar el reproductor

    """
    Añade una canción a la cola de reproducción.
    """

    # URL para agregar a la cola de reproducción
    url = "https://api.spotify.com/v1/me/player/queue"

    # Headers de la solicitud, incluyendo el token de acceso
    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    # Cuerpo de la solicitud, incluyendo el URI de la lista de reproducción
    data = {
        "uri": f"spotify:playlist:{playlist_id}"
    }
    # Convertir el cuerpo de la solicitud a JSON
    payload = json.dumps(data)
    
    # Realiza la solicitud POST
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 204:
        return True, {"message": "Item agregdo a la cola", "status_code": response.status_code}

    return False, {"status_code": response.status_code}


def skip_to_next(spotify_access_token, device_id=None):

    """
    Avanza a la siguiente canción en la cola de reproducción.
    """

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    if device_id:
        url = f"https://api.spotify.com/v1/me/player/next?device_id={device_id}"
    else:
        url = "https://api.spotify.com/v1/me/player/next"

    response = requests.post(url, headers=headers)

    if response.status_code == 204:
        return True, {"message": "Item salteado", "status_code": response.status_code}

    return False, {"status_code": response.status_code}
