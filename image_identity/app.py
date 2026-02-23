from flask import Flask, render_template, request, send_file, jsonify
from DECIMER.decimer import predict_SMILES
from rdkit import Chem
from rdkit.Chem import Draw
import os
import uuid
from PIL import Image

app = Flask(__name__)

# 配置上传文件夹和输出文件夹
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def identify():
    """识别图片中的化学分子"""
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    # 保存上传的文件
    filename = f"{uuid.uuid4()}.png"
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        # 使用 DECIMER 识别 SMILES
        smiles = predict_SMILES(upload_path)

        # 验证 SMILES 并生成图片
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            output_filename = f"{uuid.uuid4()}.png"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            img = Draw.MolToImage(mol, size=(400, 400))
            img.save(output_path)

            return jsonify({
                'success': True,
                'smiles': smiles,
                'image_url': f'/static/outputs/{output_filename}'
            })
        else:
            return jsonify({'error': 'SMILES 格式错误'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
