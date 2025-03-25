// 특정 이름의 쿠키 값을 가져오는 함수
function getCookie(name) {
    let cookieValue = null;  // 쿠키 값을 저장할 변수 (초기값: null)

    if (document.cookie && document.cookie !== '') {  // 쿠키가 존재하는지 확인
        const cookies = document.cookie.split(';');  // 쿠키 문자열을 ';' 기준으로 분리하여 배열로 저장

        for (let i = 0; i < cookies.length; i++) {  // 배열을 순회하며 원하는 쿠키 찾기
            const cookie = cookies[i].trim();  // 공백 제거

            // 쿠키 이름이 우리가 찾는 값(name)으로 시작하는지 확인
            if (cookie.startsWith(name + '=')) {
                // '=' 이후의 값이 실제 쿠키 값이므로 이를 가져와 디코딩하여 저장
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;  // 원하는 쿠키를 찾았으니 반복문 종료
            }
        }
    }
    return cookieValue;  // 최종적으로 찾은 쿠키 값을 반환 (없다면 null)
}

// 페이지가 로드되면 실행되는 이벤트 리스너
document.addEventListener('DOMContentLoaded', function() {
    // HTML에서 사용할 요소들 가져오기 (버튼, 입력창, 결과 출력 영역 등)
    const submitBtn = document.getElementById('submitBtn');  // "Generate" 버튼
    const userInput = document.getElementById('userInput');  // 사용자 입력 필드
    const output = document.getElementById('output');  // 결과 출력할 div
    const loading = document.getElementById('loading');  // 로딩 메시지
    const error = document.getElementById('error');  // 오류 메시지
    const csrfToken = getCookie('csrftoken');  // CSRF 토큰 가져오기
    const API_URL = '/api/prompts/';  // 백엔드 API의 URL

    // 콘솔에서 CSRF 토큰이 잘 가져와졌는지 확인 (디버깅용)
    console.log("csrfToken: ", csrfToken);

    // 필수 요소가 없을 경우 콘솔에 오류 메시지를 출력하고 코드 실행을 중단
    if (!submitBtn || !userInput || !output || !loading || !error) {
        console.error("필수 요소가 존재하지 않습니다. HTML 구조를 확인하세요.");
        return;
    }

    // CSRF 토큰이 없을 경우 보안 문제로 요청을 차단
    if (!csrfToken) {
        console.error("CSRF 토큰을 가져올 수 없습니다. 요청이 차단됩니다.");
        error.textContent = "보안 오류: CSRF 토큰이 없습니다.";
        error.style.display = "block";  // 오류 메시지를 화면에 표시
        return;  // 코드 실행 중단
    }

    // 버튼 클릭 시 실행되는 함수
    submitBtn.addEventListener('click', function() {
        console.log("generate button click"); // click을 눌렀을 때 콘솔 확인 250325
        const inputText = userInput.value;  // 사용자가 입력한 텍스트 가져오기

        // 입력값 검증 (빈 입력 방지)
        if (!inputText) {
            error.textContent = "프롬프트를 입력해주세요.";  // 사용자에게 알림
            error.style.display = "block";  // 오류 메시지 표시
            return;  // 요청 중단
        }

        // 글자 수 제한 (500자 초과 시 오류 메시지 출력)
        if (inputText.length > 500) {
            error.textContent = "입력은 500자를 초과할 수 없습니다.";
            error.style.display = "block";
            return;
        }

        // 로딩 표시 활성화 (사용자가 기다리는 동안 로딩 메시지 표시)
        loading.style.display = "block";
        output.style.display = "none";  // 기존 출력 숨김
        error.style.display = "none";  // 기존 오류 메시지 숨김

        // 백엔드로 AJAX 요청 보내기 (fetch API 사용)
        fetch(API_URL, {  
            method: 'POST',  // POST 요청 (새 데이터를 서버로 보낼 때 사용)
            headers: {
                'Content-Type': 'application/json',  // 데이터 타입을 JSON으로 설정
                'X-CSRFToken': csrfToken  // CSRF 보안 토큰 추가 (Django에서 요구함)
            },
            body: JSON.stringify({ user_input: inputText })  // 사용자의 입력을 JSON 형식으로 변환하여 전송
        })
        .then(response => {
            // 요청이 끝났으므로 로딩 표시 숨기기
            console.log("response : ", response); // response가 받아지는지 확인 250325
            loading.style.display = "none";
            output.style.display = "block";  // 결과 표시 활성화

            // 서버 응답이 정상적이지 않을 경우 처리
            if (!response.ok) {
                return response.text().then(text => {  // 응답 본문을 가져옴
                    try {
                        const err = JSON.parse(text);  // JSON으로 변환 시도
                        throw new Error(err.error || "API 요청 실패");  // 서버에서 보낸 오류 메시지 출력
                    } catch {
                        throw new Error("서버 오류: 예상치 못한 응답을 받았습니다.");  // JSON 변환 실패 시 일반 오류 처리
                    }
                });
            }
            return response.json();  // 응답을 JSON 형식으로 변환
        })
        .then(data => {
            console.log("data : ", data); // data가 받아지는지 확인 250325
            // 서버 응답이 정상적일 경우 결과 출력
            if (data.Miravelle) {
                console.log("data.Miravelle : ", data.Miravelle) // Miravelle data가 잘 넘어오는지 확인 250325
                output.textContent = data.Miravelle;  // 서버에서 받은 결과 출력
            } else {
                throw new Error(data.error || "서버 응답 오류: 결과를 가져올 수 없습니다.");  // 예상과 다른 응답 처리
            }
        })
        .catch(err => {
            // 오류 발생 시 사용자에게 표시
            error.textContent = err.message || "서버 오류가 발생했습니다.";
            error.style.display = "block";
        });
    });
});
