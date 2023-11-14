import requests


"""
Este modulo contiene funciones que permiten obtener información del cátalogo de spotify.
"""


def get_playlist(spotify_access_token, playlist_id, fields=""):

    """
    Retorna información de los items de una playlist.
    """

    if fields:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}?fields={fields}"
    else:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

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


def get_playlist_items(spotify_access_token, playlist_id, offset=0, limit=20):

    """
    Retorna los items de una playlist.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}"

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


def check_if_users_follow_playlist(spotify_access_token, users_id, playlist_id):
    
    """
    Chequea si una lista de usuarios sigue una playlist. La lista de usuarios debe ser pasada como una lista separada por comas de id de usuario de Spotify, valor de ejemplo: "jmperezperez,thelinmichael,wizzler".
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains?ids={users_id}"

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


def search_tracks_in_catalog(spotify_access_token, search_str):

    """
    Busca una canción en el catalogo de spotify.
    """

    url = f"https://api.spotify.com/v1/search?q={search_str}&type=track&limit=40"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        data = data["tracks"]
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def get_track(spotify_access_token, track_id):

    """
    Retorna los datos de una canción.
    """

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

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


def get_artist(spotify_access_token, artist_id):

    """
    Retorna los datos de un artista.
    """

    url = f"https://api.spotify.com/v1/artists/{artist_id}"

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


def check_if_track_is_in_playlist(spotify_access_token, track_uri, playlist_id, playlist_track_index):

    """
        Valida que la canción cuyo uri se pasa por parametro se encuentre en la playlist cuyo id se pasa por parametro. Para esto se toma el indice en donde se encuentra la canción dentro de la lista de items de la playlist (dato que se pasa por parámetro), se hace una request para obtener el item de la playlist en ese indice, y se valida que coincidan con el que se paso como parámetro.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={playlist_track_index}&limit=1&fields=items.track.uri"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()

    else:
        return False, {"status_code": response.status_code}

    # Se valida que la canción obtenida en la petición a la api de spotify coincida con la que se pasa por parámetro:
    playlist_item = data["items"][0]
    track_is_in_playlist = playlist_item["track"]["uri"] == track_uri

    return track_is_in_playlist


def check_if_playlist_is_in_user_playlists(spotify_access_token, user_id, playlist_data):

    """
        Valida que la playlist cuyo id se pasa por parametro este entre las playlists del usuario dado, esto es, que el usuario siga o sea propietario de la playlist.
    """

    playlist_id = playlist_data["id"]

    # Se chequea si el usuario es propietario:
    if playlist_data["owner"]["id"] == user_id:
        return True

    # Se chequea si el usuario sigue a la playlist:
    follows_success, follows_response = check_if_users_follow_playlist(spotify_access_token, user_id, playlist_id)
    if follows_success and any(follows_response):
        return True

    # Si nada se cumple se toma como que la playlist no esta entre las playlist del usuario:
    return False
