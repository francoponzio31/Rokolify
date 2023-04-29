let playlistSettingsPage = 1;

const playlistItemsContainer = document.getElementById("playlist-settings-items-container");
const playlistSettingsSpinner = document.getElementById("playlist-settings-load-spinner");
const paginationBtns = document.querySelectorAll(".playlist-pagination-btn");
const previousBtn = document.getElementById("playlist-settings-previous-page-btn");
const nextBtn = document.getElementById("playlist-settings-next-page-btn");

paginationBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        if (!btn.classList.contains("active") && !btn.classList.contains("disabled")){

            // Actualización del valor de la pagina actual:
            const btnPaginationValue = btn.getAttribute("data-pagination-value");

            if (btnPaginationValue === "previous"){
                playlistSettingsPage--;
            }
            else if (btnPaginationValue === "next"){
                playlistSettingsPage++;
            }
            else{
                playlistSettingsPage = parseInt(btnPaginationValue);
            }

            // Actualización del paginado:
            if (playlistSettingsPage === 1){
                previousBtn.classList.add("disabled");
                nextBtn.classList.remove("disabled");
            }
            else if (playlistSettingsPage === parseInt(paginationBtns[paginationBtns.length - 2].getAttribute("data-pagination-value"))){
                nextBtn.classList.add("disabled");
                previousBtn.classList.remove("disabled");
            }
            else{
                previousBtn.classList.remove("disabled");
                nextBtn.classList.remove("disabled");
            }
            const activeBtn = Array.prototype.filter.call(paginationBtns, btn => parseInt(btn.getAttribute("data-pagination-value")) === playlistSettingsPage)[0];
            if (activeBtn){
                activeBtn.classList.add("active");
                const inactiveBtns = Array.prototype.filter.call(paginationBtns, btn => parseInt(btn.getAttribute("data-pagination-value")) !== playlistSettingsPage && btn.getAttribute("data-pagination-rol") !== "nav");
                inactiveBtns.forEach(btn => btn.classList.remove("active"));
            }

            // Actualización de playlists:
            playlistItemsContainer.classList.add("d-none");
            playlistSettingsSpinner.classList.remove("d-none");

            const offset = playlistsAmountToShow * (playlistSettingsPage - 1)
            fetch(`/owner/api/get_playlists/${offset}/${playlistsAmountToShow}`)
            .then(response => {
                if (!response.ok){
                    throw new Error(`Error: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {

                playlistItemsContainer.innerHTML = "";
                
                data.playlists.items.forEach(playlist => {
                    playlistItemsContainer.insertAdjacentHTML(
                        "beforeend",
                        PlaylistSettingCardHtml(
                            playlist.uri,
                            playlist.id,
                            playlist.name,
                            playlist.images[0].url,
                        )
                    );
                });
                
                console.log(playlistSettingsToConfirm)
                let playlistAllowedSwitches = document.querySelectorAll(".allow-playlist-switch");
                initializeAllowSwitches(playlistAllowedSwitches, playlistSettingsToConfirm);

                playlistItemsContainer.classList.remove("d-none");
                playlistSettingsSpinner.classList.add("d-none")
            })
            .catch(error => {
                playlistSettingsSpinner.classList.add("d-none")
                console.error(error);
            })
        }
    })
})


function PlaylistSettingCardHtml(playlistUri, playlistId, playlistName, playlistImageUrl){
     
    const html = `
        <div class="playlist-setting-card card mx-1" data-playlist-uri="${playlistUri}">
            <div class="card-header d-flex align-items-center">
                <img src="${playlistImageUrl}" class="img-thumbnail img-thumbnail-playlist playlist-image object-fit-cover me-3" style="width: 55px; height: 55px;" alt="playlist-image">
                <h2 class="fs-4 card-title my-0">${playlistName}</h2>
            </div>
            <div class="card-body d-flex align-items-center justify-content-around">
                <div class="form-check form-switch">
                    <input class="form-check-input allow-playlist-switch" type="checkbox" role="button" id="${playlistId}">
                    <label class="form-check-label" for="${playlistId}">Habilitar</label>
                </div>
                <!-- <button type="button" id="playlist-settings-btn" class="btn btn-sm btn-secondary" data-bs-target="#playlist-conditions-settings" data-bs-toggle="modal">Más opciones</button> -->
            </div>
        </div>
    `;

    return html;    
}