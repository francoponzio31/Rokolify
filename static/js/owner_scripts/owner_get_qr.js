const generateQrBtn = document.getElementById("qr-btn");

generateQrBtn.addEventListener("click", ()=>{
    window.location.href = `${getQrUrl}?guest_url=${guestUrl}`;
})