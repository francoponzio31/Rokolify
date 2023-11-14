let playlistSettingsPage = 1;

const addAllowConditionBtn = document.getElementById("add-allow-playlist-condition-btn");
const playlistItemsContainer = document.getElementById("playlist-settings-items-container");
const playlistSettingsSpinner = document.getElementById("playlist-settings-load-spinner");
const paginationBtns = document.querySelectorAll(".playlist-pagination-btn");
const previousBtn = document.getElementById("playlist-settings-previous-page-btn");
const nextBtn = document.getElementById("playlist-settings-next-page-btn");


// Seteo de valor de switches al abrir el modal de configuración de playlists:
playlistSettingsBtn.addEventListener("click", async () => {

    // Se muestra el spinner
    playlistItemsContainer.classList.add("d-none");
    playlistSettingsSpinner.classList.remove("d-none");

    let playlistSettings = await getPlaylistSettings();
    
    let playlistAllowedSwitches = document.querySelectorAll(".allow-playlist-switch");
    
    initializeAllowSwitches(playlistSettings, playlistAllowedSwitches);
    // Seteo de eventos para los switches:
    setAllowPlaylistSwitchesEvents();
    
    // Seteo de eventos para los botones de Condiciones:
    setPlaylistConditionsBtnsEvents();

    // Se ocults el spinner
    playlistItemsContainer.classList.remove("d-none");
    playlistSettingsSpinner.classList.add("d-none")

})


// Función para setear eventos a los switch para habilitar playlists:
function setAllowPlaylistSwitchesEvents(){
    let playlistAllowedSwitches = document.querySelectorAll(".allow-playlist-switch");
    playlistAllowedSwitches.forEach((allowSwitch) => {        
        allowSwitch.addEventListener("change", () => {
            let playlistId = allowSwitch.getAttribute("data-playlist-id");
            setPlaylistAllowValue(playlistId, allowSwitch.checked);
        })

    })
}


// Eventos en botones de paginado:
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

                playlistItemsContainer.innerHTML = `
                <a href='https://open.spotify.com' target='_blank'>
                    <img src='/static/img/spotify_logo.png' class="mb-2 ms-2 align-self-start" style='height: 30px'>
                </a>
                `;
                
                data.playlists.items.forEach(playlist => {
                    playlistItemsContainer.insertAdjacentHTML(
                        "beforeend",
                        playlistSettingCardHtml(
                            playlist.uri,
                            playlist.id,
                            playlist.name,
                            playlist.images[0].url,
                        )
                    );
                });
                
                // Seteo de eventos para los switches:
                setAllowPlaylistSwitchesEvents();

                return getPlaylistSettings();
            })
            .then(playlistSettings => {
                let playlistAllowedSwitches = document.querySelectorAll(".allow-playlist-switch");
                initializeAllowSwitches(playlistSettings, playlistAllowedSwitches);
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


// Modelo html de card de configuración de playlist
function playlistSettingCardHtml(playlistUri, playlistId, playlistName, playlistImageUrl){
     
    const html = `
        <div class="playlist-setting-card card mx-1" style="min-height: 55px;" data-playlist-uri="${playlistUri}">
            <div class="card-header d-flex align-items-center">
                <img src="${playlistImageUrl}" class="img-thumbnail img-thumbnail-playlist playlist-image object-fit-cover me-3" style="width: 55px; height: 55px;" alt="playlist-image">
                <h2 class="fs-4 card-title my-0">${playlistName}</h2>
            </div>
            <div class="card-body d-flex align-items-center justify-content-around">
                <div class="form-check form-switch">
                    <input class="form-check-input allow-playlist-switch" type="checkbox" role="button" data-playlist-id="${playlistId}">
                    <label class="form-check-label" for="${playlistId}">Enable</label>
                </div>
                <button type="button" data-playlist-id="${playlistId}" class="playlist-allow-conditions-btn btn btn-sm btn-secondary" data-bs-target="#playlist-conditions-settings" data-bs-toggle="modal">Conditions</button>
            </div>
        </div>
    `;

    return html;    
}


// Función para hacer una petición para obtener la configuración de playlists
function getPlaylistSettings(){
    return fetch("/owner/api/playlists_settings")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error("Error: ", error);
            throw error;
        })
}


// Función para precargar los switches de habilitación de playlists:
function initializeAllowSwitches(playlistSettings, playlistAllowedSwitches){

    playlistAllowedSwitches.forEach((allowSwitch)=>{
        let playlistId = allowSwitch.getAttribute("data-playlist-id");
        if (playlistSettings[playlistId]?.allowed !== undefined){
            allowSwitch.checked = Boolean(playlistSettings[playlistId].allowed);
        }
        else{
            allowSwitch.checked = true;
        }
    })
}


