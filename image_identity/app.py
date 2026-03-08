from flask import Flask, render_template, request, jsonify
from DECIMER.decimer import predict_SMILES
from rdkit import Chem
from rdkit.Chem import Draw
import os
import uuid
import base64
from io import BytesIO

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def identify():
    """识别图片中的化学分子，返回 base64 图片"""
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    # 保存上传的文件（临时）
    filename = f"{uuid.uuid4()}.png"
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        # 使用 DECIMER 识别 SMILES
        smiles = predict_SMILES(upload_path)

        # 验证 SMILES 并生成图片（内存中，不保存）
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            # 将图片保存到内存
            img_buffer = BytesIO()
            img = Draw.MolToImage(mol, size=(400, 400))
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # 转换为 base64
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

            # 删除临时上传文件
            try:
                os.remove(upload_path)
            except:
                pass

            return jsonify({
                'success': True,
                'smiles': smiles,
                'image_data': f'data:image/png;base64,{img_base64}'
            })
        else:
            # 删除临时上传文件
            try:
                os.remove(upload_path)
            except:
                pass
            return jsonify({'error': f'SMILES 格式错误: {smiles}'}), 400

    except Exception as e:
        # 删除临时上传文件
        try:
            os.remove(upload_path)
        except:
            pass
        return jsonify({'error': f'识别失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
