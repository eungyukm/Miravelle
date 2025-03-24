// API 엔드포인트 URL 설정
const API_URL = "http://127.0.0.1:8000/api/prompts/";

// 사용자 입력을 받아 API 호출하는 함수
async function generatePrompt() {
    // 입력 필드에서 사용자 텍스트 가져오기
    const userInput = document.getElementById("userInput").value;
    
    if (!userInput) {
        alert("입력 값을 입력해주세요!");
        return;
    }
    
    try {
        // API에 보낼 요청 데이터 준비
        const requestData = { user_input: userInput };
        
        // API 호출
        const response = await fetch(API_URL, {
            method: "POST", // POST 요청 방식 사용
            headers: {
                "Content-Type": "application/json" // JSON 형식으로 요청 헤더 설정
            },
            body: JSON.stringify(requestData) // 데이터를 JSON 문자열로 변환하여 전송
        });
        
        // 응답 데이터 처리
        const responseData = await response.json();
        
        if (response.ok) {
            // 성공 시 결과를 화면에 표시
            document.getElementById("output").innerText = responseData.Miravelle;
        } else {
            // 오류 메시지 표시
            alert("오류 발생: " + responseData.error || "응답을 받아오지 못했습니다.");
        }
    } catch (error) {
        console.error("API 호출 중 오류 발생:", error);
        alert("API 요청 중 오류가 발생했습니다.");
    }
}

// 이벤트 리스너 추가
window.onload = function() {
    document.getElementById("submitBtn").addEventListener("click", generatePrompt);
};

// HTML 예제 (사용자가 입력하고 버튼을 클릭하면 결과가 표시됨)
// <input type="text" id="userInput" placeholder="프롬프트 입력">
// <button id="submitBtn">프롬프트 생성</button>
// <p id="output"></p>
