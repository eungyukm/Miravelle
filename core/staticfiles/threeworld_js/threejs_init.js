let scene, camera, renderer, cube;

function initThreeJS() {
    const container = document.getElementById("threejs-container");

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 5;

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    adjustRendererSize();
}

function animate() {
    if (document.getElementById("myModal").style.display === "block") {
        requestAnimationFrame(animate);
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
}

function adjustRendererSize() {
    const container = document.getElementById("threejs-container");
    if (renderer) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }
}

window.addEventListener('resize', adjustRendererSize);
const modalContent = document.querySelector('.modal-content');
const resizeObserver = new ResizeObserver(() => adjustRendererSize());
resizeObserver.observe(modalContent);