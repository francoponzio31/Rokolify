const searchBtn = document.getElementById("search-input-btn");
const searchInput = document.getElementById("search-input");
const searchResultContainer = document.getElementById("search-result-container");
const emptySearchContainer = document.getElementById("empty-search-container");
const searchSpinner = document.getElementById("search-load-spinner");


searchBtn.addEventListener("click", (event)=>{
    
    event.preventDefault()
    emptySearchContainer.classList.add("d-none");
    searchResultContainer.innerHTML = "";

    if (searchInput.value){

        searchSpinner.classList.remove("d-none");
        
        fetch(`/guest/api/search_in_catalog/${searchInput.value}`)
        .then(response => {
            if (!response.ok){
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {

            searchSpinner.classList.add("d-none");

            const tracks = data.items;

            searchResultContainer.innerHTML = "";
            tracks.forEach(track => {
                searchResultContainer.insertAdjacentHTML("beforeend", generateTrackItem(
                    track.id,
                    track.uri,
                    track.name,
                    track.artists.map(artist => artist.name).join(", "),
                    track.album.images[0].url,
                    ));
                });
    
                setTrackIemsEventListeners()
                setTrackCardsEventListeners()

        })
        .catch(error => {
            searchSpinner.classList.add("d-none");
            console.error(error);
        });

    }
    else{
        emptySearchContainer.classList.remove("d-none");
    }
})

function generateTrackItem(trackId, trackURI, trackName, artist, trackImageURL){

    const item = `
    <div class="track-card  card d-flex flex-row align-items-center pe-2 gap-3 bg-dark-subtle border-dark-subtle" data-item-id="${trackId}" data-item-uri="${trackURI}">
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
    </div>
    `

    return item
}
