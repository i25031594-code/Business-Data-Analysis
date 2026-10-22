# CDA 二级量化策略分析：第 4、5 章 Python 复现

本项目复现教材以下内容：

- 第 4 章：使用 pandas 读取数据、选择与筛选、连接与合并、排序、分组汇总、透视、赋值、重复值、缺失值、异常值与分箱。
- 第 5 章：描述性统计、相关系数，以及 Matplotlib / Seaborn 的线图、饼图、条形图、直方图、散点图、箱线图、分布图和热图。

## 环境安装

建议使用 Python 3.10–3.13：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
```

## 运行脚本

从项目根目录执行：

```bash
python src/chapter4_pandas.py
python src/chapter5_statistics.py
python src/chapter5_visualization.py
```

脚本生成的表格和图片保存在 `artifacts/`。绘图脚本默认使用非交互式后端，适合命令行、CI 和无图形界面的环境。

## 运行 Notebook

```bash
jupyter lab
```

打开 `notebooks/chapter4/` 或 `notebooks/chapter5/` 下的 `.ipynb` 文件后选择“Run All”。Notebook 旁已放置原教材配套数据，保持原有相对路径可直接执行。

如果把 `src/` 中的脚本复制到 Notebook 单元格执行，请先将 Notebook 的工作目录设为项目根目录。代码会自动向上查找 `data/`，不依赖 Notebook 中不存在的 `__file__`。

## 兼容性说明

- 将 `Series.between(..., inclusive=True)` 更新为 pandas 新版支持的 `inclusive="both"`。
- 绘图脚本自动选择系统中可用的中文字体，不要求必须安装 SimHei。
- 所有随机示例均固定随机种子，便于重复得到相同结果。
- Matplotlib 箱线图使用新版参数 `tick_labels`。

## 项目结构

```text
.
├── data/                  # 脚本所需数据
├── notebooks/             # 教材 Notebook（兼容性修订版）
├── src/                   # 可直接运行的 Python 脚本
├── artifacts/             # 运行后生成（已忽略）
├── requirements.txt
└── README.md
```

数据与示例代码仅用于个人学习与教学复现，请遵循原教材及数据来源的授权范围。