// Se agrega evento al botón para agregar nuevas condiciones para habilitar playlist:
addAllowConditionBtn.addEventListener("click", async () => {

    let playlistId =  addAllowConditionBtn.getAttribute("data-playlist-id");

    // Elemento con mensaje de validación:
    const validationMessage = document.getElementById("allow-condition-validation-message");

    // Obtener los valores de los inputs
    const day = document.getElementById("allow-playlist-day-input").value;
    const initTime = document.getElementById("allow-playlist-init-time-input").value;
    const endTime = document.getElementById("allow-playlist-end-time-input").value;
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    if (timeInputValuesAreValid(initTime, endTime) && playlistId){

        validationMessage.classList.add("d-none");

        // Se deshabilita el botón de agregar
        addAllowConditionBtn.disabled = true;


        // Agrego la nueva condicion
        let newCondition = {
            "day": day,
            "init_time": initTime,
            "end_time": endTime,
            "timezone": userTimezone
        }

        // Se agrega nueva condición
        await addPlaylistAllowCondition(playlistId, newCondition);
        // Se obtienen las condiciones de habilitación de la playlist
        let updatedPlaylistAllowedConditions = await getPlaylistAllowConditions(playlistId);
        
        // Se renderizan nuevamente las condiciones
        renderPlaylistSettings(playlistId, updatedPlaylistAllowedConditions);

        // Se habilita el botón de agregar
        addAllowConditionBtn.disabled = false;

    }
    else{
        validationMessage.classList.remove("d-none");
    }
    
})


// Seteo de eventos para botones de "Condiciones" de habilitación de playlists:
function setPlaylistConditionsBtnsEvents(){
    let playlistConditionsBtn = document.querySelectorAll(".playlist-allow-conditions-btn");
    playlistConditionsBtn.forEach((btn) => {        
        btn.addEventListener("click", async () => {

            let playlistId = btn.getAttribute("data-playlist-id");
            // Se guarda el dato del id de la playlist en el botón para agregar nuevas condiciones
            addAllowConditionBtn.setAttribute("data-playlist-id", playlistId);

            let playlistAllowedConditions = await getPlaylistAllowConditions(playlistId);            

            renderPlaylistSettings(playlistId, playlistAllowedConditions);

            // Se oculta el elemento con el mensaje de validación
            const validationMessage = document.getElementById("allow-condition-validation-message");
            validationMessage.classList.add("d-none");
        })
    })
}


// Se renderizan las opciones de habilitación de playlists en la grilla
function renderPlaylistSettings(playlistId, playlistAllowedConditions){

    const emptyGridMessage = document.getElementById("allow-conditions-grid-empty-message");
    const conditionsGridBody = document.getElementById("allow-playlist-conditions-grid");
    conditionsGridBody.innerHTML = "";

    if (playlistAllowedConditions.length > 0){
        
        emptyGridMessage.classList.add("d-none")

        const dayNameMap = {
            "-1": "All",
            "0": "Monday",
            "1": "Tuesday",
            "2": "Wednesday",
            "3": "Thursday",
            "4": "Friday",
            "5": "Saturday",
            "6": "Sunday"
        }

        playlistAllowedConditions.forEach((condition) => {
            // Crear una nueva fila en la tabla con los valores ingresados y el botón de eliminar
            const newRow =
            `<tr>
                <td class="align-middle">${dayNameMap[condition.day]}</td>
                <td class="align-middle">${condition.init_time}</td>
                <td class="align-middle">${condition.end_time}</td>
                <td>
                    <button data-condition-id=${condition.id} class="btn btn-danger rounded-3 playlist-condition-delete-btn" style="padding: .1rem .2rem">
                        <img src="/static/img/trash.svg">
                    </button>
                </td>
            </tr>`;
            
            // Agregar la nueva fila al cuerpo de la tabla
            conditionsGridBody.insertAdjacentHTML("beforeend", newRow);
            
            // Asignar la funcionalidad de eliminación a los nuevos botones
            const deleteBtns = document.querySelectorAll(".playlist-condition-delete-btn");
            deleteBtns.forEach(function(btn) {

                if (!btn.deleteConditionEvent){
                    btn.addEventListener("click", async () => {
                        
                        btn.disabled = true;
                        
                        let conditionId = btn.getAttribute("data-condition-id");
                        await deletePlaylistAllowCondition(playlistId, conditionId);
                        // Vuelvo a pedir las condiciones
                        let updatedPlaylistAllowedConditions = await getPlaylistAllowConditions(playlistId);

                        renderPlaylistSettings(playlistId, updatedPlaylistAllowedConditions);

                    });
                    btn.deleteConditionEvent = true;
                }   

            });
        })
    }
    else {
        emptyGridMessage.classList.remove("d-none");
    }

}


// Obtención de condiciones de habilitación de playlist
async function getPlaylistAllowConditions(playlistId){
    let playlistsSettings = await getPlaylistSettings();
    let playlistAllowedConditions = playlistsSettings[playlistId]?.conditions || [];

    return playlistAllowedConditions
}


// Request para setear habilitar/deshabilitar una playlist
async function setPlaylistAllowValue(playlistId, switchValue){
    fetch(`/owner/api/set_allow_playlist_value/${playlistId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({allow_value: switchValue})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error("Error: ", error);
    })
}


// Request para agregar condición de habilitacipon para una playlist
async function addPlaylistAllowCondition(playlistId, newCondition){
    return fetch(`/owner/api/add_playlist_condition/${playlistId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({new_permision: newCondition})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error("Error: ", error);
    })
}


// Request para eliminar una condición de habilitacipon para una playlist
async function deletePlaylistAllowCondition(playlistId, conditionId){
    return fetch(`/owner/api/delete_playlist_condition/${playlistId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({condition_id: conditionId})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error("Error: ", error);
    })
}


// Validación de los valores de los inputs de horarios
function timeInputValuesAreValid(initTimeValue, endTimeValue){
    // Crear objetos Date para realizar la comparación
    const initDate = new Date(`2000-01-01T${initTimeValue}`);
    const endDate = new Date(`2000-01-01T${endTimeValue}`);

    return (initDate < endDate)
}