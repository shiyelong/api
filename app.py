import easyocr
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import MarianMTModel, MarianTokenizer
import langid

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

# 模型名称
en_zh_model_name = "Helsinki-NLP/opus-mt-en-zh"
ja_zh_model_name = "Helsinki-NLP/opus-mt-ja-zh"

# 延迟加载模型
en_zh_model = None
ja_zh_model = None

# 初始化语音识别器
reader = easyocr.Reader(['ch_sim', 'en'])  # 只支持简体中文和英文

@app.route('/')
def index():
    return "欢迎来到 Flask API！"

def load_models():
    global en_zh_model, ja_zh_model
    if en_zh_model is None or ja_zh_model is None:
        try:
            print("正在加载英语到中文模型...")
            en_zh_tokenizer = MarianTokenizer.from_pretrained(en_zh_model_name)
            en_zh_model = MarianMTModel.from_pretrained(en_zh_model_name)
            print("英语到中文模型加载成功")

            print("正在加载日语到中文模型...")
            ja_zh_tokenizer = MarianTokenizer.from_pretrained(ja_zh_model_name)
            ja_zh_model = MarianMTModel.from_pretrained(ja_zh_model_name)
            print("日语到中文模型加载成功")
        except Exception as e:
            print(f"加载模型时出错: {e}")

@app.route('/translate', methods=['POST'])
def translate():
    load_models()  # 延迟加载模型

    if not request.json or 'text' not in request.json:
        return jsonify({'error': '未提供文本'}), 400

    data = request.json
    text = data['text']
    print(f"正在翻译: {text}")  # 打印接收到的文本

    try:
        lang, _ = langid.classify(text)
        print(f"识别到的语言: {lang}")

        if lang == 'en':
            inputs = MarianTokenizer.from_pretrained(en_zh_model_name)(text, return_tensors="pt", padding=True, truncation=True)
            translated = en_zh_model.generate(**inputs)
            translated_text = MarianTokenizer.from_pretrained(en_zh_model_name).decode(translated[0], skip_special_tokens=True)
        elif lang == 'ja':
            inputs = MarianTokenizer.from_pretrained(ja_zh_model_name)(text, return_tensors="pt", padding=True, truncation=True)
            translated = ja_zh_model.generate(**inputs)
            translated_text = MarianTokenizer.from_pretrained(ja_zh_model_name).decode(translated[0], skip_special_tokens=True)
        else:
            return jsonify({'error': '不支持的语言'}), 400
        
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"翻译过程中出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ocr_and_translate', methods=['POST'])
def ocr_and_translate():
    if 'image' not in request.files:
        return jsonify({'error': '未上传图像'}), 400

    image_file = request.files['image']

    try:
        image = image_file.read()
        result = reader.readtext(image, detail=1)
        ocr_text = " ".join([text[1] for text in result])
        print(f"识别出的文本: {ocr_text}")

        lang, _ = langid.classify(ocr_text)

        if lang == 'en':
            inputs = MarianTokenizer.from_pretrained(en_zh_model_name)(ocr_text, return_tensors="pt", padding=True, truncation=True)
            translated = en_zh_model.generate(**inputs)
            translated_text = MarianTokenizer.from_pretrained(en_zh_model_name).decode(translated[0], skip_special_tokens=True)
        elif lang == 'ja':
            inputs = MarianTokenizer.from_pretrained(ja_zh_model_name)(ocr_text, return_tensors="pt", padding=True, truncation=True)
            translated = ja_zh_model.generate(**inputs)
            translated_text = MarianTokenizer.from_pretrained(ja_zh_model_name).decode(translated[0], skip_special_tokens=True)
        else:
            return jsonify({'ocrText': ocr_text.strip()})

        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
