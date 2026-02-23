from DECIMER.decimer import predict_SMILES  # 注意大小写：DECIMER文件夹 + decimer.py模块 + predict_SMILES函数
# 示例：预测图片中的化学结构
smiles = predict_SMILES("C:/Users/44818/Desktop/chem_project/image_identity/3.jpg")  # 替换为你的图片路径
print(smiles)  # 输出预测的SMILES字符串
