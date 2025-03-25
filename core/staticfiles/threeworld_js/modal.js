function openModal() {
    const modal = document.getElementById("myModal");
    modal.style.display = "block";
    initThreeJS(); // threejs_init.js에서 정의
    animate();     // threejs_init.js에서 정의
}

function closeModal() {
    const modal = document.getElementById("myModal");
    modal.style.display = "none";
    if (renderer) {
        renderer.dispose();
        document.getElementById("threejs-container").innerHTML = "";
    }
}

// 외부 클릭으로 모달 닫기
document.getElementById("myModal").addEventListener('click', function(event) {
    const modalContent = document.querySelector('.modal-content');
    if (!modalContent.contains(event.target)) {
        closeModal();
    }
});