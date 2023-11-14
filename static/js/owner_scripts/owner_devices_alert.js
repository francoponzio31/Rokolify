const alertContainer = document.getElementById("devices-alert-container")
linkedpotifyAccountValidation = linkedpotifyAccountValidation === "True";
devicesValidation = devicesValidation === "True";

if (linkedpotifyAccountValidation && !devicesValidation){
    
    const alertMessage = `
    <div class="alert alert-dark alert-dismissible" role="alert">
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        <p>No devices with an active Spotify session were found. Would you like to open Spotify on this device?</p>
        <button onclick="window.location.href='spotify:'" class="btn btn-secondary btn-sm" data-bs-dismiss="alert">Open Spotify</button>
    </div>
    `

    alertContainer.insertAdjacentHTML("beforeend", alertMessage)
    
}