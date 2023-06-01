import requests


"""
Este modulo contiene funciones que permiten obtener información del perfil del dueño de la cuenta de spotify.
"""


def get_user_profile(spotify_access_token):

    """
    Retorna información del perfil del usuario actual.
    """
    
    url = "https://api.spotify.com/v1/me"

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


def get_user_playlists(spotify_access_token, offset=0, limit=20):

    """
    Retorna información de las playlists del usuario.
    """

    url = f"https://api.spotify.com/v1/me/playlists?offset={offset}&limit={limit}"

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
