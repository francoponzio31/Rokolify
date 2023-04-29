const queueModalTrigger = document.getElementById("queue-modal-trigger");
const queueItemsContainer = document.getElementById("queue-items-container");
const queueLoadSpinner = document.getElementById("queue-load-spinner");


queueModalTrigger.addEventListener("click", ()=>{

    queueItemsContainer.innerHTML = "";
    queueLoadSpinner.classList.remove("d-none");
    
    fetch("/guest/api/queue")
    .then(response => {
        if (!response.ok){
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    })
    .then(data => {

        queueLoadSpinner.classList.add("d-none");

        queue = data;
    
        queueItemsContainer.innerHTML = "";
        if (queue.currently_playing || queue.queue > 0){
            
            const currentPlayingItem = generateQueueListItem(
                queue.currently_playing.uri,
                queue.currently_playing.id,
                queue.currently_playing.name,
                queue.currently_playing.album.images[0].url,
                queue.currently_playing.artists.map(artist => artist.name).join(", "),
                currently_playing=true
            );
            queueItemsContainer.insertAdjacentHTML("beforeend", currentPlayingItem);

            const queueTacks = queue.queue;
            queueTacks.forEach(track => {
                const queueItem = generateQueueListItem(
                    track.uri,
                    track.id,
                    track.name,
                    track.album.images[0].url,
                    track.artists.map(artist => artist.name).join(", "),
                );
                queueItemsContainer.insertAdjacentHTML("beforeend", queueItem);
            });

            // Eventos:
            setTrackCardsEventListeners()

        }

        else{
            queueItemsContainer.innerHTML = "No se encontró ningún reproductor activo"
        }
    })
    .catch(error => {
        queueLoadSpinner.classList.add("d-none");
        console.error(error);
    });

})


function generateQueueListItem(trackURI, trackId, trackName, trackImageURL, artist, currently_playing=false){

    const queueItem = `
    <div class="track-card card d-flex flex-row align-items-center pe-2 gap-3 bg-dark-subtle border-dark-subtle-subtle" data-item-uri="${trackURI}" data-item-id="${trackId}" data-bs-toggle="modal" data-bs-target="#track-modal">
        ${
            trackImageURL
            ? `<img src="${trackImageURL}" class="item-image rounded-start" style="width:60px; max-height:60px;" alt="item-image">`
            : ""
        }   
        <div class="w-100 justify-content-between text-truncate">
            <h5 class="card-title fs-6 fw-bold text-truncate mb-0">${trackName}</h5>
            <small>${artist}</small>
        </div>
        
        ${
            currently_playing
            ? `<img src="${playIconPath}" alt="play-icon"></img>`
            : ""
        }   
    </div>
    `

    return queueItem
}
