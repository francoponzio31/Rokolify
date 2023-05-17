const userSettingsSwitchs = document.querySelectorAll(".user-setting-switch");
const reAddSongMinutesInput = document.getElementById("re-add-song-minutes-input");
const reAddSongMinutesBtn = document.getElementById("re-add-song-minutes-save-btn");

const playlistAccesSwitch = document.getElementById("owner-playlists-access-switch");
const playlistSettingsBtn = document.getElementById("owner-playlists-settings-btn");
const playlistSettingCards = document.querySelectorAll(".playlist-setting-card");
const playlistSettingSaveBtn = document.getElementById("playlist-settings-save-btn");
const playlistSettingDiscardBtn = document.getElementById("playlist-settings-discard-btn");


//? --------------------------------- Deshabilitar el botón de configuración de playlists:

function checkPlaylistAccesSwitch(playlistAccesSwitch, playlistSettingsBtn){
    if (playlistAccesSwitch.checked){
        playlistSettingsBtn.disabled = false;
    }
    else{
        playlistSettingsBtn.disabled = true;
    }
}


checkPlaylistAccesSwitch(playlistAccesSwitch, playlistSettingsBtn);

playlistAccesSwitch.addEventListener("change", ()=>{
    checkPlaylistAccesSwitch(playlistAccesSwitch, playlistSettingsBtn);
});



//? --------------------------------- Actualización de la configuración del usuario:

userSettingsSwitchs.forEach(settingSwitch => {
    settingSwitch.addEventListener("change", () => {

        fetch("/owner/api/guest_permissions", {
            method:"PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({"permission": settingSwitch.name, "value": settingSwitch.checked})
        })
        .then(response => {
            if (!response.ok){
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json()
        })
        .then(data => {
            console.log(data)
        })
        .catch(error => console.error(error))
    })

});

reAddSongMinutesInput.addEventListener("input", () => {
    reAddSongMinutesBtn.disabled = false;

})

reAddSongMinutesBtn.addEventListener("click", () => {
    reAddSongMinutesBtn.disabled = true;
    fetch("/owner/api/guest_permissions", {
        method:"PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({"permission": "time_to_re_add_same_track", "value": parseInt(reAddSongMinutesInput.value)})
    })
    .then(response => {
        if (!response.ok){
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json()
    })
    .then(data => {
        console.log(data)
    })
    .catch(error => console.error(error))
})

//? --------------------------------- Eventos de configuración de playlists:

let playlistSettingsToConfirm = {};


function initializeAllowSwitches(playlistAllowedSwitches, playlistSettingsToConfirm){

    playlistAllowedSwitches.forEach((allowSwitch)=>{
        
        let playlistId = allowSwitch.id;
        
        // Precarga:
        if (playlistSettingsToConfirm[playlistId]?.allowed !== undefined){
            allowSwitch.checked = Boolean(playlistSettingsToConfirm[playlistId].allowed);
        }
        else if (playlistSettings[playlistId]?.allowed !== undefined){
            allowSwitch.checked = Boolean(playlistSettings[playlistId].allowed);
        }
        else{
            allowSwitch.checked = true;
        }

        // Eventos
        if (!allowSwitch.hasEventListener){
            allowSwitch.addEventListener("change", ()=>{
                if (!(playlistId in playlistSettingsToConfirm)){
                    playlistSettingsToConfirm[playlistId] = {}
                }
                playlistSettingsToConfirm[playlistId].allowed = allowSwitch.checked;
            })
            allowSwitch.hasEventListener = true;
        }
    })
}


playlistSettingsBtn.addEventListener("click", ()=> {
    let playlistAllowedSwitches = document.querySelectorAll(".allow-playlist-switch");
    initializeAllowSwitches(playlistAllowedSwitches, playlistSettingsToConfirm);
});


// Actualización de la configuración las playlists:
playlistSettingSaveBtn.addEventListener("click", ()=> {    
    // Post de datos:    
    fetch("/owner/api/playlists_settings", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(playlistSettingsToConfirm)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            playlistSettings = data;
        })
        .catch(error => {
            console.error("Error: ", error);
        })

    // Vaciado de el objeto auxiliar playlistSettingsToConfirm:
    Object.keys(playlistSettingsToConfirm).forEach(key => delete playlistSettingsToConfirm[key]);
});

playlistSettingDiscardBtn.addEventListener("click", ()=>{
    // Vaciado de el objeto auxiliar playlistSettingsToConfirm:
    Object.keys(playlistSettingsToConfirm).forEach(key => delete playlistSettingsToConfirm[key]);
});
