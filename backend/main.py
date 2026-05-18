from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import zipfile
from pathlib import Path
import requests
import os

app = FastAPI(title="محول الصور إلى 3D")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

HF_API_KEY = os.environ.get("HF_API_KEY", "")
HF_API_URL = "https://api-inference.huggingface.co/models/TencentARC/InstantMesh"


def clean_folder(folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            item.unlink()


@app.get("/")
def home():
    return {
        "message": "السيرفر يعمل بنجاح!",
        "status": "OK",
        "has_api_key": bool(HF_API_KEY)
    }


@app.post("/convert")
async def convert_images(files: list[UploadFile] = File(...)):
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="يرجى رفع صورة واحدة على الأقل")

    clean_folder(UPLOAD_DIR)
    clean_folder(OUTPUT_DIR)

    first_file = files[0]
    suffix = Path(first_file.filename).suffix.lower() or ".png"
    input_path = UPLOAD_DIR / f"input{suffix}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(first_file.file, buffer)

    print(f"✅ تم استلام الصورة: {first_file.filename}")

    if HF_API_KEY:
        try:
            with open(input_path, "rb") as f:
                image_bytes = f.read()

            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            print("🔄 جاري إرسال الصورة إلى الذكاء الاصطناعي...")

            response = requests.post(
                HF_API_URL,
                headers=headers,
                data=image_bytes,
                timeout=180
            )

            if response.status_code == 200:
                output_filename = "model_result.glb"
                output_path = OUTPUT_DIR / output_filename

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✅ تم إنشاء موديل 3D حقيقي!")

                zip_name = "model_3d.zip"
                zip_path = OUTPUT_DIR / zip_name

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(output_path, arcname=output_filename)
                    zipf.write(input_path, arcname=f"texture{suffix}")

                base_url = os.environ.get("BASE_URL", "http://localhost:8000")
                return {
                    "success": True,
                    "message": "✅ تم تحويل الصورة إلى موديل 3D حقيقي بالذكاء الاصطناعي!",
                    "download_url": f"{base_url}/download/{zip_name}",
                    "filename": zip_name,
                    "type": "real_ai"
                }
            else:
                print(f"⚠️ خطأ من API ({response.status_code}): {response.text[:200]}")
        except Exception as e:
            print(f"❌ خطأ في الاتصال بـ AI: {e}")

    return create_mock_model(input_path, suffix)


def create_mock_model(input_path: Path, suffix: str):
    texture_name = f"texture{suffix}"
    texture_path = OUTPUT_DIR / texture_name
    shutil.copy(input_path, texture_path)

    obj_name = "model_result.obj"
    mtl_name = "model_result.mtl"
    obj_path = OUTPUT_DIR / obj_name
    mtl_path = OUTPUT_DIR / mtl_name

    mtl_content = f"""newmtl material0
Ka 1.000 1.000 1.000
Kd 1.000 1.000 1.000
Ks 0.000 0.000 0.000
d 1.0
illum 2
map_Kd {texture_name}
"""

    obj_content = f"""mtllib {mtl_name}
o TexturedCube
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0
vt 0.0 0.0
vt 1.0 0.0
vt 1.0 1.0
vt 0.0 1.0
usemtl material0
s off
f 1/1 2/2 3/3 4/4
f 5/1 8/2 7/3 6/4
f 1/1 5/2 6/3 2/4
f 2/1 6/2 7/3 3/4
f 3/1 7/2 8/3 4/4
f 5/1 1/2 4/3 8/4
"""

    with open(mtl_path, "w", encoding="utf-8") as f:
        f.write(mtl_content)
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write(obj_content)

    zip_name = "model_3d.zip"
    zip_path = OUTPUT_DIR / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(obj_path, arcname=obj_name)
        zipf.write(mtl_path, arcname=mtl_name)
        zipf.write(texture_path, arcname=texture_name)

    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    return {
        "success": True,
        "message": "⚠️ تم إنشاء موديل تجريبي (الذكاء الاصطناعي غير متاح)",
        "download_url": f"{base_url}/download/{zip_name}",
        "filename": zip_name,
        "type": "mock"
    }


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 بدء تشغيل السيرفر على المنفذ {port}")
    print(f"🔑 المفتاح موجود: {bool(HF_API_KEY)}")
    uvicorn.run(app, host="0.0.0.0", port=port)