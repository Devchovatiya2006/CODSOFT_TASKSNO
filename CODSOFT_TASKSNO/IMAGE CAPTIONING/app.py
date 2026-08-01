import os
from PIL import Image
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from transformers import BlipProcessor, BlipForConditionalGeneration

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

print("⏳ Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
model.eval()
print("✅ BLIP Model loaded!")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/caption", methods=["POST"])
def caption():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    img = Image.open(filepath).convert("RGB")
    inputs = processor(img, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=100, num_beams=5, min_length=20)
    caption_text = processor.decode(output[0], skip_special_tokens=True)

    return jsonify({"caption": caption_text, "image_url": f"/static/uploads/{filename}"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
