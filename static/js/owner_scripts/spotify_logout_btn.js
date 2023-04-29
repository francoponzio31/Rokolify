//TODO: implementar como evento al presionar un boton:

const url = 'https://www.spotify.com/logout/'                                                                                                                                                                                                                                                                               
const spotifyLogoutWindow = window.open(url, 'Spotify Logout', 'width=700,height=500,top=40,left=40')                                                                                                
setTimeout(() => spotifyLogoutWindow.close(), 2000)