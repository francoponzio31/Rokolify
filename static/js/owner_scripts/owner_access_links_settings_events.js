const createAccessLinkBtn = document.getElementById("create-access-link-btn");
const addAccessLinkBtn = document.getElementById("add-access-link-btn");
const AccessLinksGridBody = document.getElementById("access-links-grid");
const AccessLinksGridSpinner = document.getElementById("access-links-grid-load-spinner");
const accessLinkDescriptionInput = document.getElementById("access-link-description-input");
const accessLinkDatetimeInput = document.getElementById("access-link-datetime-input");
const accessLinkConfirmDeleteBtn = document.getElementById("access-link-confirm-delete-btn");
const emptyGridMessage = document.getElementById("access-links-grid-empty-message");
const accessLinkValidationMessage = document.getElementById("access-link-validation-message");
const addLinkBsModal = new bootstrap.Modal('#addLinkModal')


// Se renderizan por primera vez los links
document.addEventListener("DOMContentLoaded", async () => {
    // Se obtienen los links de acceso
    const accessLinks = await getGuestAccessLinks();
    renderAccessLinks(accessLinks);
});


// Se agrega evento al botón para agregar nuevos links de acceso:
addAccessLinkBtn.addEventListener("click", async () => {

    // Obtener los valores de los inputs
    const description = accessLinkDescriptionInput.value.trim();
    const expirationDatetime = accessLinkDatetimeInput.value;
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Validaciones
    if (!description){
        accessLinkValidationMessage.innerText = "Description is required"
        accessLinkValidationMessage.classList.remove("d-none")
        return
    }

    if (expirationDatetime && new Date(expirationDatetime) < new Date()){
        accessLinkValidationMessage.innerText = "The expiration date must be after the current date"
        accessLinkValidationMessage.classList.remove("d-none")
        return
    }
    
    addLinkBsModal.hide()

    // Agrego la nueva condicion
    let newAccessLink = {
        "description": description,
        "expiration_datetime": expirationDatetime,
        "timezone": userTimezone
    }

    // Se agrega nuevo link de acceso para invitados
    await addGuestAccessLink(newAccessLink);

    // Se obtienen los links de acceso
    let updatedAccessLinks = await getGuestAccessLinks();
    

    // Se renderizan nuevamente los links
    renderAccessLinks(updatedAccessLinks);
})


// Evento para boton que abre el modal para crear nuevos links de acceso:
createAccessLinkBtn.addEventListener("click", () => {

    // Se resetean los inputs
    accessLinkDescriptionInput.value = null;
    accessLinkDatetimeInput.value = null;
    accessLinkValidationMessage.classList.add("d-none")
    
    // Establecer el valor mínimo del input de fecha y hora de vencimiento
    const currentDatetime = luxon.DateTime.now();
    const formattedDatetime = currentDatetime.toFormat("yyyy-MM-dd'T'HH:mm");
    accessLinkDatetimeInput.setAttribute("min", formattedDatetime);
})


