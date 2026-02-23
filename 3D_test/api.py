#!/usr/bin/env python3
"""
MolVis Backend API
SMILES → 3D Molecule Parser using RDKit
Supports: SMILES, English names, Chinese names
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import json
from pathlib import Path

# RDKit imports
from rdkit import Chem
from rdkit.Chem import AllChem

# OpenBabel import for inorganic molecules (deprecated, not used)
try:
    from openbabel import pybel
    OPENBABEL_AVAILABLE = True
except ImportError:
    OPENBABEL_AVAILABLE = False
    print("Warning: OpenBabel not available. Inorganic molecules will use XTB fallback.")

# XTB + ASE for quantum chemistry based geometry optimization
XTB_AVAILABLE = False
try:
    from ase import Atoms
    from ase.optimize import BFGS
    try:
        from xtb.ase.calculator import XTBCalculator
        XTB_AVAILABLE = True
        print("XTB is available for quantum chemistry geometry optimization")
    except ImportError:
        print("Warning: XTB not available. Install with: pip install xtb ase")
except ImportError:
    print("Warning: ASE not available. Install with: pip install ase")

app = FastAPI(title="MolVis API", version="1.2.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data file path
DATA_FILE = Path(__file__).parent / "data" / "name_mapping.json"

# Name mapping cache
_NAME_MAPPING_CACHE = None

# Common inorganic elements and patterns
INORGANIC_PATTERNS = [
    # 中心原子 + 卤素/氧族元素
    r'^[A-Z][a-z]?\d*[FClBrIO][123456]*$',  # 如 SF4, PF5, ClF3
    r'^[A-Z][a-z]?\d*F\d+$',  # 如 CF4, BF3
    r'^Xe[IFOC]\d*$',  # 氙化合物
    r'^[A-Z][a-z]?[FClBrIO]3$',  # 如 ClF3
    r'^[A-Z][a-z]?[FClBrIO]5$',  # 如 PF5
    r'^[A-Z][a-z]?[FClBrIO]7$',  # 如 IF7
    r'^[A-Z][a-z]?\d*O\d*[234]*$',  # 氧化物
]

import re

def is_inorganic(smiles: str) -> bool:
    """
    判断SMILES是否为无机分子
    基于元素组成和结构模式判断
    """
    smiles = smiles.strip()

    # 包含金属元素（除常见有机金属外）
    organic_metals = {'Li', 'Be', 'B', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'K', 'Ca',
                     'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga',
                     'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Ag', 'Cd', 'In', 'Sn',
                     'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'Au', 'Hg', 'Tl', 'Pb', 'Bi',
                     'Po', 'At', 'Rn', 'Fr', 'Ra'}

    # 提取所有元素符号
    elements = set(re.findall(r'[A-Z][a-z]?', smiles))

    # 如果包含离子标记或特殊结构，可能是无机
    if '[' in smiles and ']' in smiles:
        # 检查是否是离子化合物
        return True

    # 检查是否匹配无机模式
    for pattern in INORGANIC_PATTERNS:
        if re.match(pattern, smiles):
            return True

    # 简单判断：如果只包含1-2个元素且不包含C/N/O/S/P等有机元素
    if len(elements) <= 2 and not any(e in {'C', 'N', 'O', 'S', 'P'} for e in elements):
        return elements <= {'H', 'F', 'Cl', 'Br', 'I', 'B', 'Si'}

    return False


def try_xtb_3d(mol, smiles: str):
    """
    使用 XTB 半经验量子化学方法优化几何结构
    返回优化后的RDKit Mol对象，失败返回None
    """
    if not XTB_AVAILABLE:
        return None

    try:
        import numpy as np

        num_atoms = mol.GetNumAtoms()

        # 获取原子符号列表
        symbols = []
        for i in range(num_atoms):
            atom = mol.GetAtomWithIdx(i)
            symbols.append(atom.GetSymbol())

        # 创建 ASE 原子对象
        atoms = Atoms(symbols)

        # 生成初始猜测坐标
        # 优先使用 RDKit 的 ETKDG 生成初始构型
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        embed_result = AllChem.EmbedMolecule(mol, params)

        if embed_result == -1:
            # RDKit 嵌入失败，使用简单线性排列作为初始猜测
            positions = []
            for i in range(num_atoms):
                positions.append([i * 2.0, 0.0, 0.0])
            atoms.set_positions(positions)
        else:
            # 使用 RDKit 生成的坐标作为初始猜测
            conf = mol.GetConformer()
            positions = []
            for i in range(num_atoms):
                pos = conf.GetAtomPosition(i)
                positions.append([pos.x, pos.y, pos.z])
            atoms.set_positions(positions)

        # 设置 XTB 计算器
        # GFN2-xTB 是半经验方法，速度快，对无机分子效果好
        calc = XTBCalculator(method="GFN2-xTB")
        atoms.calc = calc

        # 使用 BFGS 优化几何结构
        # fmax=0.05 表示力的收敛标准（Hartree/Bohr）
        optimizer = BFGS(atoms, logfile=None)
        optimizer.run(fmax=0.05, steps=1000)

        # 获取优化后的坐标
        final_positions = atoms.get_positions()

        # 创建新的 conformer 并设置坐标
        new_conf = Chem.Conformer(num_atoms)
        for i in range(num_atoms):
            new_conf.SetAtomPosition(i, (
                final_positions[i][0],
                final_positions[i][1],
                final_positions[i][2]
            ))

        mol.RemoveAllConformers()
        mol.AddConformer(new_conf)

        print(f"XTB optimization completed for {smiles}")
        return mol

    except Exception as e:
        print(f"XTB error: {e}")
        import traceback
        traceback.print_exc()
        return None


def try_openbabel_3d(smiles: str):
    """
    尝试使用OpenBabel生成3D结构 (已弃用，请使用XTB)
    返回RDKit Mol对象，失败返回None
    """
    if not OPENBABEL_AVAILABLE:
        return None

    try:
        # 使用OpenBabel读取SMILES并生成3D结构
        mol = pybel.readstring("smi", smiles)
        if not mol:
            return None

        # 生成3D坐标（使用MMFF94力场）
        mol.make3D(forcefield="mmff94")

        # 转换为SDF格式，然后转换为RDKit Mol对象
        sdf = mol.write("sdf")
        rdkit_mol = Chem.MolFromMolBlock(sdf)

        if rdkit_mol:
            return rdkit_mol
    except Exception as e:
        print(f"OpenBabel error: {e}")
        return None

    return None


def load_name_mapping() -> dict:
    """从 JSON 文件加载名称映射表"""
    global _NAME_MAPPING_CACHE

    if _NAME_MAPPING_CACHE is not None:
        return _NAME_MAPPING_CACHE

    if not DATA_FILE.exists():
        _NAME_MAPPING_CACHE = {}
        return {}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 递归展开嵌套的字典结构
    def flatten_dict(d, mapping=None):
        if mapping is None:
            mapping = {}
        for key, value in d.items():
            if isinstance(value, dict):
                # 递归处理嵌套字典
                flatten_dict(value, mapping)
            else:
                # 扁平化键值对
                mapping[key] = value
        return mapping

    # 跳过 metadata，只处理数据部分
    mapping = {}
    for category, items in data.items():
        if category == "_metadata":
            continue
        if isinstance(items, dict):
            flatten_dict(items, mapping)

    _NAME_MAPPING_CACHE = mapping
    return mapping


def name_to_smiles(name: str) -> str:
    """
    将名称（中文/英文/化学式）转换为 SMILES
    返回 SMILES 字符串，如果找不到返回 None
    """
    name = name.strip()
    mapping = load_name_mapping()

    # 直接查找
    if name in mapping:
        return mapping[name]

    # 如果本身是有效的 SMILES，直接返回
    mol = Chem.MolFromSmiles(name)
    if mol is not None:
        return name

    return None


class SMILESRequest(BaseModel):
    smiles: str


class SMILESInfo(BaseModel):
    smiles: str
    num_atoms: int
    num_bonds: int
    molecular_weight: float
    formula: str


@app.get("/")
def home():
    """API health check"""
    return {
        "status": "ok",
        "service": "MolVis Backend",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "xtb_available": XTB_AVAILABLE,
        "openbabel_available": OPENBABEL_AVAILABLE
    }


def generate_rdkit_3d(mol, num_bonds):
    """使用RDKit生成3D坐标（优化版）"""
    if num_bonds > 0:
        # Use ETKDGv3 with improved parameters for better geometry
        params = AllChem.ETKDGv3()
        params.randomSeed = 42  # Consistent results
        params.useExpTorsionAnglePrefs = True  # Use experimental torsion angles
        params.useBasicKnowledge = True  # Use chemical knowledge

        embed_result = AllChem.EmbedMolecule(mol, params)
        if embed_result != -1:
            # Use MMFF for more accurate optimization (better than UFF)
            try:
                # Try MMFF optimization first (better for organic molecules)
                AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
            except:
                # Fallback to UFF if MMFF fails
                AllChem.UFFOptimizeMolecule(mol, maxIters=500)
        else:
            # Fallback to manual positioning
            _set_manual_coordinates(mol)
    else:
        # Ion compound or single atoms - manual positioning
        _set_manual_coordinates(mol)

    return mol


@app.post("/parse")
def parse_smiles(request: SMILESRequest):
    """
    Parse SMILES/Name and return 3D molecular structure in PDB format
    Supports: SMILES, Chinese names, English names, Chemical formulas
    """
    smiles = request.smiles.strip()

    if not smiles:
        raise HTTPException(status_code=400, detail="Input is empty")

    try:
        # First, try to convert name to SMILES
        converted_smiles = name_to_smiles(smiles)
        if converted_smiles:
            smiles = converted_smiles

        # Parse SMILES
        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            raise HTTPException(status_code=400, detail="Invalid input: not a valid SMILES or known name")

        # Add hydrogens
        mol = Chem.AddHs(mol)

        num_atoms = mol.GetNumAtoms()
        num_bonds = mol.GetNumBonds()

        # Generate 3D coordinates
        # Strategy: Use XTB for inorganic molecules (quantum chemistry accuracy)
        # Use optimized RDKit for organic molecules
        if is_inorganic(smiles) and XTB_AVAILABLE:
            # Try XTB first for inorganic molecules (quantum chemistry)
            xtb_mol = try_xtb_3d(mol, smiles)
            if xtb_mol is not None:
                mol = xtb_mol
            else:
                # Fallback to RDKit if XTB fails
                mol = generate_rdkit_3d(mol, num_bonds)
        else:
            # Organic molecules or XTB not available: use optimized RDKit
            mol = generate_rdkit_3d(mol, num_bonds)

        if mol is None:
            raise HTTPException(status_code=500, detail="Failed to generate 3D structure")

        # Convert to PDB format
        pdb_block = Chem.MolToPDBBlock(mol)

        # Also get SDF format for backup
        sdf_block = Chem.MolToMolBlock(mol)

        return {
            "success": True,
            "smiles": smiles,
            "pdb": pdb_block,
            "sdf": sdf_block
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing input: {str(e)}")


def _set_manual_coordinates(mol):
    """Set 3D coordinates for molecules manually (for ions and single atoms)"""
    num_atoms = mol.GetNumAtoms()

    # Remove any existing conformers
    mol.RemoveAllConformers()

    # Create new conformer
    conf = Chem.Conformer(num_atoms)

    # Position atoms
    for i in range(num_atoms):
        atom = mol.GetAtomWithIdx(i)
        charge = atom.GetFormalCharge()

        # Strategy: arrange atoms along X axis
        # Positive charges on left, negative on right
        if charge > 0:
            # Cation - place on left
            x_pos = -2.0 - (i * 2.5)
        elif charge < 0:
            # Anion - place on right
            x_pos = 2.0 + (i * 2.5)
        else:
            # Neutral - place in middle
            x_pos = 0.0 + (i * 1.5)

        conf.SetAtomPosition(i, (x_pos, 0.0, 0.0))

    mol.AddConformer(conf)


@app.post("/info")
def get_molecule_info(request: SMILESRequest):
    """
    Get molecular information from SMILES/Name
    Supports: SMILES, Chinese names, English names, Chemical formulas
    """
    smiles = request.smiles.strip()

    if not smiles:
        raise HTTPException(status_code=400, detail="Input is empty")

    try:
        # First, try to convert name to SMILES
        converted_smiles = name_to_smiles(smiles)
        if converted_smiles:
            smiles = converted_smiles

        # Parse SMILES
        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            raise HTTPException(status_code=400, detail="Invalid input: not a valid SMILES or known name")

        # Get molecule properties
        num_atoms = mol.GetNumAtoms()
        num_bonds = mol.GetNumBonds()
        mol_weight = AllChem.CalcExactMolWt(mol)

        # Get molecular formula
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)

        return SMILESInfo(
            smiles=smiles,
            num_atoms=num_atoms,
            num_bonds=num_bonds,
            molecular_weight=round(mol_weight, 2),
            formula=formula
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting molecule info: {str(e)}")


@app.post("/validate")
def validate_smiles(request: SMILESRequest):
    """
    Validate if a input string is valid (SMILES or known name)
    Supports: SMILES, Chinese names, English names, Chemical formulas
    """
    smiles = request.smiles.strip()

    if not smiles:
        return {"valid": False, "error": "Empty input"}

    try:
        # First, try to convert name to SMILES
        converted_smiles = name_to_smiles(smiles)
        if converted_smiles:
            return {
                "valid": True,
                "input": smiles,
                "smiles": converted_smiles,
                "type": "name"
            }

        # Try as SMILES
        mol = Chem.MolFromSmiles(smiles)
        is_valid = mol is not None

        if is_valid:
            return {
                "valid": True,
                "input": smiles,
                "smiles": smiles,
                "type": "smiles"
            }
        else:
            return {
                "valid": False,
                "input": smiles,
                "error": "Not a valid SMILES or known name"
            }
    except Exception as e:
        return {
            "valid": False,
            "input": smiles,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("MolVis Backend Server")
    print("=" * 50)
    print("Starting server at: http://localhost:8001")
    print("API documentation: http://localhost:8001/docs")
    print("=" * 50)

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
