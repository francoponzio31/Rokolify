setTrackIemsEventListeners()

function setTrackIemsEventListeners(){

    const addToQueueBtns = document.querySelectorAll(".add-to-queue-btn")
    const addToQueueToast = document.getElementById("add-to-queue-toast")

    function addTrackToQueue(trackURI, playlistTrackIndex){

        fetch("/guest/api/queue", {
            method:"POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({"track_uri": trackURI, "playlist_track_index": playlistTrackIndex})
        })
        .then(response => {
            if (!response.ok){
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {   
            const toastBody = addToQueueToast.querySelector(".toast-body");
            toastBody.innerText = data.message;
            const toast = new bootstrap.Toast(addToQueueToast);
            toast.show();

            if (!data.success){
                console.log(data);
            }
        })
        .catch(error => {
            console.error(error);
        })
    }
    
    addToQueueBtns.forEach(btn => {

        if (!btn.hasAddToQueueEvent){
            btn.addEventListener("click", () => {
                const btnCardContainer = btn.parentNode;
                const trackURI = btnCardContainer.getAttribute("data-item-uri");
                const playlistTrackIndex = btnCardContainer.getAttribute("data-playlist-track-index");
                addTrackToQueue(trackURI, playlistTrackIndex);
            });
            btn.hasAddToQueueEvent = true;
        }        
    });

}


