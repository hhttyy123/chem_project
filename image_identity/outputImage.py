from rdkit import Chem
from rdkit.Chem import Draw

# 从 SMILES 创建分子（SMILES 是简化分子线性输入规范）
smiles = "C1=CC=C(C=C1)CC(=O)NC2=CC=CC=C2"  # 乙醇的 SMILES
mol = Chem.MolFromSmiles(smiles)
if mol is not None:
    print("分子创建成功")
    # 保存分子为图片
    img = Draw.MolToImage(mol)
    img.save("output.png")
else:
    print("SMILES 格式错误")