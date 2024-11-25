import sys
print("Python Path:", sys.path)
print("Python Version:", sys.version)
from flask import Flask, request, jsonify
from translate import Translator  # 使用 translate 进行翻译
import easyocr  # 使用 EasyOCR 进行 OCR
from flask_cors import CORS  # 处理跨域请求
import io
#
# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

@app.route('/')
def index():
    return "欢迎来到 Flask API！"  # 提供欢迎信息

@app.route('/translate_text', methods=['POST'])
def translate_text():
    # 检查请求数据
    if not request.json or 'text' not in request.json:
        return jsonify({'error': '未提供文本'}), 400

    data = request.json
    text = data['text']
    
    print(f"正在翻译: {text}")  # 打印接收到的文本

    try:
        # 将文本翻译成中文
        translator = Translator(to_lang="zh")
        translated_text = translator.translate(text)
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"翻译过程中出错: {str(e)}")  # 打印错误信息
        return jsonify({'error': str(e)}), 500

@app.route('/ocr_and_translate', methods=['POST'])
def ocr_and_translate():
    # 检查请求是否包含图像文件
    if 'image' not in request.files:
        return jsonify({'error': '未上传图像'}), 400

    image_file = request.files['image']

    try:
        # 读取图像文件
        image = image_file.read()

        # 初始化 EasyOCR 读取器，支持中文和英文
        reader = easyocr.Reader(['ch_sim', 'en'])  # 仅支持简体中文和英文

        # 执行 OCR 识别
        result = reader.readtext(image, detail=1)

        # 提取识别的文本
        ocr_text = " ".join([text[1] for text in result])
        print(f"识别出的文本: {ocr_text}")  # 打印识别出的文本

        # 检查识别的文本是否包含中文
        if any(u'\u4e00' <= char <= u'\u9fff' for char in ocr_text):  # 检查是否包含中文字符
            return jsonify({'ocrText': ocr_text.strip()})  # 直接返回识别到的中文
        
        # 如果是英文，则翻译成中文
        translator = Translator(to_lang="zh")
        translated_text = translator.translate(ocr_text)
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")  # 打印错误信息
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
