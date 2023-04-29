const copyUrlBtn = document.getElementById("copy-url-btn");
const copyUrlToast = document.getElementById("copy-url-toast");

copyUrlBtn.addEventListener("click", ()=>{
    const input = document.getElementById("guest-url-input");
    input.select();
    navigator.clipboard.writeText(input.value);
    
    const toastBody = copyUrlToast.querySelector(".toast-body");
    toastBody.innerText = "URL copiada en el portapapeles";
    
    const toast = new bootstrap.Toast(copyUrlToast);
    toast.show();
})
