from flask import Flask, request, jsonify
from googletrans import Translator
import pytesseract
from PIL import Image
import io
from flask_cors import CORS  # 处理跨域请求

app = Flask(__name__)
CORS(app)  # 启用 CORS 支持
translator = Translator()

@app.route('/')
def index():
    return "Welcome to the Flask API!"

@app.route('/translate', methods=['POST'])
def translate():
    # 检查请求数据
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400

    data = request.json
    text = data['text']
    # 翻译文本
    translated_text = translator.translate(text, dest='zh-cn').text
    return jsonify({'translatedText': translated_text})

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    # 使用 pytesseract 提取图像中的文本
    ocr_text = pytesseract.image_to_string(image)
    return jsonify({'ocrText': ocr_text})

if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
