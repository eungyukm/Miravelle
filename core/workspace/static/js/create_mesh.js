document.addEventListener("DOMContentLoaded", function () {
    let currentJobId = null;
    localStorage.removeItem("currentJobId");

    // DOM 요소 가져오기
    const statusSection = document.getElementById("statusSection");
    const previewSection = document.getElementById("previewSection");
    const progressBar = document.getElementById("progressBar");
    const generateBtn = document.getElementById("generateBtn");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const errorMessage = document.getElementById("error-message");
    const thumbnail = document.getElementById("thumbnail");
    const video = document.getElementById("video");
    const videoSource = document.getElementById("videoSource");

    function startProgressStream(jobId) {
        if (!jobId) return;

        console.log("진행률 스트리밍 시작:", jobId);
        const eventSource = new EventSource(`/workspace/${jobId}/stream/`);

        eventSource.onmessage = function (event) {
            try {
                const data = JSON.parse(event.data);
                console.log("스트리밍 데이터 수신:", data);

                if (data.progress !== undefined) {
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.textContent = `${data.progress}%`;
                    statusSection.style.display = "block";
                }

                if (["SUCCEEDED", "FAILED", "CANCELED"].includes(data.status)) {
                    eventSource.close();
                    if (data.status === "SUCCEEDED") {
                        fetchMeshData(jobId);  // ✅ 100% 완료되면 get_mesh 실행
                    } else {
                        alert("모델 생성 실패!");
                    }
                }
            } catch (error) {
                console.error("JSON 파싱 오류:", error);
            }
        };

        eventSource.onerror = function () {
            console.error("스트리밍 연결 오류. 3초 후 재시도...");
            eventSource.close();
            setTimeout(() => startProgressStream(jobId), 3000);
        };
    }

    function fetchMeshData(jobId) {
        fetch(`/workspace/${jobId}/`)
            .then(response => response.json())
            .then(mesh => {
                console.log("Mesh data:", mesh);
                if (mesh.thumbnail_url) {
                    thumbnail.src = mesh.thumbnail_url;
                    thumbnail.style.display = "block";
                }
                if (mesh.video_url) {
                    videoSource.src = mesh.video_url;
                    video.load();
                    video.style.display = "block";
                }
                previewSection.style.display = "block";
                alert("모델 생성 완료!");
            })
            .catch(error => {
                console.error("Error fetching mesh data:", error);
                alert("모델 데이터를 가져오는 중 오류가 발생했습니다.");
            });
    }

    document.getElementById("meshForm").addEventListener("submit", function (event) {
        event.preventDefault();
        generateBtn.disabled = true;
        generateBtn.innerText = "Generating...";
        loadingSpinner.style.display = "block";
        previewSection.classList.add("hidden");
        errorMessage.innerText = "";

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        const prompt = document.getElementById("prompt").value;
        const artStyle = document.getElementById("art_style").value;

        fetch("/workspace/api/generate_mesh/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ prompt, art_style: artStyle })
        })
        .then(response => response.json())
        .then(data => {
            generateBtn.disabled = false;
            generateBtn.innerText = "Generate Model";
            loadingSpinner.style.display = "none";

            if (data.error) {
                errorMessage.innerText = data.error;
                return;
            }

            currentJobId = data.job_id;
            localStorage.setItem("currentJobId", currentJobId);
            if (currentJobId) {
                startProgressStream(currentJobId);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            errorMessage.innerText = "An error occurred.";
            generateBtn.disabled = false;
            generateBtn.innerText = "Generate Model";
            loadingSpinner.style.display = "none";
        });
    });
});