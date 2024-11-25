import easyocr
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import MarianMTModel, MarianTokenizer
import langid  # 用于语言识别

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

# 下载和加载翻译模型
en_zh_model_name = "Helsinki-NLP/opus-mt-en-zh"
en_zh_tokenizer = MarianTokenizer.from_pretrained(en_zh_model_name)
en_zh_model = MarianMTModel.from_pretrained(en_zh_model_name)

ja_zh_model_name = "Helsinki-NLP/opus-mt-ja-zh"
ja_zh_tokenizer = MarianTokenizer.from_pretrained(ja_zh_model_name)
ja_zh_model = MarianMTModel.from_pretrained(ja_zh_model_name)

# 初始化 EasyOCR 读取器，支持中文、英文和日文
reader = easyocr.Reader(['ch_sim', 'en', 'ja'])  # 支持简体中文、英文和日文

@app.route('/')
def index():
    return "欢迎来到 Flask API！"  # 提供欢迎信息

@app.route('/translate', methods=['POST'])
def translate():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': '未提供文本'}), 400

    data = request.json
    text = data['text']

    print(f"正在翻译: {text}")  # 打印接收到的文本

    try:
        # 自动识别语言
        lang, _ = langid.classify(text)

        if lang == 'en':
            # 英文到中文翻译
            inputs = en_zh_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = en_zh_model.generate(**inputs)
            translated_text = en_zh_tokenizer.decode(translated[0], skip_special_tokens=True)
        elif lang == 'ja':
            # 日文到中文翻译
            inputs = ja_zh_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = ja_zh_model.generate(**inputs)
            translated_text = ja_zh_tokenizer.decode(translated[0], skip_special_tokens=True)
        else:
            return jsonify({'error': '不支持的语言'}), 400
        
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

        # 执行 OCR 识别
        result = reader.readtext(image, detail=1)

        # 提取识别的文本
        ocr_text = " ".join([text[1] for text in result])
        print(f"识别出的文本: {ocr_text}")  # 打印识别出的文本

        # 自动识别语言
        lang, _ = langid.classify(ocr_text)

        # 对识别到的英文或日文进行翻译
        if lang == 'en':
            inputs = en_zh_tokenizer(ocr_text, return_tensors="pt", padding=True, truncation=True)
            translated = en_zh_model.generate(**inputs)
            translated_text = en_zh_tokenizer.decode(translated[0], skip_special_tokens=True)
        elif lang == 'ja':
            inputs = ja_zh_tokenizer(ocr_text, return_tensors="pt", padding=True, truncation=True)
            translated = ja_zh_model.generate(**inputs)
            translated_text = ja_zh_tokenizer.decode(translated[0], skip_special_tokens=True)
        else:
            return jsonify({'ocrText': ocr_text.strip()})  # 直接返回识别到的文本

        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