// Se renderizan los links de acceso en la grilla
function renderAccessLinks(accessLinks){

    AccessLinksGridBody.innerHTML = "";

    if (accessLinks.length > 0){
        const baseUrl = window.location.origin;
        
        accessLinks.forEach((link) => {

            const accessLinkUrl = `${baseUrl}/guest/gateway/${link.token}`;
            const accessLinkQrUrl = `${baseUrl}/owner/get_access_link_qr/${link.token}`;
            
            // Crear una nueva fila en la tabla con los valores ingresados y el botón de eliminar
            const newRow =
            `<tr>
                <td class="align-middle">${link.description}</td>
                <td class="align-middle">
                    <a id="guest-url-link" href="/guest/gateway/${link.token}" target="_blank" class="text-decoration-none text-primary-emphasis">Enter</a>
                </td>
                <td class="align-middle">${link.created_on}</td>
                <td class="align-middle">${link.expiration_datetime || "Never"}</td>
                <td class="grid gap-3 col-1 col-md-3">
                    <button type="button" class="access-link-copy-url-btn btn btn-sm btn-primary rounded-3" style="padding: .18rem .32rem" data-access-link-url="${accessLinkUrl}">
                        <img src="/static/img/bxs-copy.svg">
                    </button>
                    <button type="button" class="access-link-qr-btn btn btn-sm btn-primary rounded-3" style="padding: .18rem .32rem; margin: .2rem 0" data-bs-toggle="modal" data-bs-target="#qrModal" data-access-link-qr-url="${accessLinkQrUrl}">
                        <img src="/static/img/qr-code.svg">
                    </button>
                    <button type="button" class="access-link-delete-btn btn btn-sm btn-danger rounded-3" style="padding: .18rem .32rem" data-bs-toggle="modal" data-bs-target="#deleteLinkModal" data-access-link-id="${link.id}">
                        <img src="/static/img/trash.svg">
                    </button>
                </td>
            </tr>`;
            
            // Agregar la nueva fila al cuerpo de la tabla
            AccessLinksGridBody.insertAdjacentHTML("beforeend", newRow);
        })

        // Asignar la funcionalidad de eliminación a los botones de eliminar:
        const deleteBtns = document.querySelectorAll(".access-link-delete-btn");
        deleteBtns.forEach((btn) => {

            if (!btn.deleteConditionEvent){
                btn.addEventListener("click", () => {
                    const accesslinkId = btn.getAttribute("data-access-link-id");
                    accessLinkConfirmDeleteBtn.setAttribute("data-access-link-id", accesslinkId);
                });
                btn.deleteConditionEvent = true;
            }   

        });

        // Asignar la funcionalidad de eliminación a los botones para copiar el link de acceso:
        const copyUrlBtns = document.querySelectorAll(".access-link-copy-url-btn");
        copyUrlBtns.forEach((btn) => {

            if (!btn.copyLinkConditionEvent){
                btn.addEventListener("click", () => {
                    
                    const url = btn.getAttribute("data-access-link-url");
                    navigator.clipboard.writeText(url);

                    const copyUrlToast = document.getElementById("copy-url-toast");
                    const toastBody = copyUrlToast.querySelector(".toast-body");
                    toastBody.innerText = "Link URL copied to clipboard";
                    
                    const toast = new bootstrap.Toast(copyUrlToast);
                    toast.show();

                });
                btn.copyLinkConditionEvent = true;
            }   

        });

        // Asignar la funcionalidad de eliminación a los botones para generar el qr:
        const qrBtns = document.querySelectorAll(".access-link-qr-btn");
        qrBtns.forEach((btn) => {

            if (!btn.qrConditionEvent){
                btn.addEventListener("click", () => {
                    const qrLoadSpinner = document.getElementById("qr-modal-load-spinner");
                    const qrImg = document.getElementById("access-link-qr-img");
                    qrImg.classList.add("d-none")
                    qrLoadSpinner.classList.remove("d-none")

                    const accessLinkQrUrl = btn.getAttribute("data-access-link-qr-url");
                    
                    const qrDownloadLink = document.getElementById("access-link-qr-download-link");

                    qrImg.setAttribute("src", accessLinkQrUrl);
                    qrDownloadLink.setAttribute("href", accessLinkQrUrl);

                    qrLoadSpinner.classList.add("d-none")
                    qrImg.classList.remove("d-none")

                });
                btn.qrConditionEvent = true;
            }   

        });
    }
    else {
        emptyGridMessage.classList.remove("d-none");
    }

    AccessLinksGridSpinner.classList.add("d-none");
    AccessLinksGridBody.classList.remove("d-none");
}


// Evento para borrar un link de acceso
accessLinkConfirmDeleteBtn.addEventListener("click", async () => {
    const accessLinkId = accessLinkConfirmDeleteBtn.getAttribute("data-access-link-id");

    await deleteGuestAccessLink(accessLinkId);

    // Se obtienen los links de acceso
    let updatedAccessLinks = await getGuestAccessLinks();

    // Se renderizan nuevamente los links
    renderAccessLinks(updatedAccessLinks);
})


// Obtención de links de acceso
async function getGuestAccessLinks(){

    emptyGridMessage.classList.add("d-none")
    AccessLinksGridSpinner.classList.remove("d-none");
    AccessLinksGridBody.classList.add("d-none");
    
    return fetch("/owner/api/guest_access_links")
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


// Request para agregar link de acceso para invitados
async function addGuestAccessLink(newAccessLink){
    return fetch(`/owner/api/guest_access_links`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({new_access_link: newAccessLink})
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
async function deleteGuestAccessLink(accessLinkId){
    return fetch(`/owner/api/guest_access_links`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({access_link_id: accessLinkId})
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
