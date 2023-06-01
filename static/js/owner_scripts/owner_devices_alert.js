const alertContainer = document.getElementById("devices-alert-container")
linkedpotifyAccountValidation = linkedpotifyAccountValidation === "True";
devicesValidation = devicesValidation === "True";

if (linkedpotifyAccountValidation && !devicesValidation){
    
    const alertMessage = `
    <div class="alert alert-dark alert-dismissible" role="alert">
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        <p>No se han encontrado dispositivos disponibles con una sesión de Spotify activa. ¿Desea abrir Spotify en este dispositivo?</p>
        <button onclick="window.location.href='spotify:'" class="btn btn-secondary btn-sm" data-bs-dismiss="alert">Abrir Spotify</button>
    </div>
    `

    alertContainer.insertAdjacentHTML("beforeend", alertMessage)
    
}