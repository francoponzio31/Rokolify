const userSettingsSwitchs = document.querySelectorAll(".user-setting-switch");
const reAddSongMinutesInput = document.getElementById("re-add-song-minutes-input");
const reAddSongMinutesBtn = document.getElementById("re-add-song-minutes-save-btn");
const cooldownSecondsInput = document.getElementById("cooldown-seconds-input");
const cooldownSecondsBtn = document.getElementById("cooldown-seconds-save-btn");

const playlistAccesSwitch = document.getElementById("owner-playlists-access-switch");
const playlistSettingsBtn = document.getElementById("owner-playlists-settings-btn");


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

// Switchs:
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


// Input de tiempo para volver a agregar misma canción:
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


// Input de tiempo para que un invitado pueda volver a agregar una canción:
cooldownSecondsInput.addEventListener("input", () => {
    cooldownSecondsBtn.disabled = false;

})

cooldownSecondsBtn.addEventListener("click", () => {
    cooldownSecondsBtn.disabled = true;
    fetch("/owner/api/guest_permissions", {
        method:"PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({"permission": "cooldown_time_to_add", "value": parseInt(cooldownSecondsInput.value)})
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
