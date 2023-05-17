const copyUrlBtn = document.getElementById("copy-url-btn");
const copyUrlToast = document.getElementById("copy-url-toast");

copyUrlBtn.addEventListener("click", ()=>{
    const guestLinkElement = document.getElementById("guest-url-link");
    navigator.clipboard.writeText(guestLinkElement.href);
    
    const toastBody = copyUrlToast.querySelector(".toast-body");
    toastBody.innerText = "URL copiada en el portapapeles";
    
    const toast = new bootstrap.Toast(copyUrlToast);
    toast.show();
})
