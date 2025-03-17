from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
import clip
import shutil

app = FastAPI()

# CLIP 모델 로드
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 이미지 평가 함수
def evaluate_image(image_path: str, prompts: list):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = clip.tokenize(prompts).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

    similarity = (image_features @ text_features.T).softmax(dim=-1)
    return float(similarity[0][0])  # 높은 점수가 좋은 이미지


@app.post("/evaluate/")
async def upload_and_evaluate_image(file: UploadFile = File(...)):
    file_path = f"uploaded_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 다양한 기준으로 점수 평가
    score_aesthetic = evaluate_image(file_path, ["beautiful image", "bad image"])  # 미적 가치
    score_sharpness = evaluate_image(file_path, ["sharp image", "blurry image"])  # 선명도
    score_brightness = evaluate_image(file_path, ["well-lit image", "dark image"])  # 밝기
    score_color = evaluate_image(file_path, [
        "vibrant colors", "dull colors", 
        "rich color depth", "harmonious color balance",
        "cinematic color grading", "fantasy-style colors", 
        "surreal vibrant colors"
    ])  # 색감 평가 수정
    score_composition = evaluate_image(file_path, [
        "well-composed image", "poor composition",
        "epic fantasy composition",
        "dramatic perspective",
        "cinematic framing"
    ])  # 구도 평가 강화

    # 가중치를 반영한 최종 점수 계산
    overall_score = (
        (score_aesthetic * 0.3) +  
        (score_sharpness * 0.2) +  
        (score_brightness * 0.15) +  
        (score_color * 0.15) +  
        (score_composition * 0.2)
    )

    # 한국어 등급 및 평가 이유 설정
    if overall_score > 0.85:
        rating = "탁월함"
        reason = "이 이미지는 매우 아름답고, 밝기와 구도가 훌륭하며 색감이 뛰어납니다."
    elif overall_score > 0.7:
        rating = "좋음"
        if score_color < 0.3:
            reason = "이 이미지는 조화로운 구성을 가지고 있으며, 밝기와 선명도가 뛰어나지만 색감이 단조로울 수 있습니다."
        else:
            reason = "이 이미지는 조화로운 구성을 가지고 있으며, 밝기와 색감이 대체로 양호합니다."
    else:
        rating = "보통"
        reason = "이 이미지는 밝기나 색감, 구도 측면에서 개선이 필요할 수 있습니다."

    return {
        "파일명": file.filename,
        "전체 점수": overall_score,
        "등급": rating,
        "세부 평가": {
            "미적 가치": score_aesthetic,
            "선명도": score_sharpness,
            "밝기": score_brightness,
            "색감": score_color,
            "구도": score_composition
        },
        "평가 이유": reason
    }