#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
化学物质晶体类型分类表 -> 完整SMILES映射
从MD文件提取化学式、中英文名称，生成包含中英文的name_mapping.json
"""

import json
import re
from pathlib import Path

# 完整的化学信息映射表（化学式 -> 英文名, 中文名, SMILES, 类别）
COMPLETE_CHEMICAL_DATA = {
    # ===== 金属晶体 (55种) =====
    'Ag': {'english': 'Silver', 'chinese': '银', 'smiles': '[Ag]'},
    'Al': {'english': 'Aluminum', 'chinese': '铝', 'smiles': '[Al]'},
    'As': {'english': 'Arsenic', 'chinese': '砷', 'smiles': '[As]'},
    'Au': {'english': 'Gold', 'chinese': '金', 'smiles': '[Au]'},
    'Ba': {'english': 'Barium', 'chinese': '钡', 'smiles': '[Ba]'},
    'Be': {'english': 'Beryllium', 'chinese': '铍', 'smiles': '[Be]'},
    'Bi': {'english': 'Bismuth', 'chinese': '铋', 'smiles': '[Bi]'},
    'Ca': {'english': 'Calcium', 'chinese': '钙', 'smiles': '[Ca]'},
    'Cd': {'english': 'Cadmium', 'chinese': '镉', 'smiles': '[Cd]'},
    'Ce': {'english': 'Cerium', 'chinese': '铈', 'smiles': '[Ce]'},
    'Co': {'english': 'Cobalt', 'chinese': '钴', 'smiles': '[Co]'},
    'Cr': {'english': 'Chromium', 'chinese': '铬', 'smiles': '[Cr]'},
    'Cs': {'english': 'Cesium', 'chinese': '铯', 'smiles': '[Cs]'},
    'Cu': {'english': 'Copper', 'chinese': '铜', 'smiles': '[Cu]'},
    'Eu': {'english': 'Europium', 'chinese': '铕', 'smiles': '[Eu]'},
    'Fe': {'english': 'Iron', 'chinese': '铁', 'smiles': '[Fe]'},
    'Ga': {'english': 'Gallium', 'chinese': '镓', 'smiles': '[Ga]'},
    'Ge': {'english': 'Germanium', 'chinese': '锗', 'smiles': '[Ge]'},
    'Hg': {'english': 'Mercury', 'chinese': '汞', 'smiles': '[Hg]'},
    'In': {'english': 'Indium', 'chinese': '铟', 'smiles': '[In]'},
    'Ir': {'english': 'Iridium', 'chinese': '铱', 'smiles': '[Ir]'},
    'K': {'english': 'Potassium', 'chinese': '钾', 'smiles': '[K]'},
    'La': {'english': 'Lanthanum', 'chinese': '镧', 'smiles': '[La]'},
    'Li': {'english': 'Lithium', 'chinese': '锂', 'smiles': '[Li]'},
    'Mg': {'english': 'Magnesium', 'chinese': '镁', 'smiles': '[Mg]'},
    'Mn': {'english': 'Manganese', 'chinese': '锰', 'smiles': '[Mn]'},
    'Mo': {'english': 'Molybdenum', 'chinese': '钼', 'smiles': '[Mo]'},
    'Nb': {'english': 'Niobium', 'chinese': '铌', 'smiles': '[Nb]'},
    'Na': {'english': 'Sodium', 'chinese': '钠', 'smiles': '[Na]'},
    'Ni': {'english': 'Nickel', 'chinese': '镍', 'smiles': '[Ni]'},
    'Os': {'english': 'Osmium', 'chinese': '锇', 'smiles': '[Os]'},
    'Pb': {'english': 'Lead', 'chinese': '铅', 'smiles': '[Pb]'},
    'Pd': {'english': 'Palladium', 'chinese': '钯', 'smiles': '[Pd]'},
    'Pt': {'english': 'Platinum', 'chinese': '铂', 'smiles': '[Pt]'},
    'Rb': {'english': 'Rubidium', 'chinese': '铷', 'smiles': '[Rb]'},
    'Re': {'english': 'Rhenium', 'chinese': '铼', 'smiles': '[Re]'},
    'Rh': {'english': 'Rhodium', 'chinese': '铑', 'smiles': '[Rh]'},
    'Ru': {'english': 'Ruthenium', 'chinese': '钌', 'smiles': '[Ru]'},
    'Sb': {'english': 'Antimony', 'chinese': '锑', 'smiles': '[Sb]'},
    'Sc': {'english': 'Scandium', 'chinese': '钪', 'smiles': '[Sc]'},
    'Se': {'english': 'Selenium', 'chinese': '硒', 'smiles': '[Se]'},
    'Si': {'english': 'Silicon', 'chinese': '硅', 'smiles': '[Si]'},
    'Sn': {'english': 'Tin', 'chinese': '锡', 'smiles': '[Sn]'},
    'Sr': {'english': 'Strontium', 'chinese': '锶', 'smiles': '[Sr]'},
    'Ta': {'english': 'Tantalum', 'chinese': '钽', 'smiles': '[Ta]'},
    'Tc': {'english': 'Technetium', 'chinese': '锝', 'smiles': '[Tc]'},
    'Te': {'english': 'Tellurium', 'chinese': '碲', 'smiles': '[Te]'},
    'Ti': {'english': 'Titanium', 'chinese': '钛', 'smiles': '[Ti]'},
    'Tl': {'english': 'Thallium', 'chinese': '铊', 'smiles': '[Tl]'},
    'U': {'english': 'Uranium', 'chinese': '铀', 'smiles': '[U]'},
    'V': {'english': 'Vanadium', 'chinese': '钒', 'smiles': '[V]'},
    'W': {'english': 'Tungsten', 'chinese': '钨', 'smiles': '[W]'},
    'Y': {'english': 'Yttrium', 'chinese': '钇', 'smiles': '[Y]'},
    'Zn': {'english': 'Zinc', 'chinese': '锌', 'smiles': '[Zn]'},
    'Zr': {'english': 'Zirconium', 'chinese': '锆', 'smiles': '[Zr]'},

    # ===== 共价晶体 (11种) =====
    'C': {'english': 'Diamond', 'chinese': '金刚石', 'smiles': 'C'},
    'BN': {'english': 'Boron nitride', 'chinese': '氮化硼', 'smiles': 'B#N'},
    'SiC': {'english': 'Silicon carbide', 'chinese': '碳化硅', 'smiles': '[Si]#C'},
    'SiO2': {'english': 'Silicon dioxide', 'chinese': '二氧化硅', 'smiles': 'O=[Si]=O'},
    'GaAs': {'english': 'Gallium arsenide', 'chinese': '砷化镓', 'smiles': '[Ga].[As]'},
    'GaN': {'english': 'Gallium nitride', 'chinese': '氮化镓', 'smiles': '[Ga]#N'},
    'GaSb': {'english': 'Gallium antimonide', 'chinese': '锑化镓', 'smiles': '[Ga].[Sb]'},
    'InAs': {'english': 'Indium arsenide', 'chinese': '砷化铟', 'smiles': '[In].[As]'},
    'InP': {'english': 'Indium phosphide', 'chinese': '磷化铟', 'smiles': '[In]#P'},
    'InSb': {'english': 'Indium antimonide', 'chinese': '锑化铟', 'smiles': '[In].[Sb]'},
    'GeO2': {'english': 'Germanium oxide', 'chinese': '二氧化锗', 'smiles': 'O=[Ge]=O'},

    # ===== 离子晶体 =====
    # 银化合物
    'AgNO3': {'english': 'Silver nitrate', 'chinese': '硝酸银', 'smiles': '[Ag+].[O-][N+](=O)O'},
    'Ag2O': {'english': 'Silver oxide', 'chinese': '氧化银', 'smiles': '[Ag+].[Ag+].[O-2]'},
    'Ag2S': {'english': 'Silver sulfide', 'chinese': '硫化银', 'smiles': '[Ag+].[Ag+].[S-2]'},
    'AgBr': {'english': 'Silver bromide', 'chinese': '溴化银', 'smiles': '[Ag+].[Br-]'},
    'AgCl': {'english': 'Silver chloride', 'chinese': '氯化银', 'smiles': '[Ag+].[Cl-]'},
    'AgI': {'english': 'Silver iodide', 'chinese': '碘化银', 'smiles': '[Ag+].[I-]'},
    'Ag2CO3': {'english': 'Silver carbonate', 'chinese': '碳酸银', 'smiles': '[Ag+].[Ag+].[O-]C(=O)[O-]'},
    'Ag2CrO4': {'english': 'Silver chromate', 'chinese': '铬酸银', 'smiles': '[Ag+].[Ag+].[O-]Cr(=O)(=O)[O-]'},
    'Ag2SO4': {'english': 'Silver sulfate', 'chinese': '硫酸银', 'smiles': '[Ag+].[Ag+].[O-]S(=O)(=O)[O-]'},
    'AgBrO3': {'english': 'Silver bromate', 'chinese': '溴酸银', 'smiles': '[Ag+].[O-]Br(=O)=O'},
    'AgClO3': {'english': 'Silver chlorate', 'chinese': '氯酸银', 'smiles': '[Ag+].[O-]Cl(=O)=O'},
    'AgClO4': {'english': 'Silver perchlorate', 'chinese': '高氯酸银', 'smiles': '[Ag+].[O-]Cl(=O)(=O)=O'},
    'AgCN': {'english': 'Silver cyanide', 'chinese': '氰化银', 'smiles': '[Ag+].[C-]#N'},
    'AgF': {'english': 'Silver fluoride', 'chinese': '氟化银', 'smiles': '[Ag+].[F-]'},
    'AgIO3': {'english': 'Silver iodate', 'chinese': '碘酸银', 'smiles': '[Ag+].[O-]I(=O)=O'},

    # 铝化合物
    'Al2O3': {'english': 'Aluminum oxide', 'chinese': '氧化铝', 'smiles': '[Al+3].[Al+3].[O-2].[O-2].[O-2]'},
    'AlPO4': {'english': 'Aluminum phosphate', 'chinese': '磷酸铝', 'smiles': '[Al+3].[O-]P(=O)([O-])O'},
    'Al2S3': {'english': 'Aluminum sulfide', 'chinese': '硫化铝', 'smiles': '[Al+3].[Al+3].[S-2].[S-2].[S-2]'},
    'AlF3': {'english': 'Aluminum fluoride', 'chinese': '氟化铝', 'smiles': '[Al+3].[F-].[F-].[F-]'},
    'AlI3': {'english': 'Aluminum iodide', 'chinese': '碘化铝', 'smiles': '[Al+3].[I-].[I-].[I-]'},

    # 钡化合物
    'BaO': {'english': 'Barium oxide', 'chinese': '氧化钡', 'smiles': '[Ba+2].[O-2]'},
    'BaS': {'english': 'Barium sulfide', 'chinese': '硫化钡', 'smiles': '[Ba+2].[S-2]'},
    'BaSO4': {'english': 'Barium sulfate', 'chinese': '硫酸钡', 'smiles': '[Ba+2].[O-]S(=O)(=O)[O-]'},
    'BaCO3': {'english': 'Barium carbonate', 'chinese': '碳酸钡', 'smiles': '[Ba+2].[O-]C(=O)[O-]'},
    'Ba(OH)2': {'english': 'Barium hydroxide', 'chinese': '氢氧化钡', 'smiles': '[Ba+2].[OH-].[OH-]'},
    'Ba(NO3)2': {'english': 'Barium nitrate', 'chinese': '硝酸钡', 'smiles': '[Ba+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'BaCl2': {'english': 'Barium chloride', 'chinese': '氯化钡', 'smiles': '[Ba+2].[Cl-].[Cl-]'},

    # 铍化合物
    'BeO': {'english': 'Beryllium oxide', 'chinese': '氧化铍', 'smiles': '[Be+2].[O-2]'},
    'Be(OH)2': {'english': 'Beryllium hydroxide', 'chinese': '氢氧化铍', 'smiles': '[Be+2].[OH-].[OH-]'},
    'BeCl2': {'english': 'Beryllium chloride', 'chinese': '氯化铍', 'smiles': '[Be+2].[Cl-].[Cl-]'},
    'BeCO3': {'english': 'Beryllium carbonate', 'chinese': '碳酸铍', 'smiles': '[Be+2].[O-]C(=O)[O-]'},
    'BeS': {'english': 'Beryllium sulfide', 'chinese': '硫化铍', 'smiles': '[Be+2].[S-2]'},
    'BeSO4': {'english': 'Beryllium sulfate', 'chinese': '硫酸铍', 'smiles': '[Be+2].[O-]S(=O)(=O)[O-]'},

    # 铋化合物
    'Bi2O3': {'english': 'Bismuth oxide', 'chinese': '氧化铋', 'smiles': '[Bi+3].[Bi+3].[O-2].[O-2].[O-2]'},
    'Bi(OH)3': {'english': 'Bismuth hydroxide', 'chinese': '氢氧化铋', 'smiles': '[Bi+3].[OH-].[OH-].[OH-]'},
    'Bi2(SO4)3': {'english': 'Bismuth sulfate', 'chinese': '硫酸铋', 'smiles': '[Bi+3].[Bi+3].[O-]S(=O)(=O)[O-].[O-]S(=O)(=O)[O-].[O-]S(=O)(=O)[O-]'},
    'Bi2S3': {'english': 'Bismuth sulfide', 'chinese': '硫化铋', 'smiles': '[Bi+3].[Bi+3].[S-2].[S-2].[S-2]'},

    # 钙化合物
    'CaO': {'english': 'Calcium oxide', 'chinese': '氧化钙', 'smiles': '[Ca+2].[O-2]'},
    'CaCO3': {'english': 'Calcium carbonate', 'chinese': '碳酸钙', 'smiles': '[Ca+2].[O-]C(=O)[O-]'},
    'Ca(OH)2': {'english': 'Calcium hydroxide', 'chinese': '氢氧化钙', 'smiles': '[Ca+2].[OH-].[OH-]'},
    'CaSO4': {'english': 'Calcium sulfate', 'chinese': '硫酸钙', 'smiles': '[Ca+2].[O-]S(=O)(=O)[O-]'},
    'Ca(NO3)2': {'english': 'Calcium nitrate', 'chinese': '硝酸钙', 'smiles': '[Ca+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Ca3(PO4)2': {'english': 'Calcium phosphate', 'chinese': '磷酸钙', 'smiles': '[Ca+2].[Ca+2].[Ca+2].[O-]P(=O)([O-])O.[O-]P(=O)([O-])O'},
    'CaBr2': {'english': 'Calcium bromide', 'chinese': '溴化钙', 'smiles': '[Ca+2].[Br-].[Br-]'},
    'CaC2': {'english': 'Calcium carbide', 'chinese': '碳化钙', 'smiles': '[Ca+2].[C-]#C'},
    'CaC2O4': {'english': 'Calcium oxalate', 'chinese': '草酸钙', 'smiles': '[Ca+2].[O-]C(=O)C(=O)[O-]'},
    'CaCl2': {'english': 'Calcium chloride', 'chinese': '氯化钙', 'smiles': '[Ca+2].[Cl-].[Cl-]'},
    'CaH2': {'english': 'Calcium hydride', 'chinese': '氢化钙', 'smiles': '[Ca+2].[H-].[H-]'},

    # 镉化合物
    'CdO': {'english': 'Cadmium oxide', 'chinese': '氧化镉', 'smiles': '[Cd+2].[O-2]'},
    'CdS': {'english': 'Cadmium sulfide', 'chinese': '硫化镉', 'smiles': '[Cd+2].[S-2]'},
    'CdSO4': {'english': 'Cadmium sulfate', 'chinese': '硫酸镉', 'smiles': '[Cd+2].[O-]S(=O)(=O)[O-]'},
    'CdCl2': {'english': 'Cadmium chloride', 'chinese': '氯化镉', 'smiles': '[Cd+2].[Cl-].[Cl-]'},
    'CdCO3': {'english': 'Cadmium carbonate', 'chinese': '碳酸镉', 'smiles': '[Cd+2].[O-]C(=O)[O-]'},

    # 铈化合物
    'CeO2': {'english': 'Cerium oxide', 'chinese': '二氧化铈', 'smiles': '[Ce+4].[O-2].[O-2]'},
    'Ce2O3': {'english': 'Cerium oxide', 'chinese': '三氧化二铈', 'smiles': '[Ce+3].[Ce+3].[O-2].[O-2].[O-2]'},

    # 钴化合物
    'CoO': {'english': 'Cobalt oxide', 'chinese': '氧化钴', 'smiles': '[Co+2].[O-2]'},
    'CoS': {'english': 'Cobalt sulfide', 'chinese': '硫化钴', 'smiles': '[Co+2].[S-2]'},
    'CoSO4': {'english': 'Cobalt sulfate', 'chinese': '硫酸钴', 'smiles': '[Co+2].[O-]S(=O)(=O)[O-]'},
    'Co(NO3)2': {'english': 'Cobalt nitrate', 'chinese': '硝酸钴', 'smiles': '[Co+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Co(OH)2': {'english': 'Cobalt hydroxide', 'chinese': '氢氧化钴', 'smiles': '[Co+2].[OH-].[OH-]'},
    'Co2S3': {'english': 'Cobalt sulfide', 'chinese': '硫化钴', 'smiles': '[Co+3].[Co+3].[S-2].[S-2].[S-2]'},
    'CoCl2': {'english': 'Cobalt chloride', 'chinese': '氯化钴', 'smiles': '[Co+2].[Cl-].[Cl-]'},

    # 铬化合物
    'Cr2O3': {'english': 'Chromium oxide', 'chinese': '三氧化二铬', 'smiles': '[Cr+3].[Cr+3].[O-2].[O-2].[O-2]'},
    'CrO3': {'english': 'Chromium oxide', 'chinese': '三氧化铬', 'smiles': 'O=[Cr](=O)=O'},

    # 铯化合物
    'Cs2O': {'english': 'Cesium oxide', 'chinese': '氧化铯', 'smiles': '[Cs+].[Cs+].[O-2]'},
    'Cs2CO3': {'english': 'Cesium carbonate', 'chinese': '碳酸铯', 'smiles': '[Cs+].[Cs+].[O-]C(=O)[O-]'},
    'Cs2SO4': {'english': 'Cesium sulfate', 'chinese': '硫酸铯', 'smiles': '[Cs+].[Cs+].[O-]S(=O)(=O)[O-]'},
    'CsClO4': {'english': 'Cesium perchlorate', 'chinese': '高氯酸铯', 'smiles': '[Cs+].[O-]Cl(=O)(=O)=O'},
    'CsH': {'english': 'Cesium hydride', 'chinese': '氢化铯', 'smiles': '[Cs+].[H-]'},
    'CsNO3': {'english': 'Cesium nitrate', 'chinese': '硝酸铯', 'smiles': '[Cs+].[O-][N+](=O)O'},
    'CsO2': {'english': 'Cesium superoxide', 'chinese': '超氧化铯', 'smiles': '[Cs+].[O-]O'},
    'CsOH': {'english': 'Cesium hydroxide', 'chinese': '氢氧化铯', 'smiles': '[Cs+].[OH-]'},

    # 铜化合物
    'CuO': {'english': 'Copper oxide', 'chinese': '氧化铜', 'smiles': '[Cu+2].[O-2]'},
    'Cu2O': {'english': 'Copper oxide', 'chinese': '氧化亚铜', 'smiles': '[Cu+].[Cu+].[O-2]'},
    'CuS': {'english': 'Copper sulfide', 'chinese': '硫化铜', 'smiles': '[Cu+2].[S-2]'},
    'CuSO4': {'english': 'Copper sulfate', 'chinese': '硫酸铜', 'smiles': '[Cu+2].[O-]S(=O)(=O)[O-]'},
    'Cu(NO3)2': {'english': 'Copper nitrate', 'chinese': '硝酸铜', 'smiles': '[Cu+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Cu(OH)2': {'english': 'Copper hydroxide', 'chinese': '氢氧化铜', 'smiles': '[Cu+2].[OH-].[OH-]'},
    'CuBr': {'english': 'Copper bromide', 'chinese': '溴化亚铜', 'smiles': '[Cu+].[Br-]'},
    'CuBr2': {'english': 'Copper bromide', 'chinese': '溴化铜', 'smiles': '[Cu+2].[Br-].[Br-]'},
    'CuCl': {'english': 'Copper chloride', 'chinese': '氯化亚铜', 'smiles': '[Cu+].[Cl-]'},
    'CuCl2': {'english': 'Copper chloride', 'chinese': '氯化铜', 'smiles': '[Cu+2].[Cl-].[Cl-]'},
    'CuCN': {'english': 'Copper cyanide', 'chinese': '氰化亚铜', 'smiles': '[Cu+].[C-]#N'},
    'CuI': {'english': 'Copper iodide', 'chinese': '碘化亚铜', 'smiles': '[Cu+].[I-]'},
    'CuWO4': {'english': 'Copper tungstate', 'chinese': '钨酸铜', 'smiles': '[Cu+2].[O-]W(=O)(=O)[O-]'},

    # 铁化合物
    'FeO': {'english': 'Iron oxide', 'chinese': '氧化亚铁', 'smiles': '[Fe+2].[O-2]'},
    'Fe2O3': {'english': 'Iron oxide', 'chinese': '三氧化二铁', 'smiles': '[Fe+3].[Fe+3].[O-2].[O-2].[O-2]'},
    'Fe3O4': {'english': 'Iron oxide', 'chinese': '四氧化三铁', 'smiles': '[Fe+2].[Fe+3].[Fe+3].[O-2].[O-2].[O-2].[O-2]'},
    'FeS': {'english': 'Iron sulfide', 'chinese': '硫化亚铁', 'smiles': '[Fe+2].[S-2]'},
    'FeS2': {'english': 'Iron disulfide', 'chinese': '二硫化铁', 'smiles': '[Fe+4].[S-2].[S-2]'},
    'FeSO4': {'english': 'Iron sulfate', 'chinese': '硫酸亚铁', 'smiles': '[Fe+2].[O-]S(=O)(=O)[O-]'},
    'FeCl2': {'english': 'Iron chloride', 'chinese': '氯化亚铁', 'smiles': '[Fe+2].[Cl-].[Cl-]'},
    'FeCl3': {'english': 'Iron chloride', 'chinese': '氯化铁', 'smiles': '[Fe+3].[Cl-].[Cl-].[Cl-]'},
    'FeCO3': {'english': 'Iron carbonate', 'chinese': '碳酸亚铁', 'smiles': '[Fe+2].[O-]C(=O)[O-]'},
    'FeCr2O4': {'english': 'Chromium iron oxide', 'chinese': '铬铁矿', 'smiles': '[Fe+2].[Cr+3].[Cr+3].[O-2].[O-2].[O-2].[O-2]'},

    # 镓化合物
    'Ga2O3': {'english': 'Gallium oxide', 'chinese': '氧化镓', 'smiles': '[Ga+3].[Ga+3].[O-2].[O-2].[O-2]'},
    'Ga(OH)3': {'english': 'Gallium hydroxide', 'chinese': '氢氧化镓', 'smiles': '[Ga+3].[OH-].[OH-].[OH-]'},
    'GaCl3': {'english': 'Gallium chloride', 'chinese': '氯化镓', 'smiles': '[Ga+3].[Cl-].[Cl-].[Cl-]'},

    # 汞化合物
    'HgO': {'english': 'Mercury oxide', 'chinese': '氧化汞', 'smiles': '[Hg+2].[O-2]'},
    'HgS': {'english': 'Mercury sulfide', 'chinese': '硫化汞', 'smiles': '[Hg+2].[S-2]'},
    'Hg2Br2': {'english': 'Mercury bromide', 'chinese': '溴化亚汞', 'smiles': '[Hg+2].[Hg+2].[Br-].[Br-]'},
    'Hg2Cl2': {'english': 'Mercury chloride', 'chinese': '氯化亚汞', 'smiles': '[Hg+2].[Hg+2].[Cl-].[Cl-]'},
    'Hg2CO3': {'english': 'Mercury carbonate', 'chinese': '碳酸亚汞', 'smiles': '[Hg+2].[Hg+2].[O-]C(=O)[O-]'},
    'Hg2I2': {'english': 'Mercury iodide', 'chinese': '碘化亚汞', 'smiles': '[Hg+2].[Hg+2].[I-].[I-]'},
    'Hg2SO4': {'english': 'Mercury sulfate', 'chinese': '硫酸亚汞', 'smiles': '[Hg+2].[Hg+2].[O-]S(=O)(=O)[O-]'},
    'HgBr2': {'english': 'Mercury bromide', 'chinese': '溴化汞', 'smiles': '[Hg+2].[Br-].[Br-]'},
    'HgCl2': {'english': 'Mercury chloride', 'chinese': '氯化汞', 'smiles': '[Hg+2].[Cl-].[Cl-]'},
    'HgI2': {'english': 'Mercury iodide', 'chinese': '碘化汞', 'smiles': '[Hg+2].[I-].[I-]'},
    'HgSO4': {'english': 'Mercury sulfate', 'chinese': '硫酸汞', 'smiles': '[Hg+2].[O-]S(=O)(=O)[O-]'},

    # 铟化合物
    'In2O3': {'english': 'Indium oxide', 'chinese': '氧化铟', 'smiles': '[In+3].[In+3].[O-2].[O-2].[O-2]'},
    'InI3': {'english': 'Indium iodide', 'chinese': '三碘化铟', 'smiles': '[In+3].[I-].[I-].[I-]'},

    # 钾化合物
    'K2O': {'english': 'Potassium oxide', 'chinese': '氧化钾', 'smiles': '[K+].[K+].[O-2]'},
    'K2CO3': {'english': 'Potassium carbonate', 'chinese': '碳酸钾', 'smiles': '[K+].[K+].[O-]C(=O)[O-]'},
    'KOH': {'english': 'Potassium hydroxide', 'chinese': '氢氧化钾', 'smiles': '[K+].[OH-]'},
    'KMnO4': {'english': 'Potassium permanganate', 'chinese': '高锰酸钾', 'smiles': '[K+].[O-]Mn(=O)(=O)=O'},
    'KCl': {'english': 'Potassium chloride', 'chinese': '氯化钾', 'smiles': '[K+].[Cl-]'},
    'KI': {'english': 'Potassium iodide', 'chinese': '碘化钾', 'smiles': '[K+].[I-]'},
    'KNO3': {'english': 'Potassium nitrate', 'chinese': '硝酸钾', 'smiles': '[K+].[O-][N+](=O)O'},
    'K2C2O4': {'english': 'Potassium oxalate', 'chinese': '草酸钾', 'smiles': '[K+].[K+].[O-]C(=O)C(=O)[O-]'},
    'K2O2': {'english': 'Potassium peroxide', 'chinese': '过氧化钾', 'smiles': '[K+].[K+].[O-2]'},
    'K2S': {'english': 'Potassium sulfide', 'chinese': '硫化钾', 'smiles': '[K+].[K+].[S-2]'},
    'K2SiF6': {'english': 'Potassium hexafluorosilicate', 'chinese': '氟硅酸钾', 'smiles': '[K+].[K+].F[Si](F)(F)(F)F'},
    'K2SO4': {'english': 'Potassium sulfate', 'chinese': '硫酸钾', 'smiles': '[K+].[K+].[O-]S(=O)(=O)[O-]'},
    'K3PO4': {'english': 'Potassium phosphate', 'chinese': '磷酸钾', 'smiles': '[K+].[K+].[K+].[O-]P(=O)([O-])O'},
    'KBH4': {'english': 'Potassium borohydride', 'chinese': '硼氢化钾', 'smiles': '[K+].B([H])([H])([H])[H]'},
    'KBrO3': {'english': 'Potassium bromate', 'chinese': '溴酸钾', 'smiles': '[K+].[O-]Br(=O)=O'},
    'KBrO4': {'english': 'Potassium perbromate', 'chinese': '高溴酸钾', 'smiles': '[K+].[O-]Br(=O)(=O)=O'},
    'KClO3': {'english': 'Potassium chlorate', 'chinese': '氯酸钾', 'smiles': '[K+].[O-]Cl(=O)=O'},
    'KClO4': {'english': 'Potassium perchlorate', 'chinese': '高氯酸钾', 'smiles': '[K+].[O-]Cl(=O)(=O)=O'},
    'KCN': {'english': 'Potassium cyanide', 'chinese': '氰化钾', 'smiles': '[K+].[C-]#N'},
    'KH': {'english': 'Potassium hydride', 'chinese': '氢化钾', 'smiles': '[K+].[H-]'},
    'KH2PO4': {'english': 'Potassium dihydrogen phosphate', 'chinese': '磷酸二氢钾', 'smiles': '[K+].O=P(O)(O)O'},
    'KHCO3': {'english': 'Potassium hydrogen carbonate', 'chinese': '碳酸氢钾', 'smiles': '[K+].[O-]C(=O)O'},
    'KHF2': {'english': 'Potassium hydrogen fluoride', 'chinese': '氟氢化钾', 'smiles': '[K+].F[F-]'},
    'KIO3': {'english': 'Potassium iodate', 'chinese': '碘酸钾', 'smiles': '[K+].[O-]I(=O)=O'},
    'KIO4': {'english': 'Potassium periodate', 'chinese': '高碘酸钾', 'smiles': '[K+].[O-]I(=O)(=O)=O'},
    'KNO2': {'english': 'Potassium nitrite', 'chinese': '亚硝酸钾', 'smiles': '[K+].[O-][N+]=O'},
    'KO2': {'english': 'Potassium superoxide', 'chinese': '超氧化钾', 'smiles': '[K+].[O-]O'},
    'KSCN': {'english': 'Potassium thiocyanate', 'chinese': '硫氰酸钾', 'smiles': '[K+].S=C=N'},

    # 镧化合物
    'La2O3': {'english': 'Lanthanum oxide', 'chinese': '氧化镧', 'smiles': '[La+3].[La+3].[O-2].[O-2].[O-2]'},
    'LaCl3': {'english': 'Lanthanum chloride', 'chinese': '氯化镧', 'smiles': '[La+3].[Cl-].[Cl-].[Cl-]'},

    # 锂化合物
    'Li2O': {'english': 'Lithium oxide', 'chinese': '氧化锂', 'smiles': '[Li+].[Li+].[O-2]'},
    'Li2CO3': {'english': 'Lithium carbonate', 'chinese': '碳酸锂', 'smiles': '[Li+].[Li+].[O-]C(=O)[O-]'},
    'LiOH': {'english': 'Lithium hydroxide', 'chinese': '氢氧化锂', 'smiles': '[Li+].[OH-]'},
    'Li2SO4': {'english': 'Lithium sulfate', 'chinese': '硫酸锂', 'smiles': '[Li+].[Li+].[O-]S(=O)(=O)[O-]'},
    'Li3PO4': {'english': 'Lithium phosphate', 'chinese': '磷酸锂', 'smiles': '[Li+].[Li+].[Li+].[O-]P(=O)([O-])O'},
    'LiAlH4': {'english': 'Lithium aluminum hydride', 'chinese': '氢化铝锂', 'smiles': '[Li+].[AlH4-]'},
    'LiBH4': {'english': 'Lithium borohydride', 'chinese': '硼氢化锂', 'smiles': '[Li+].B([H])([H])([H])[H]'},
    'LiF': {'english': 'Lithium fluoride', 'chinese': '氟化锂', 'smiles': '[Li+].[F-]'},
    'LiH': {'english': 'Lithium hydride', 'chinese': '氢化锂', 'smiles': '[Li+].[H-]'},
    'LiNO2': {'english': 'Lithium nitrite', 'chinese': '亚硝酸锂', 'smiles': '[Li+].[O-][N+]=O'},
    'LiNO3': {'english': 'Lithium nitrate', 'chinese': '硝酸锂', 'smiles': '[Li+].[O-][N+](=O)O'},

    # 镁化合物
    'MgO': {'english': 'Magnesium oxide', 'chinese': '氧化镁', 'smiles': '[Mg+2].[O-2]'},
    'MgCO3': {'english': 'Magnesium carbonate', 'chinese': '碳酸镁', 'smiles': '[Mg+2].[O-]C(=O)[O-]'},
    'Mg(OH)2': {'english': 'Magnesium hydroxide', 'chinese': '氢氧化镁', 'smiles': '[Mg+2].[OH-].[OH-]'},
    'MgSO4': {'english': 'Magnesium sulfate', 'chinese': '硫酸镁', 'smiles': '[Mg+2].[O-]S(=O)(=O)[O-]'},
    'Mg(NO3)2': {'english': 'Magnesium nitrate', 'chinese': '硝酸镁', 'smiles': '[Mg+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'MgBr2': {'english': 'Magnesium bromide', 'chinese': '溴化镁', 'smiles': '[Mg+2].[Br-].[Br-]'},
    'MgC2O4': {'english': 'Magnesium oxalate', 'chinese': '草酸镁', 'smiles': '[Mg+2].[O-]C(=O)C(=O)[O-]'},
    'MgCl2': {'english': 'Magnesium chloride', 'chinese': '氯化镁', 'smiles': '[Mg+2].[Cl-].[Cl-]'},
    'MgH2': {'english': 'Magnesium hydride', 'chinese': '氢化镁', 'smiles': '[Mg+2].[H-].[H-]'},
    'MgI2': {'english': 'Magnesium iodide', 'chinese': '碘化镁', 'smiles': '[Mg+2].[I-].[I-]'},

    # 锰化合物
    'MnO': {'english': 'Manganese oxide', 'chinese': '氧化锰', 'smiles': '[Mn+2].[O-2]'},
    'MnO2': {'english': 'Manganese oxide', 'chinese': '二氧化锰', 'smiles': 'O=[Mn]=O'},
    'Mn2O3': {'english': 'Manganese oxide', 'chinese': '三氧化二锰', 'smiles': '[Mn+3].[Mn+3].[O-2].[O-2].[O-2]'},
    'Mn3O4': {'english': 'Manganese oxide', 'chinese': '四氧化三锰', 'smiles': '[Mn+2].[Mn+3].[Mn+3].[O-2].[O-2].[O-2].[O-2]'},
    'MnS': {'english': 'Manganese sulfide', 'chinese': '硫化锰', 'smiles': '[Mn+2].[S-2]'},
    'Mn(NO3)2': {'english': 'Manganese nitrate', 'chinese': '硝酸锰', 'smiles': '[Mn+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Mn2SiO4': {'english': 'Manganese orthosilicate', 'chinese': '硅酸锰', 'smiles': '[Mn+2].[Mn+2].[O-]Si([O-])O'},

    # 钼化合物
    'MoO3': {'english': 'Molybdenum oxide', 'chinese': '三氧化钼', 'smiles': 'O=[Mo](=O)=O'},

    # 钠化合物
    'Na2O': {'english': 'Sodium oxide', 'chinese': '氧化钠', 'smiles': '[Na+].[Na+].[O-2]'},
    'Na2O2': {'english': 'Sodium peroxide', 'chinese': '过氧化钠', 'smiles': '[Na+].[Na+].[O-2]'},
    'Na2CO3': {'english': 'Sodium carbonate', 'chinese': '碳酸钠', 'smiles': '[Na+].[Na+].[O-]C(=O)[O-]'},
    'NaCl': {'english': 'Sodium chloride', 'chinese': '氯化钠', 'smiles': '[Na+].[Cl-]'},
    'NaOH': {'english': 'Sodium hydroxide', 'chinese': '氢氧化钠', 'smiles': '[Na+].[OH-]'},
    'NaBr': {'english': 'Sodium bromide', 'chinese': '溴化钠', 'smiles': '[Na+].[Br-]'},
    'NaI': {'english': 'Sodium iodide', 'chinese': '碘化钠', 'smiles': '[Na+].[I-]'},
    'NaNO3': {'english': 'Sodium nitrate', 'chinese': '硝酸钠', 'smiles': '[Na+].[O-][N+](=O)O'},
    'Na2B4O7': {'english': 'Sodium tetraborate', 'chinese': '四硼酸钠', 'smiles': '[Na+].[Na+].O[B]O[B](O)O[B]O[B]O'},
    'Na2C2O4': {'english': 'Sodium oxalate', 'chinese': '草酸钠', 'smiles': '[Na+].[Na+].[O-]C(=O)C(=O)[O-]'},
    'Na2HPO4': {'english': 'Sodium hydrogen phosphate', 'chinese': '磷酸氢二钠', 'smiles': '[Na+].[Na+].O=P(O)([O-])O'},
    'Na2MnO4': {'english': 'Sodium manganate', 'chinese': '锰酸钠', 'smiles': '[Na+].[Na+].[O-]Mn(=O)(=O)[O-]'},
    'Na2SiF6': {'english': 'Sodium hexafluorosilicate', 'chinese': '氟硅酸钠', 'smiles': '[Na+].[Na+].F[Si](F)(F)(F)F'},
    'Na2SiO3': {'english': 'Sodium metasilicate', 'chinese': '硅酸钠', 'smiles': '[Na+].[Na+].[O-]Si([O-])O'},
    'Na2SO3': {'english': 'Sodium sulfite', 'chinese': '亚硫酸钠', 'smiles': '[Na+].[Na+].[O-]S(=O)[O-]'},
    'NaBF4': {'english': 'Sodium tetrafluoroborate', 'chinese': '四氟硼酸钠', 'smiles': '[Na+].B(F)(F)(F)F'},
    'NaBH4': {'english': 'Sodium borohydride', 'chinese': '硼氢化钠', 'smiles': '[Na+].B([H])([H])([H])[H]'},
    'NaCN': {'english': 'Sodium cyanide', 'chinese': '氰化钠', 'smiles': '[Na+].[C-]#N'},
    'NaF': {'english': 'Sodium fluoride', 'chinese': '氟化钠', 'smiles': '[Na+].[F-]'},
    'NaH': {'english': 'Sodium hydride', 'chinese': '氢化钠', 'smiles': '[Na+].[H-]'},
    'NaHCO3': {'english': 'Sodium hydrogen carbonate', 'chinese': '碳酸氢钠', 'smiles': '[Na+].[O-]C(=O)O'},
    'NaHSO4': {'english': 'Sodium hydrogen sulfate', 'chinese': '硫酸氢钠', 'smiles': '[Na+].[O-]S(=O)(=O)O'},
    'NaIO4': {'english': 'Sodium periodate', 'chinese': '高碘酸钠', 'smiles': '[Na+].[O-]I(=O)(=O)=O'},
    'NaN3': {'english': 'Sodium azide', 'chinese': '叠氮化钠', 'smiles': '[Na+].[N-]=[N+]=N'},
    'NaNH2': {'english': 'Sodium amide', 'chinese': '氨基钠', 'smiles': '[Na+].[NH2-]'},
    'NaNO2': {'english': 'Sodium nitrite', 'chinese': '亚硝酸钠', 'smiles': '[Na+].[O-][N+]=O'},
    'NaO2': {'english': 'Sodium superoxide', 'chinese': '超氧化钠', 'smiles': '[Na+].[O-]O'},
    'NaOCN': {'english': 'Sodium cyanate', 'chinese': '氰酸钠', 'smiles': '[Na+].N=C=O'},

    # 铌化合物
    'NbCl5': {'english': 'Niobium chloride', 'chinese': '五氯化铌', 'smiles': 'Cl[Nb](Cl)(Cl)(Cl)Cl'},

    # 铵化合物
    'NH4Cl': {'english': 'Ammonium chloride', 'chinese': '氯化铵', 'smiles': '[NH4+].[Cl-]'},
    'NH4Br': {'english': 'Ammonium bromide', 'chinese': '溴化铵', 'smiles': '[NH4+].[Br-]'},
    'NH4I': {'english': 'Ammonium iodide', 'chinese': '碘化铵', 'smiles': '[NH4+].[I-]'},
    'NH4F': {'english': 'Ammonium fluoride', 'chinese': '氟化铵', 'smiles': '[NH4+].[F-]'},
    'NH4NO2': {'english': 'Ammonium nitrite', 'chinese': '亚硝酸铵', 'smiles': '[NH4+].[O-][N+]=O'},
    'NH4NO3': {'english': 'Ammonium nitrate', 'chinese': '硝酸铵', 'smiles': '[NH4+].[O-][N+](=O)O'},

    # 镍化合物
    'NiO': {'english': 'Nickel oxide', 'chinese': '氧化镍', 'smiles': '[Ni+2].[O-2]'},
    'NiS': {'english': 'Nickel sulfide', 'chinese': '硫化镍', 'smiles': '[Ni+2].[S-2]'},
    'Ni(NO3)2': {'english': 'Nickel nitrate', 'chinese': '硝酸镍', 'smiles': '[Ni+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Ni(OH)2': {'english': 'Nickel hydroxide', 'chinese': '氢氧化镍', 'smiles': '[Ni+2].[OH-].[OH-]'},
    'NiCl2': {'english': 'Nickel chloride', 'chinese': '氯化镍', 'smiles': '[Ni+2].[Cl-].[Cl-]'},
    'NiCO3': {'english': 'Nickel carbonate', 'chinese': '碳酸镍', 'smiles': '[Ni+2].[O-]C(=O)[O-]'},
    'Ni2O3': {'english': 'Nickel oxide', 'chinese': '三氧化二镍', 'smiles': '[Ni+3].[Ni+3].[O-2].[O-2].[O-2]'},
    'NiSO4': {'english': 'Nickel sulfate', 'chinese': '硫酸镍', 'smiles': '[Ni+2].[O-]S(=O)(=O)[O-]'},

    # 铅化合物
    'PbO': {'english': 'Lead oxide', 'chinese': '氧化铅', 'smiles': '[Pb+2].[O-2]'},
    'PbO2': {'english': 'Lead oxide', 'chinese': '二氧化铅', 'smiles': 'O=[Pb]=O'},
    'Pb3O4': {'english': 'Lead oxide', 'chinese': '四氧化三铅', 'smiles': '[Pb+2].[Pb+3].[Pb+3].[O-2].[O-2].[O-2].[O-2]'},
    'PbS': {'english': 'Lead sulfide', 'chinese': '硫化铅', 'smiles': '[Pb+2].[S-2]'},
    'PbSO4': {'english': 'Lead sulfate', 'chinese': '硫酸铅', 'smiles': '[Pb+2].[O-]S(=O)(=O)[O-]'},
    'Pb(NO3)2': {'english': 'Lead nitrate', 'chinese': '硝酸铅', 'smiles': '[Pb+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'PbC2O4': {'english': 'Lead oxalate', 'chinese': '草酸铅', 'smiles': '[Pb+2].[O-]C(=O)C(=O)[O-]'},
    'PbCO3': {'english': 'Lead carbonate', 'chinese': '碳酸铅', 'smiles': '[Pb+2].[O-]C(=O)[O-]'},
    'PbCl2': {'english': 'Lead chloride', 'chinese': '氯化铅', 'smiles': '[Pb+2].[Cl-].[Cl-]'},
    'PbCl4': {'english': 'Lead chloride', 'chinese': '四氯化铅', 'smiles': 'Cl[Pb](Cl)(Cl)Cl'},
    'PbI2': {'english': 'Lead iodide', 'chinese': '碘化铅', 'smiles': '[Pb+2].[I-].[I-]'},
    'PbSe': {'english': 'Lead selenide', 'chinese': '硒化铅', 'smiles': '[Pb+2].[Se-2]'},
    'PbTe': {'english': 'Lead telluride', 'chinese': '碲化铅', 'smiles': '[Pb+2].[Te-2]'},

    # 钯化合物
    'PdO': {'english': 'Palladium oxide', 'chinese': '氧化钯', 'smiles': '[Pd+2].[O-2]'},
    'PdCl2': {'english': 'Palladium chloride', 'chinese': '氯化钯', 'smiles': '[Pd+2].[Cl-].[Cl-]'},
    'PdSO4': {'english': 'Palladium sulfate', 'chinese': '硫酸钯', 'smiles': '[Pd+2].[O-]S(=O)(=O)[O-]'},

    # 铂化合物
    'PtCl4': {'english': 'Platinum chloride', 'chinese': '四氯化铂', 'smiles': 'Cl[Pt](Cl)(Cl)Cl'},

    # 铷化合物
    'Rb2O': {'english': 'Rubidium oxide', 'chinese': '氧化铷', 'smiles': '[Rb+].[Rb+].[O-2]'},
    'Rb2CO3': {'english': 'Rubidium carbonate', 'chinese': '碳酸铷', 'smiles': '[Rb+].[Rb+].[O-]C(=O)[O-]'},
    'Rb2O2': {'english': 'Rubidium peroxide', 'chinese': '过氧化铷', 'smiles': '[Rb+].[Rb+].[O-2]'},
    'RbCl': {'english': 'Rubidium chloride', 'chinese': '氯化铷', 'smiles': '[Rb+].[Cl-]'},
    'RbClO4': {'english': 'Rubidium perchlorate', 'chinese': '高氯酸铷', 'smiles': '[Rb+].[O-]Cl(=O)(=O)=O'},
    'RbNO3': {'english': 'Rubidium nitrate', 'chinese': '硝酸铷', 'smiles': '[Rb+].[O-][N+](=O)O'},
    'RbOH': {'english': 'Rubidium hydroxide', 'chinese': '氢氧化铷', 'smiles': '[Rb+].[OH-]'},

    # 铼化合物
    'Re2O7': {'english': 'Rhenium oxide', 'chinese': '七氧化二铼', 'smiles': 'O=[Re](=O)(=O)O[Re](=O)(=O)=O'},

    # 铑化合物
    'Rh2O3': {'english': 'Rhodium oxide', 'chinese': '氧化铑', 'smiles': '[Rh+3].[Rh+3].[O-2].[O-2].[O-2]'},

    # 钌化合物
    'RuO2': {'english': 'Ruthenium oxide', 'chinese': '二氧化钌', 'smiles': 'O=[Ru]=O'},
    'RuO4': {'english': 'Ruthenium oxide', 'chinese': '四氧化钌', 'smiles': 'O=[Ru](=O)(=O)=O'},
    'RuCl3': {'english': 'Ruthenium chloride', 'chinese': '三氯化钌', 'smiles': 'Cl[Ru](Cl)Cl'},

    # 锑化合物
    'Sb2O5': {'english': 'Antimony oxide', 'chinese': '五氧化二锑', 'smiles': 'O=[Sb](=O)O[Sb](=O)=O'},

    # 钪化合物
    'Sc2O3': {'english': 'Scandium oxide', 'chinese': '氧化钪', 'smiles': '[Sc+3].[Sc+3].[O-2].[O-2].[O-2]'},

    # 硒化合物
    'SeO2': {'english': 'Selenium dioxide', 'chinese': '二氧化硒', 'smiles': 'O=[Se]=O'},

    # 锡化合物
    'SnO': {'english': 'Tin oxide', 'chinese': '氧化亚锡', 'smiles': '[Sn+2].[O-2]'},
    'SnO2': {'english': 'Tin oxide', 'chinese': '二氧化锡', 'smiles': 'O=[Sn]=O'},
    'SnS': {'english': 'Tin sulfide', 'chinese': '硫化亚锡', 'smiles': '[Sn+2].[S-2]'},
    'Sn(OH)2': {'english': 'Tin hydroxide', 'chinese': '氢氧化亚锡', 'smiles': '[Sn+2].[OH-].[OH-]'},
    'Sn(NO3)2': {'english': 'Tin nitrate', 'chinese': '硝酸亚锡', 'smiles': '[Sn+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'SnCO3': {'english': 'Tin carbonate', 'chinese': '碳酸亚锡', 'smiles': '[Sn+2].[O-]C(=O)[O-]'},
    'SnS2': {'english': 'Tin sulfide', 'chinese': '二硫化锡', 'smiles': 'S=[Sn]=S'},

    # 锶化合物
    'SrO': {'english': 'Strontium oxide', 'chinese': '氧化锶', 'smiles': '[Sr+2].[O-2]'},
    'SrS': {'english': 'Strontium sulfide', 'chinese': '硫化锶', 'smiles': '[Sr+2].[S-2]'},
    'SrSO4': {'english': 'Strontium sulfate', 'chinese': '硫酸锶', 'smiles': '[Sr+2].[O-]S(=O)(=O)[O-]'},
    'Sr(OH)2': {'english': 'Strontium hydroxide', 'chinese': '氢氧化锶', 'smiles': '[Sr+2].[OH-].[OH-]'},
    'Sr(NO3)2': {'english': 'Strontium nitrate', 'chinese': '硝酸锶', 'smiles': '[Sr+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'SrCl2': {'english': 'Strontium chloride', 'chinese': '氯化锶', 'smiles': '[Sr+2].[Cl-].[Cl-]'},
    'SrCO3': {'english': 'Strontium carbonate', 'chinese': '碳酸锶', 'smiles': '[Sr+2].[O-]C(=O)[O-]'},
    'SrH2': {'english': 'Strontium hydride', 'chinese': '氢化锶', 'smiles': '[Sr+2].[H-].[H-]'},

    # 钛化合物
    'TiO2': {'english': 'Titanium oxide', 'chinese': '二氧化钛', 'smiles': 'O=[Ti]=O'},
    'TiBr3': {'english': 'Titanium bromide', 'chinese': '三溴化钛', 'smiles': 'Br[Ti](Br)Br'},
    'TiCl3': {'english': 'Titanium chloride', 'chinese': '三氯化钛', 'smiles': 'Cl[Ti](Cl)Cl'},
    'TiF4': {'english': 'Titanium fluoride', 'chinese': '四氟化钛', 'smiles': 'F[Ti](F)(F)F'},
    'TiCl4': {'english': 'Titanium chloride', 'chinese': '四氯化钛', 'smiles': 'Cl[Ti](Cl)(Cl)Cl'},

    # 铊化合物
    'Tl2O': {'english': 'Thallium oxide', 'chinese': '氧化亚铊', 'smiles': '[Tl+].[Tl+].[O-2]'},
    'TlOH': {'english': 'Thallium hydroxide', 'chinese': '氢氧化亚铊', 'smiles': '[Tl+].[OH-]'},
    'Tl2S': {'english': 'Thallium sulfide', 'chinese': '硫化亚铊', 'smiles': '[Tl+].[Tl+].[S-2]'},
    'Tl2SO4': {'english': 'Thallium sulfate', 'chinese': '硫酸亚铊', 'smiles': '[Tl+].[Tl+].[O-]S(=O)(=O)[O-]'},
    'TlBr': {'english': 'Thallium bromide', 'chinese': '溴化铊', 'smiles': '[Tl+].[Br-]'},
    'TlCl': {'english': 'Thallium chloride', 'chinese': '氯化铊', 'smiles': '[Tl+].[Cl-]'},
    'TlCl3': {'english': 'Thallium chloride', 'chinese': '三氯化铊', 'smiles': 'Cl[Tl](Cl)Cl'},
    'Tl2CO3': {'english': 'Thallium carbonate', 'chinese': '碳酸铊', 'smiles': '[Tl+].[Tl+].[O-]C(=O)[O-]'},
    'TlF': {'english': 'Thallium fluoride', 'chinese': '氟化铊', 'smiles': '[Tl+].[F-]'},
    'TlI': {'english': 'Thallium iodide', 'chinese': '碘化铊', 'smiles': '[Tl+].[I-]'},

    # 铀化合物
    'UO3': {'english': 'Uranium oxide', 'chinese': '三氧化铀', 'smiles': 'O=[U](=O)=O'},

    # 钒化合物
    'V2O5': {'english': 'Vanadium oxide', 'chinese': '五氧化二钒', 'smiles': 'O=[V](=O)O[V](=O)=O'},
    'V2O3': {'english': 'Vanadium oxide', 'chinese': '三氧化二钒', 'smiles': '[V+3].[V+3].[O-2].[O-2].[O-2]'},
    'VCl3': {'english': 'Vanadium chloride', 'chinese': '三氯化钒', 'smiles': 'Cl[V](Cl)Cl'},
    'VCl4': {'english': 'Vanadium chloride', 'chinese': '四氯化钒', 'smiles': 'Cl[V](Cl)(Cl)Cl'},

    # 钨化合物
    'WO3': {'english': 'Tungsten oxide', 'chinese': '三氧化钨', 'smiles': 'O=[W](=O)=O'},

    # 钇化合物
    'Y2O3': {'english': 'Yttrium oxide', 'chinese': '氧化钇', 'smiles': '[Y+3].[Y+3].[O-2].[O-2].[O-2]'},

    # 锌化合物
    'ZnO': {'english': 'Zinc oxide', 'chinese': '氧化锌', 'smiles': '[Zn+2].[O-2]'},
    'ZnS': {'english': 'Zinc sulfide', 'chinese': '硫化锌', 'smiles': '[Zn+2].[S-2]'},
    'ZnSO4': {'english': 'Zinc sulfate', 'chinese': '硫酸锌', 'smiles': '[Zn+2].[O-]S(=O)(=O)[O-]'},
    'Zn(NO3)2': {'english': 'Zinc nitrate', 'chinese': '硝酸锌', 'smiles': '[Zn+2].[O-][N+](=O)O.[O-][N+](=O)O'},
    'Zn(OH)2': {'english': 'Zinc hydroxide', 'chinese': '氢氧化锌', 'smiles': '[Zn+2].[OH-].[OH-]'},
    'ZnCl2': {'english': 'Zinc chloride', 'chinese': '氯化锌', 'smiles': '[Zn+2].[Cl-].[Cl-]'},
    'ZnCO3': {'english': 'Zinc carbonate', 'chinese': '碳酸锌', 'smiles': '[Zn+2].[O-]C(=O)[O-]'},
    'ZnF2': {'english': 'Zinc fluoride', 'chinese': '氟化锌', 'smiles': '[Zn+2].[F-].[F-]'},

    # 锆化合物
    'ZrO2': {'english': 'Zirconium oxide', 'chinese': '二氧化锆', 'smiles': 'O=[Zr]=O'},
    'ZrCl2': {'english': 'Zirconium chloride', 'chinese': '二氯化锆', 'smiles': '[Zr+2].[Cl-].[Cl-]'},
    'ZrCl4': {'english': 'Zirconium chloride', 'chinese': '四氯化锆', 'smiles': 'Cl[Zr](Cl)(Cl)Cl'},
    'ZrF4': {'english': 'Zirconium fluoride', 'chinese': '四氟化锆', 'smiles': 'F[Zr](F)(F)F'},

    # ===== 分子晶体 =====
    # 气体单质
    'H2': {'english': 'Hydrogen', 'chinese': '氢气', 'smiles': '[H][H]'},
    'N2': {'english': 'Nitrogen', 'chinese': '氮气', 'smiles': 'N#N'},
    'O2': {'english': 'Oxygen', 'chinese': '氧气', 'smiles': 'O=O'},
    'F2': {'english': 'Fluorine', 'chinese': '氟气', 'smiles': 'F-F'},
    'Cl2': {'english': 'Chlorine', 'chinese': '氯气', 'smiles': 'Cl-Cl'},
    'Br2': {'english': 'Bromine', 'chinese': '溴', 'smiles': 'Br-Br'},
    'I2': {'english': 'Iodine', 'chinese': '碘', 'smiles': 'I-I'},
    'P4': {'english': 'Phosphorus', 'chinese': '白磷', 'smiles': 'P1P1P1P1'},

    # 稀有气体
    'Ar': {'english': 'Argon', 'chinese': '氩气', 'smiles': '[Ar]'},
    'He': {'english': 'Helium', 'chinese': '氦气', 'smiles': '[He]'},
    'Ne': {'english': 'Neon', 'chinese': '氖气', 'smiles': '[Ne]'},
    'Kr': {'english': 'Krypton', 'chinese': '氪气', 'smiles': '[Kr]'},
    'Xe': {'english': 'Xenon', 'chinese': '氙气', 'smiles': '[Xe]'},
    'Rn': {'english': 'Radon', 'chinese': '氡气', 'smiles': '[Rn]'},

    # 氧化物
    'CO': {'english': 'Carbon monoxide', 'chinese': '一氧化碳', 'smiles': 'C#O'},
    'CO2': {'english': 'Carbon dioxide', 'chinese': '二氧化碳', 'smiles': 'O=C=O'},
    'CS2': {'english': 'Carbon disulfide', 'chinese': '二硫化碳', 'smiles': 'S=C=S'},
    'SO2': {'english': 'Sulfur dioxide', 'chinese': '二氧化硫', 'smiles': 'O=S=O'},
    'SO3': {'english': 'Sulfur trioxide', 'chinese': '三氧化硫', 'smiles': 'O=S(=O)=O'},
    'NO': {'english': 'Nitric oxide', 'chinese': '一氧化氮', 'smiles': '[N]=O'},
    'NO2': {'english': 'Nitrogen dioxide', 'chinese': '二氧化氮', 'smiles': 'O=[N](=O)O'},
    'N2O': {'english': 'Nitrous oxide', 'chinese': '一氧化二氮', 'smiles': 'N#NO'},
    'N2O3': {'english': 'Nitrogen trioxide', 'chinese': '三氧化二氮', 'smiles': 'O=N-N(=O)=O'},
    'N2O4': {'english': 'Nitrogen tetroxide', 'chinese': '四氧化二氮', 'smiles': 'O=[N+](O)[O-]'},
    'N2O5': {'english': 'Nitrogen pentoxide', 'chinese': '五氧化二氮', 'smiles': 'O=[N+](O)[O-].[O-][N+](=O)O'},

    # 氢化物
    'H2O': {'english': 'Water', 'chinese': '水', 'smiles': 'O'},
    'H2O2': {'english': 'Hydrogen peroxide', 'chinese': '过氧化氢', 'smiles': 'OO'},
    'H2S': {'english': 'Hydrogen sulfide', 'chinese': '硫化氢', 'smiles': 'S'},
    'H2Se': {'english': 'Hydrogen selenide', 'chinese': '硒化氢', 'smiles': '[Se]'},
    'H2Te': {'english': 'Hydrogen telluride', 'chinese': '碲化氢', 'smiles': '[Te]'},
    'NH3': {'english': 'Ammonia', 'chinese': '氨气', 'smiles': 'N'},
    'N2H4': {'english': 'Hydrazine', 'chinese': '肼', 'smiles': 'NN'},

    # 卤化氢
    'HCl': {'english': 'Hydrogen chloride', 'chinese': '氯化氢', 'smiles': 'Cl'},
    'HBr': {'english': 'Hydrogen bromide', 'chinese': '溴化氢', 'smiles': 'Br'},
    'HI': {'english': 'Hydrogen iodide', 'chinese': '碘化氢', 'smiles': 'I'},
    'HF': {'english': 'Hydrogen fluoride', 'chinese': '氟化氢', 'smiles': 'F'},

    # 其他简单分子
    'HCN': {'english': 'Hydrogen cyanide', 'chinese': '氰化氢', 'smiles': 'C#N'},
    'H2SO4': {'english': 'Sulfuric acid', 'chinese': '硫酸', 'smiles': 'O=S(=O)(O)O'},
    'HNO3': {'english': 'Nitric acid', 'chinese': '硝酸', 'smiles': 'O=[N+]([O-])O'},
    'HNO2': {'english': 'Nitrous acid', 'chinese': '亚硝酸', 'smiles': 'O=NO'},
    'H3PO4': {'english': 'Phosphoric acid', 'chinese': '磷酸', 'smiles': 'O=P(O)(O)O'},
    'H3PO3': {'english': 'Phosphonic acid', 'chinese': '亚磷酸', 'smiles': 'O=P(O)O'},
    'H3BO3': {'english': 'Boric acid', 'chinese': '硼酸', 'smiles': 'B(O)(O)O'},
    'H2SeO4': {'english': 'Selenic acid', 'chinese': '硒酸', 'smiles': 'O=[Se](=O)(O)O'},
    'H2SiO3': {'english': 'Metasilicic acid', 'chinese': '硅酸', 'smiles': 'O=[Si](O)O'},
    'H3AsO4': {'english': 'Arsenic acid', 'chinese': '砷酸', 'smiles': 'O=[As](O)(O)O'},
    'H3PO2': {'english': 'Phosphinic acid', 'chinese': '次磷酸', 'smiles': 'O=PO'},
    'HClO': {'english': 'Hypochlorous acid', 'chinese': '次氯酸', 'smiles': 'OCl'},
    'HClO4': {'english': 'Perchloric acid', 'chinese': '高氯酸', 'smiles': 'O=Cl(=O)(=O)=O'},
    'HN3': {'english': 'Hydrazoic acid', 'chinese': '叠氮酸', 'smiles': '[N-]=[N+]=N'},
    'HNCO': {'english': 'Isocyanic acid', 'chinese': '异氰酸', 'smiles': 'N=C=O'},
    'ClO2': {'english': 'Chlorine dioxide', 'chinese': '二氧化氯', 'smiles': 'O=[Cl](=O)O'},
    'Cl2O': {'english': 'Chlorine monoxide', 'chinese': '一氧化二氯', 'smiles': 'O=ClO'},

    # 硼化合物
    'BF3': {'english': 'Boron trifluoride', 'chinese': '三氟化硼', 'smiles': 'B(F)(F)F'},
    'BCl3': {'english': 'Boron trichloride', 'chinese': '三氯化硼', 'smiles': 'B(Cl)(Cl)Cl'},
    'BBr3': {'english': 'Boron tribromide', 'chinese': '三溴化硼', 'smiles': 'B(Br)(Br)Br'},
    'B2O3': {'english': 'Boron oxide', 'chinese': '氧化硼', 'smiles': 'O=[B]O[B]=O'},

    # 碳化合物
    'CCl4': {'english': 'Tetrachloromethane', 'chinese': '四氯化碳', 'smiles': 'C(Cl)(Cl)(Cl)Cl'},
    'CBr4': {'english': 'Tetrabromomethane', 'chinese': '四溴化碳', 'smiles': 'C(Br)(Br)(Br)Br'},
    'CF4': {'english': 'Tetrafluoromethane', 'chinese': '四氟化碳', 'smiles': 'C(F)(F)(F)F'},
    'COCl2': {'english': 'Carbonyl chloride', 'chinese': '碳酰氯', 'smiles': 'O=C(Cl)Cl'},
    'CH3OH': {'english': 'Methanol', 'chinese': '甲醇', 'smiles': 'CO'},
    'CH3OCH3': {'english': 'Dimethyl ether', 'chinese': '二甲醚', 'smiles': 'COC'},
    'CH3NH2': {'english': 'Methylamine', 'chinese': '甲胺', 'smiles': 'CN'},
    'HCOOH': {'english': 'Formic acid', 'chinese': '甲酸', 'smiles': 'C(=O)O'},
    'HCHO': {'english': 'Formaldehyde', 'chinese': '甲醛', 'smiles': 'C=O'},

    # 硅化合物
    'SiCl4': {'english': 'Tetrachlorosilane', 'chinese': '四氯化硅', 'smiles': 'Cl[Si](Cl)(Cl)Cl'},
    'SiF4': {'english': 'Tetrafluorosilane', 'chinese': '四氟化硅', 'smiles': 'F[Si](F)(F)F'},
    'SiH4': {'english': 'Silane', 'chinese': '硅烷', 'smiles': '[SiH4]'},

    # 磷化合物
    'PCl3': {'english': 'Phosphorus trichloride', 'chinese': '三氯化磷', 'smiles': 'P(Cl)(Cl)Cl'},
    'PCl5': {'english': 'Phosphorus pentachloride', 'chinese': '五氯化磷', 'smiles': 'P(Cl)(Cl)(Cl)(Cl)Cl'},
    'PF5': {'english': 'Phosphorus pentafluoride', 'chinese': '五氟化磷', 'smiles': 'P(F)(F)(F)(F)F'},
    'PH3': {'english': 'Phosphine', 'chinese': '磷化氢', 'smiles': 'P'},

    # 硫化合物
    'SF4': {'english': 'Sulfur tetrafluoride', 'chinese': '四氟化硫', 'smiles': 'S(F)(F)(F)F'},
    'SF6': {'english': 'Sulfur hexafluoride', 'chinese': '六氟化硫', 'smiles': 'S(F)(F)(F)(F)(F)F'},
    'SeF6': {'english': 'Selenium hexafluoride', 'chinese': '六氟化硒', 'smiles': '[Se](F)(F)(F)(F)(F)F'},
    'SO2Cl2': {'english': 'Sulfuryl chloride', 'chinese': '磺酰氯', 'smiles': 'S(=O)(=O)(Cl)Cl'},
    'SCl2': {'english': 'Sulfur dichloride', 'chinese': '二氯化硫', 'smiles': 'S(Cl)Cl'},
    'S2Cl2': {'english': 'Sulfur chloride', 'chinese': '一氯化硫', 'smiles': 'ClSSCl'},
    'OF2': {'english': 'Fluorine monoxide', 'chinese': '一氧化二氟', 'smiles': 'O-F'},
    'O2F2': {'english': 'Difluorine dioxide', 'chinese': '二氧化二氟', 'smiles': 'O-OFF'},

    # 铝化合物
    'Al2Cl6': {'english': 'Aluminum hexachloride', 'chinese': '六氯化二铝', 'smiles': 'Cl[Al](Cl)(Cl)Cl[Al](Cl)(Cl)Cl'},

    # 其他金属卤化物
    'PbCl2': {'english': 'Lead chloride', 'chinese': '氯化铅', 'smiles': '[Pb+2].[Cl-].[Cl-]'},
    'PbCl4': {'english': 'Lead chloride', 'chinese': '四氯化铅', 'smiles': 'Cl[Pb](Cl)(Cl)Cl'},
    'PbI2': {'english': 'Lead iodide', 'chinese': '碘化铅', 'smiles': '[Pb+2].[I-].[I-]'},
    'PbSe': {'english': 'Lead selenide', 'chinese': '硒化铅', 'smiles': '[Pb+2].[Se-2]'},
    'PbTe': {'english': 'Lead telluride', 'chinese': '碲化铅', 'smiles': '[Pb+2].[Te-2]'},

    # 碘化合物
    'IF': {'english': 'Iodine fluoride', 'chinese': '一氟化碘', 'smiles': 'IF'},
    'IF5': {'english': 'Iodine pentafluoride', 'chinese': '五氟化碘', 'smiles': 'F[I](F)(F)(F)F'},

    # 氙化合物
    'XeF4': {'english': 'Xenon tetrafluoride', 'chinese': '四氟化氙', 'smiles': 'F[Xe](F)(F)F'},

    # 锇化合物
    'OsF6': {'english': 'Osmium fluoride', 'chinese': '六氟化锇', 'smiles': 'F[Os](F)(F)(F)(F)F'},
    'OsO4': {'english': 'Osmium oxide', 'chinese': '四氧化锇', 'smiles': 'O=[Os](=O)(=O)=O'},

    # 砷化合物
    'AsH3': {'english': 'Arsine', 'chinese': '砷化氢', 'smiles': 'As'},

    # 锗化合物
    'GeH4': {'english': 'Germane', 'chinese': '锗烷', 'smiles': '[GeH4]'},
}

# 定义每个化学式属于哪种晶体类型
CRYSTAL_TYPE_MAPPING = {
    # 金属晶体
    'Ag': 'metallic', 'Al': 'metallic', 'As': 'metallic', 'Au': 'metallic',
    'Ba': 'metallic', 'Be': 'metallic', 'Bi': 'metallic', 'Ca': 'metallic',
    'Cd': 'metallic', 'Ce': 'metallic', 'Co': 'metallic', 'Cr': 'metallic',
    'Cs': 'metallic', 'Cu': 'metallic', 'Eu': 'metallic', 'Fe': 'metallic',
    'Ga': 'metallic', 'Ge': 'metallic', 'Hg': 'metallic', 'In': 'metallic',
    'Ir': 'metallic', 'K': 'metallic', 'La': 'metallic', 'Li': 'metallic',
    'Mg': 'metallic', 'Mn': 'metallic', 'Mo': 'metallic', 'Nb': 'metallic',
    'Na': 'metallic', 'Ni': 'metallic', 'Os': 'metallic', 'Pb': 'metallic',
    'Pd': 'metallic', 'Pt': 'metallic', 'Rb': 'metallic', 'Re': 'metallic',
    'Rh': 'metallic', 'Ru': 'metallic', 'Sb': 'metallic', 'Sc': 'metallic',
    'Se': 'metallic', 'Si': 'metallic', 'Sn': 'metallic', 'Sr': 'metallic',
    'Ta': 'metallic', 'Tc': 'metallic', 'Te': 'metallic', 'Ti': 'metallic',
    'Tl': 'metallic', 'U': 'metallic', 'V': 'metallic', 'W': 'metallic',
    'Y': 'metallic', 'Zn': 'metallic', 'Zr': 'metallic',

    # 共价晶体
    'C': 'covalent', 'BN': 'covalent', 'SiC': 'covalent', 'SiO2': 'covalent',
    'GaAs': 'covalent', 'GaN': 'covalent', 'GaSb': 'covalent', 'InAs': 'covalent',
    'InP': 'covalent', 'InSb': 'covalent', 'GeO2': 'covalent',

    # 分子晶体
    'H2': 'molecular', 'N2': 'molecular', 'O2': 'molecular', 'F2': 'molecular',
    'Cl2': 'molecular', 'Br2': 'molecular', 'I2': 'molecular', 'P4': 'molecular',
    'Ar': 'molecular', 'He': 'molecular', 'Ne': 'molecular', 'Kr': 'molecular',
    'Xe': 'molecular', 'Rn': 'molecular', 'CO': 'molecular', 'CO2': 'molecular',
    'CS2': 'molecular', 'SO2': 'molecular', 'SO3': 'molecular', 'NO': 'molecular',
    'NO2': 'molecular', 'N2O': 'molecular', 'N2O3': 'molecular', 'N2O4': 'molecular',
    'N2O5': 'molecular', 'H2O': 'molecular', 'H2O2': 'molecular', 'H2S': 'molecular',
    'H2Se': 'molecular', 'H2Te': 'molecular', 'NH3': 'molecular', 'N2H4': 'molecular',
    'HCl': 'molecular', 'HBr': 'molecular', 'HI': 'molecular', 'HF': 'molecular',
    'HCN': 'molecular', 'H2SO4': 'molecular', 'HNO3': 'molecular', 'HNO2': 'molecular',
    'H3PO4': 'molecular', 'H3PO3': 'molecular', 'H3BO3': 'molecular',
    'H2SeO4': 'molecular', 'H2SiO3': 'molecular', 'H3AsO4': 'molecular',
    'H3PO2': 'molecular', 'HClO': 'molecular', 'HClO4': 'molecular',
    'HN3': 'molecular', 'HNCO': 'molecular', 'ClO2': 'molecular', 'Cl2O': 'molecular',
    'BF3': 'molecular', 'BCl3': 'molecular', 'BBr3': 'molecular', 'B2O3': 'molecular',
    'CCl4': 'molecular', 'CBr4': 'molecular', 'CF4': 'molecular', 'COCl2': 'molecular',
    'CH3OH': 'molecular', 'CH3OCH3': 'molecular', 'CH3NH2': 'molecular',
    'HCOOH': 'molecular', 'HCHO': 'molecular', 'SiCl4': 'molecular',
    'SiF4': 'molecular', 'SiH4': 'molecular', 'PCl3': 'molecular', 'PCl5': 'molecular',
    'PF5': 'molecular', 'PH3': 'molecular', 'SF4': 'molecular', 'SF6': 'molecular',
    'SeF6': 'molecular', 'SO2Cl2': 'molecular', 'SCl2': 'molecular', 'S2Cl2': 'molecular',
    'OF2': 'molecular', 'O2F2': 'molecular', 'Al2Cl6': 'molecular', 'IF': 'molecular',
    'IF5': 'molecular', 'XeF4': 'molecular', 'OsF6': 'molecular', 'OsO4': 'molecular',
    'AsH3': 'molecular', 'GeH4': 'molecular',
}

def generate_complete_mapping(output_path):
    """生成完整的name_mapping.json文件"""

    # 初始化crystals数据结构
    crystals_data = {
        "metallic": {},
        "covalent": {},
        "ionic": {},
        "molecular": {}
    }

    # 遍历所有化学物质
    for formula, data in COMPLETE_CHEMICAL_DATA.items():
        smiles = data['smiles']
        english = data['english']
        chinese = data['chinese']

        # 确定晶体类型
        crystal_type = CRYSTAL_TYPE_MAPPING.get(formula, 'ionic')

        # 添加所有名称映射
        crystals_data[crystal_type][formula] = smiles
        if english:
            crystals_data[crystal_type][english] = smiles
        if chinese:
            crystals_data[crystal_type][chinese] = smiles

    # 读取原有的name_mapping.json
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            name_mapping = json.load(f)
    except:
        name_mapping = {
            "_metadata": {
                "version": "2.0",
                "description": "Chemical name/formula to SMILES mapping",
                "last_updated": "2025-02-15",
                "total_entries": 0
            }
        }

    # 更新crystals部分
    name_mapping['crystals'] = crystals_data

    # 更新元数据
    name_mapping['_metadata']['last_updated'] = '2025-02-15'
    name_mapping['_metadata']['version'] = '2.0'

    # 计算总条目数
    total_entries = 0
    for key, value in name_mapping.items():
        if key == '_metadata':
            continue
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    total_entries += len(sub_value)
                else:
                    total_entries += 1

    name_mapping['_metadata']['total_entries'] = total_entries

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(name_mapping, f, ensure_ascii=False, indent=2)

    return total_entries

def main():
    """主函数"""
    base_path = Path(__file__).parent
    name_mapping_path = base_path / 'data' / 'name_mapping.json'

    print("=" * 60)
    print("生成完整name_mapping.json")
    print("=" * 60)

    total_entries = generate_complete_mapping(name_mapping_path)

    print(f"\n完成! 共生成 {total_entries} 个映射条目")
    print(f"文件已保存到: {name_mapping_path}")

if __name__ == '__main__':
    main()
