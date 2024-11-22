from flask import Flask, request, jsonify
from googletrans import Translator
import pytesseract
from PIL import Image
import io

app = Flask(__name__)
translator = Translator()

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data['text']
    translated_text = translator.translate(text, dest='zh-cn').text
    return jsonify({'translatedText': translated_text})

@app.route('/ocr', methods=['POST'])
def ocr():
    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    ocr_text = pytesseract.image_to_string(image)
    return jsonify({'ocrText': ocr_text})

if __name__ == '__main__':
    app.run(debug=True)
