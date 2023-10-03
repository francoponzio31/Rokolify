const loadMoreBtn = document.getElementById("load-more-tracks");
const playlistItemsContainer = document.getElementById("playlist-items-container");
const loadSpinner = document.getElementById("load-more-tracks-spinner");


const playlistTrackItemHtml = (trackName, trackImageURL, artist, trackId, trackURI, trackIndexInPlaylist) => {
    return `
    <div class="track-card card d-flex flex-row align-items-center pe-2 gap-3 bg-dark-subtle border-dark-subtle" data-item-id="${trackId}" data-item-uri="${trackURI}" data-playlist-track-index="${trackIndexInPlaylist}">
    ${
        trackImageURL
        ? `<img src="${trackImageURL}" class="item-image rounded-start" style="width:60px; max-height:60px;" alt="item-image" data-bs-toggle="modal" data-bs-target="#track-modal">`
        : ""
    }
    <div class="w-100 justify-content-between text-truncate" data-bs-toggle="modal" data-bs-target="#track-modal">
        <h5 class="card-title fs-6 fw-bold text-truncate mb-0">${trackName}</h5>
        <small>${artist}</small>
    </div>

    <button type="button" class="btn btn-primary btn-sm add-to-queue-btn rounded-pill">
        <img src="/static/img/bx-list-plus.svg" alt="add-to-queue-btn-icon">
    </button>
    </div>`
}

loadMoreBtn.addEventListener("click", ()=>{

    loadSpinner.classList.remove("d-none");
    loadMoreBtn.classList.add("d-none");

    nextItemsUrl = new URL(nextItemsUrl);

    // Se extraen los parametros de la url:
    const playlistId = nextItemsUrl.pathname.split("/")[3];
    const offset = nextItemsUrl.searchParams.get("offset");
    const limit = nextItemsUrl.searchParams.get("limit");

    fetch(`/guest/api/get_playlist_items/${playlistId}/${offset}/${limit}`)
    .then(response => {
        if (!response.ok){
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        
        loadSpinner.classList.add("d-none");

        nextItemsUrl = data.next;

        // Renderizado de items:
        for (const item of data.items){
            
            playlistItemsContainer.insertAdjacentHTML(
                "beforeend",
                playlistTrackItemHtml(
                    item.track.name,
                    item.track.album.images[0].url,
                    item.track.artists.map(artist => artist.name).join(", "),
                    item.track.id,
                    item.track.uri,
                    (parseInt(offset) + data.items.indexOf(item)),
                )
            );
        }
        // Se le agregan los eventos a los nuevos items
        setTrackIemsEventListeners()
        setTrackCardsEventListeners()

        // Si no hay mas items se esconde el boton de cargar mas
        if (nextItemsUrl){
            loadMoreBtn.classList.remove("d-none");
        }
    })
    .catch(error => {
        loadSpinner.classList.add("d-none");
        console.error(error);
    });
})