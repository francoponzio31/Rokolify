setTrackCardsEventListeners()

function setTrackCardsEventListeners(){
    const trackCards = document.querySelectorAll(".track-card");

    trackCards.forEach(trackCard => {

        if (!trackCard.hasAddToQueueEvent){
            trackCard.addEventListener("click", (event) => {

                const trackId = trackCard.getAttribute("data-item-id");
                const trackModalTitle = document.getElementById("track-modal-title");
                const trackModalTitlePlaceholder = document.getElementById("track-modal-title-placeholder");
                const trackModalInfoContainer = document.getElementById("track-modal-info-container");
                const trackModalLoadSpinner = document.getElementById("track-modal-load-spinner");
                const trackModalBtn = trackCard.querySelector(".add-to-queue-btn");

                // Si se cliquea en algun lado que no sea el botón de agregar a la cola de reproducción:
                if (!(trackModalBtn && trackModalBtn.contains(event.target))){
                    trackModalTitle.classList.add("d-none");
                    trackModalInfoContainer.classList.add("d-none");
                    trackModalTitlePlaceholder.classList.remove("d-none");
                    trackModalLoadSpinner.classList.remove("d-none");

                    fetch(`/guest/api/track/${trackId}`)
                    .then(response => {
                        if (!response.ok){
                            throw new Error(`Error: ${response.status} ${response.statusText}`);
                        }
                
                        return response.json();
                    })
                    .then(data => {
                        
                        // console.log(data)
                        trackModalTitlePlaceholder.classList.add("d-none");
                        trackModalLoadSpinner.classList.add("d-none");
                        trackModalTitle.innerText = data.name;
                        trackModalTitle.classList.remove("d-none");
                        trackModalInfoContainer.innerHTML = "";

                        trackModalInfoContainer.insertAdjacentHTML("beforeend", getAlbumInfoHtml(data));
                        trackModalInfoContainer.insertAdjacentHTML("beforeend", "<hr>");
                        trackModalInfoContainer.insertAdjacentHTML("beforeend", getArtistsInfoHtml(data));
                        trackModalInfoContainer.insertAdjacentHTML("beforeend", "<hr>");
                        trackModalInfoContainer.insertAdjacentHTML("beforeend", getTrackInfoHtml(data));
                        if (data.preview_url){ addTrackSampleEvents() }; 
                        trackModalInfoContainer.classList.remove("d-none");
                    
                    })
                    .catch(error => {
                        trackModalLoadSpinner.classList.add("d-none");
                        console.error(error);
                    });
                }
            })
            trackCard.hasAddToQueueEvent = true;
        }

    }); 
}


function getAlbumInfoHtml(trackData){

    html = `
        <section class="album-info container">
            <h3 class="track-card-section-title fs-5">Álbum</h3>
            <div class="d-flex align-items-center">
                <img src="${trackData.album_img_url}" class="img-thumbnail-track track-image object-fit-cover me-3 rounded" style="width: 60px; height: 60px;" alt="track-image">
                <div>
                    <a href="${trackData.album_spotify_url}" target="_blank" class="track-card-link">${trackData.album_name}</a>
                    <p> <span class="fw-bold">Lanzamiento: </span>${trackData.album_release_date}</p>
                </div>
            </div>
        </section>`

    return html
}


function getArtistsInfoHtml(trackData){

    const artistHtml = artistData => `
        <div class="col d-flex align-items-center text-start">
            ${
                artistData.img_url
                ? `<img src='${artistData.img_url}' class='img-thumbnail-track track-image object-fit-cover me-3 rounded-circle' style='width: 55px; height: 55px;' alt='track-image'>`
                : `
                // default user img:
                <svg xmlns='http://www.w3.org/2000/svg' width='55' height='55' fill='currentColor' class='bi bi-person-circle me-3' viewBox='0 0 16 16'>
                        <path d='M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z'/>
                        <path fill-rule='evenodd' d='M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z'/>
                </svg>
                `
            }
            <p>
                <a href="${artistData.spotify_url}" target="_blank" class="track-card-link">${artistData.name}</a>
            </p>
        </div>
    `;
    
    html = `
        <section class="artists-info container">
            <h3 class="track-card-section-title fs-5">Artistas</h3>

            <div class="row row-cols-auto row-cols-lg-3 gap-2">
                ${trackData.artists.map(artistData => artistHtml(artistData)).join("")}
            </div>
        </section>`

    return html
}


function getTrackInfoHtml(trackData){

    html = `
        <section class="track-info container">
            <h3 class="track-card-section-title fs-5">Canción</h3>
            <div class="d-flex flex-column align-items-start gap-2">
                <a href="${trackData.spotify_url}" target="_blank" class="track-card-link">${trackData.name}</a>
                <div> <span class="fw-bold">Duración: </span>${trackData.duration}</div>
                ${
                    trackData.preview_url
                    ? `
                        <audio id="track-sample" hidden>
                            <source src="${trackData.preview_url}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                        
                        <div class="d-flex align-items-start">
                            <button id="track-sample-play-btn" class="btn btn-outline-secondary rounded-4 d-flex align-items-center mt-1">
                                <span class="fw-bold me-2"> Vista previa </span>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">
                                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
                                </svg>
                            </button>

                            <button id="track-sample-pause-btn" class="d-none btn btn-outline-secondary rounded-4 d-flex align-items-center mt-1">
                                <span class="fw-bold me-2"> Vista previa </span>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">
                                    <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"/>
                                </svg>
                            </button>
                        </div>
                    `
                    : ""
                }

            </div>
           
        </section>`

    return html
}

function addTrackSampleEvents(){

    const playSampleBtn = document.getElementById("track-sample-play-btn");
    const pauseSampleBtn = document.getElementById("track-sample-pause-btn");
    const trackSamplePlayer = document.getElementById("track-sample");

    playSampleBtn.addEventListener("click", () => {
        playSampleBtn.classList.add("d-none");
        pauseSampleBtn.classList.remove("d-none");
        trackSamplePlayer.play(); 
    })

    pauseSampleBtn.addEventListener("click", () => {
        pauseSampleBtn.classList.add("d-none");
        playSampleBtn.classList.remove("d-none");
        trackSamplePlayer.pause(); 
    })
}