document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    const userInput = document.getElementById('userInput');
    const output = document.getElementById('output');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const MAX_INPUT_LENGTH = 500; // 최대 입력 길이

    if (!submitBtn || !userInput || !output || !loading || !error) {
        console.error("필수 요소가 존재하지 않습니다. HTML 구조를 확인하세요.");
        return;
    }

    submitBtn.addEventListener('click', function() {
        const inputText = userInput.value;

        // 입력값 검증
        if (!inputText) {
            error.textContent = "프롬프트를 입력해주세요.";
            error.style.display = "block";
            return;
        }

        if (inputText.length > MAX_INPUT_LENGTH) {
            error.textContent = `입력은 ${MAX_INPUT_LENGTH}자를 초과할 수 없습니다.`;
            error.style.display = "block";
            return;
        }

        // 로딩 표시
        loading.style.display = "block";
        output.style.display = "none";
        error.style.display = "none";

        fetch('/api/prompts/', {  // API 엔드포인트 URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN  // CSRF 토큰
            },
            body: JSON.stringify({ user_input: inputText })  // 요청 본문
        })
        .then(response => {
            loading.style.display = "none";  // 로딩 숨김
            output.style.display = "block"; // 결과 표시 영역 보이게 함

            if (!response.ok) {
                // HTTP 에러 처리
                return response.json().then(err => {
                    throw new Error(err.error || 'API 요청 실패');
                });
            }
            return response.json();
        })
        .then(data => {
            // 성공적으로 응답을 받은 경우
            output.textContent = data.Miravelle || "결과를 가져올 수 없습니다."; // 결과 표시
        })
        .catch(err => {
            // 에러가 발생한 경우
            error.textContent = err.message || "서버 오류가 발생했습니다."; // 에러 메시지 표시
            error.style.display = "block"; // 에러 메시지 보이게 함
        });
    });
});