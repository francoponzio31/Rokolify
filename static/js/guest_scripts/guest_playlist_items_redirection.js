setPlaylistsCardsEventListeners()

function setPlaylistsCardsEventListeners(){
   
    const playlistCards = document.querySelectorAll(".playlist-card");
    
    playlistCards.forEach(card => {
        if (!card.hasRedirectionEvent){
            card.addEventListener("click", ()=>{
                const playlistId = card.getAttribute("data-playlist-id");
                const itemsURL = `/guest/playlist/${playlistId}`;
                window.location.href = itemsURL;
            })
            card.hasRedirectionEvent = true;
        }
    });
}