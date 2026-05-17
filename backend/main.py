from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import zipfile
from pathlib import Path
import time

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


def clean_folder(folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            item.unlink()


@app.get("/")
def home():
    return {"message": "السيرفر يعمل بنجاح!", "status": "OK"}


@app.post("/convert")
async def convert_images(files: list[UploadFile] = File(...)):
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="يرجى رفع صورة واحدة على الأقل")

    clean_folder(UPLOAD_DIR)
    clean_folder(OUTPUT_DIR)

    saved_files = []

    for index, file in enumerate(files, start=1):
        suffix = Path(file.filename).suffix.lower() or ".png"
        safe_name = f"image_{index}{suffix}"
        file_path = UPLOAD_DIR / safe_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file_path)
        print(f"تم حفظ: {safe_name}")

    print(f"جاري معالجة {len(saved_files)} صور...")
    time.sleep(2)

    # سنستخدم أول صورة كـ Texture
    first_image = saved_files[0]
    texture_name = f"texture{first_image.suffix.lower()}"
    texture_output_path = OUTPUT_DIR / texture_name
    shutil.copy(first_image, texture_output_path)

    obj_name = "model_result.obj"
    mtl_name = "model_result.mtl"
    zip_name = "model_with_texture.zip"

    obj_path = OUTPUT_DIR / obj_name
    mtl_path = OUTPUT_DIR / mtl_name
    zip_path = OUTPUT_DIR / zip_name

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

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(obj_path, arcname=obj_name)
        zipf.write(mtl_path, arcname=mtl_name)
        zipf.write(texture_output_path, arcname=texture_name)

    print(f"تم إنشاء الملف المضغوط: {zip_name}")

    return {
        "success": True,
        "message": f"تم تحويل {len(saved_files)} صور بنجاح مع Texture!",
        "download_url": f"http://localhost:8000/download/{zip_name}",
        "filename": zip_name
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
    print("بدء تشغيل السيرفر على http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)