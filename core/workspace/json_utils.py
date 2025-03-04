import json

def extract_url_to_dic(data):
    fbx_url = data.get("model_urls", {}).get("fbx", None)
    thumbnail_url = data.get("thumbnail_url", None)

    return fbx_url, thumbnail_url


# 테스트용 JSON 데이터 (실제 데이터를 여기에 넣어 테스트 가능)
json_data = {
    "id": "018a210d-8ba4-705c-b111-1f1776f7f578",
    "model_urls": {
        "glb": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/model.glb?Expires=***",
        "fbx": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/model.fbx?Expires=***",
        "obj": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/model.obj?Expires=***",
        "mtl": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/model.mtl?Expires=***",
        "usdz": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/model.usdz?Expires=***"
    },
    "thumbnail_url": "https://assets.meshy.ai/***/tasks/018a210d-8ba4-705c-b111-1f1776f7f578/output/preview.png?Expires=***"
}

fbx_url, thumbnail_url = extract_url_to_dic(json_data)
print(f"fbx url {fbx_url}")
print(f"thumbanil url {thumbnail_url}")