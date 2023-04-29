const loadMoreBtn = document.getElementById("load-more-playlists");
const playlistsContainer = document.getElementById("playlists-container");
const loadSpinner = document.getElementById("load-more-playlists-spinner");


const tackItemHtml = (playlistName, playlistImageURL, playlistId) => {
    return `
    <div class="col">
        <div class="playlist-card card d-flex flex-row align-items-center pe-2 gap-3 bg-dark-subtle border-dark-subtle" style="--bs-bg-opacity: .9; cursor: pointer;" data-playlist-id="${playlistId}">
            <div>
                <img src="${playlistImageURL}" class="item-image rounded-start object-fit-cover" style="max-width: 80px; max-height:80px; width:80px; height:auto;" alt="item-image">
            </div>
            <div class="w-100 text-truncate">
                <h5 class="card-title fs-5 fw-bold text-truncate">${playlistName}</h5>
            </div>                        
        </div>
    </div>`
}

loadMoreBtn.addEventListener("click", ()=>{

    loadSpinner.classList.remove("d-none");
    loadMoreBtn.classList.add("d-none");

    nextPlaylistsUrl = new URL(nextPlaylistsUrl);
    console.log(nextPlaylistsUrl)

    // Se extraen los parametros de la url:
    const offset = nextPlaylistsUrl.searchParams.get("offset");
    const limit = nextPlaylistsUrl.searchParams.get("limit");

    fetch(`/guest/api/get_playlists/${offset}/${limit}`)
    .then(response => {
        if (!response.ok){
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        
        loadSpinner.classList.add("d-none");

        nextPlaylistsUrl = data.next;

        // Renderizado de playlists:
        for (const playlist of data.playlists){
            
            playlistsContainer.insertAdjacentHTML(
                "beforeend",
                tackItemHtml(
                    playlist.name,
                    playlist.images[0].url,
                    playlist.id
                )
            );
        }
        // Se le agregan los eventos a los nuevas playlists
        setPlaylistsCardsEventListeners()

        // Si no hay mas playlists se esconde el boton de cargar mas
        if (nextPlaylistsUrl){
            loadMoreBtn.classList.remove("d-none");
        }
    })
    .catch(error => {
        loadSpinner.classList.add("d-none");
        console.error(error);
    });
})