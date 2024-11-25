import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import torch
from onmt.translate.translator import build_translator
from onmt.opts import initial_options, model_options, translate_options

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

# 加载 OpenNMT 翻译模型的函数
def load_model(model_path):
    # 设置模型参数
    options = initial_options()
    model_options(options)
    translate_options(options)

    # 指定模型文件
    options.models = [model_path]
    options.verbose = True

    # 创建翻译器
    translator = build_translator(options, report_score=True)
    return translator

# 在全局变量中存储翻译器
translator = load_model('/path/to/your/model/model.pt')  # 替换为你的模型路径

@app.route('/')
def index():
    return "欢迎来到 Flask API！"  # 提供欢迎信息

@app.route('/translate_text', methods=['POST'])
def translate_text():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': '未提供文本'}), 400

    data = request.json
    text = data['text']
    
    print(f"正在翻译: {text}")  # 打印接收到的文本

    try:
        # 调用翻译
        translated_output = translator.translate(text)
        translated_text = translated_output[0].pred_sents[0]
        
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"翻译过程中出错: {str(e)}")
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

        # 初始化 EasyOCR 读取器，支持中文、英文和日文
        reader = easyocr.Reader(['ch_sim', 'en', 'ja'])  # 支持简体中文、英文和日文

        # 执行 OCR 识别
        result = reader.readtext(image, detail=1)

        # 提取识别的文本
        ocr_text = " ".join([text[1] for text in result])
        print(f"识别出的文本: {ocr_text}")  # 打印识别出的文本

        # 如果识别的文本有中文，直接返回
        if any(u'\u4e00' <= char <= u'\u9fff' for char in ocr_text):
            return jsonify({'ocrText': ocr_text.strip()})  # 直接返回识别到的中文
        
        # 如果是英文或日文，则翻译成中文
        translated_output = translator.translate(ocr_text)
        translated_text = translated_output[0].pred_sents[0]
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
