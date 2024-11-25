import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

# 设置Marian NMT模型的路径
MODEL_PATH = '/path/to/your/model'  # 替换为您的模型路径
CONFIG_PATH = os.path.join(MODEL_PATH, 'config.yml')  # 确保有 config.yml 文件

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
        # 使用 Marian NMT 进行翻译
        input_file = 'input.txt'
        output_file = 'output.txt'

        # 将输入文本写入文件
        with open(input_file, 'w') as f:
            f.write(text)

        # 调用 Marian NMT 的解码器
        subprocess.run(['./marian-decoder', '-c', CONFIG_PATH, '--input', input_file, '--output', output_file])

        # 读取翻译结果
        with open(output_file, 'r') as f:
            translated_text = f.read().strip()
        
        return jsonify({'translatedText': translated_text})

    except Exception as e:
        print(f"翻译过程中出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 在开发模式下运行
