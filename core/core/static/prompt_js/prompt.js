function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    const userInput = document.getElementById('userInput');
    const output = document.getElementById('output');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const csrfToken = getCookie('csrftoken');  // CSRF 토큰 가져오기
    console.log("csrfToken: ", csrfToken);

    if (!submitBtn || !userInput || !output || !loading || !error) {
        console.error("필수 요소가 존재하지 않습니다. HTML 구조를 확인하세요.");
        return;
    }

    submitBtn.addEventListener('click', function() {
        const inputText = userInput.value;

        if (!inputText) {
            error.textContent = "프롬프트를 입력해주세요.";
            error.style.display = "block";
            return;
        }

        if (inputText.length > 500) {
            error.textContent = "입력은 500자를 초과할 수 없습니다.";
            error.style.display = "block";
            return;
        }

        loading.style.display = "block";
        output.style.display = "none";
        error.style.display = "none";

        fetch('/api/prompts/', {  
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // CSRF 토큰 추가
            },
            body: JSON.stringify({ user_input: inputText })
        })
        .then(response => {
            loading.style.display = "none";
            output.style.display = "block";

            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'API 요청 실패');
                });
            }
            return response.json();
        })
        .then(data => {
            output.textContent = data.Miravelle || "결과를 가져올 수 없습니다.";
        })
        .catch(err => {
            error.textContent = err.message || "서버 오류가 발생했습니다.";
            error.style.display = "block";
        });
    });
});
