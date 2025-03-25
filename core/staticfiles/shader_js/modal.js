function openModal() {
    const modal = document.getElementById("myModal");
    modal.style.display = "block";
    initThreeJS();
    animate();
}

function closeModal() {
    const modal = document.getElementById("myModal");
    modal.style.display = "none";
    if (renderer) {
        renderer.dispose();
        document.getElementById("threejs-container").innerHTML = "";
    }
}

document.getElementById("myModal").addEventListener('click', function(event) {
    const modalContent = document.querySelector('.modal-content');
    if (!modalContent.contains(event.target)) {
        closeModal();
    }
});