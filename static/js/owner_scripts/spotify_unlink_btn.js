const spotifyUnlinkBtn = document.getElementById("unlink-spotify-account-btn");

spotifyUnlinkBtn.addEventListener("click", ()=>{  
    fetch("/owner/api/unlink_spotify_account")
    .then(() => {
        location.reload();
    })
})