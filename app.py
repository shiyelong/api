import sys
print("Python Path:", sys.path)
print("Python Version:", sys.version)
from flask import Flask, request, jsonify
from pytranslation import Translator
import pytesseract
from PIL import Image
import io
from flask_cors import CORS  # 处理跨域请求

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

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

    print(f"Translating: {text}")  # 打印接收到的文本

    try:
        # 使用 pytranslation 翻译文本
        translated_text = Translator().translate(text, dest='zh').text
        print(f"Translated Text: {translated_text}")  # 打印翻译结果
        return jsonify({'translatedText': translated_text})
    except Exception as e:
        print(f"Error during translation: {str(e)}")  # 打印错误信息
        return jsonify({'error': str(e)}), 500

@app.route('/ocr', methods=['POST'])
def ocr():
    # 检查请求是否包含图像文件
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    
    try:
        image = Image.open(io.BytesIO(image_file.read()))
        # 使用 pytesseract 提取图像中的文本
        ocr_text = pytesseract.image_to_string(image)
        return jsonify({'ocrText': ocr_text})
    except Exception as e:
        print(f"Error during OCR: {str(e)}")  # 打印错误信息
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
