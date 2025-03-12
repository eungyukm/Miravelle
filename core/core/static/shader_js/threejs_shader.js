let scene, camera, renderer, cube;

function initThreeJS() {
    const container = document.getElementById("threejs-container");

    // 장면 설정
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xcccccc); // 배경색 회색으로 설정 (검은색 확인용)

    // 카메라 설정
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 5); // 카메라가 큐브를 볼 수 있도록 설정

    // 렌더러 설정
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // 셰이더 정의
    const vertexShader = `
        varying vec3 vNormal;
        void main() {
            vNormal = normalize(normalMatrix * normal); // 노멀 벡터 변환
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `;

    const fragmentShader = `
        uniform vec3 uColor;
        varying vec3 vNormal;
        void main() {
            gl_FragColor = vec4(uColor * abs(vNormal), 1.0); // 노멀 벡터로 색상 변조
        }
    `;

    // ShaderMaterial 생성
    const material = new THREE.ShaderMaterial({
        uniforms: {
            uColor: { value: new THREE.Vector3(0.0, 1.0, 0.0) } // 초록색
        },
        vertexShader: vertexShader,
        fragmentShader: fragmentShader
    });

    // 큐브 생성
    const geometry = new THREE.BoxGeometry(2, 2, 2); // 크기 증가로 더 잘 보이게
    cube = new THREE.Mesh(geometry, material);
    cube.position.set(0, 0, 0); // 큐브가 카메라 앞에 오도록
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
    if (renderer && camera) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }
}

window.addEventListener('resize', adjustRendererSize);
const modalContent = document.querySelector('.modal-content');
if (modalContent) {
    const resizeObserver = new ResizeObserver(() => adjustRendererSize());
    resizeObserver.observe(modalContent);
}