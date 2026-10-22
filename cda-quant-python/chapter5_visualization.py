"""第 5 章：Matplotlib 与 Seaborn 数据可视化复现。"""

from pathlib import Path
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import seaborn as sns


def find_project_root() -> Path:
    """兼容 Python 脚本和没有 ``__file__`` 的 Jupyter Notebook。"""
    if "__file__" in globals():
        return Path(__file__).resolve().parents[1]

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "data" / "chapter5").is_dir():
            return candidate
    raise FileNotFoundError("找不到项目根目录，请先将工作目录切换到 cda-quant-python。")


ROOT = find_project_root()
DATA_PATH = ROOT / "data" / "chapter5" / "2017股价.xlsx"
ARTIFACT_DIR = ROOT / "artifacts" / "chapter5_visualization"


def configure_chinese_font() -> None:
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in candidates if name in available), None)
    if selected:
        plt.rcParams["font.sans-serif"] = [selected]
    else:
        warnings.warn("未找到常见中文字体，中文标签可能显示为方框。", stacklevel=2)
    plt.rcParams["axes.unicode_minus"] = False
    sns.set_theme(style="whitegrid", font=selected)


def save_current(name: str) -> None:
    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / name, dpi=160, bbox_inches="tight")
    plt.close("all")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    configure_chinese_font()
    rng = np.random.default_rng(1)

    stocks = pd.read_excel(DATA_PATH)
    plt.figure(figsize=(10, 4))
    markers = {"收盘价": "*", "开盘价": "o", "最高价": "v", "最低价": "^"}
    x = np.arange(len(stocks))
    for column, marker in markers.items():
        plt.plot(x, stocks[column], marker=marker, label=column)
    plt.title("股价走势图")
    plt.xlabel("时间")
    plt.ylabel("股价")
    plt.xticks(x, stocks["日期"].dt.strftime("%Y-%m-%d"), rotation=30, ha="right")
    plt.legend()
    save_current("01_stock_prices.png")

    votes = pd.DataFrame({"方案": ["plan A", "plan B", "plan C", "plan D", "plan E"], "投票人数": rng.integers(10, 100, 5)})
    plt.figure(figsize=(6, 6))
    plt.pie(votes["投票人数"], labels=votes["方案"], autopct="%.2f%%", textprops={"fontsize": 13})
    plt.title("方案投票占比饼图", fontsize=14)
    save_current("02_vote_pie.png")

    plt.figure(figsize=(8, 4))
    plt.bar(votes["方案"], votes["投票人数"], width=0.6)
    plt.title("各方案投票人数柱形图")
    plt.xlabel("方案")
    plt.ylabel("投票人数")
    save_current("03_vote_bar.png")

    ordered = votes.sort_values("投票人数")
    plt.figure(figsize=(8, 4))
    plt.barh(ordered["方案"], ordered["投票人数"], height=0.6)
    plt.title("各方案投票人数条形图")
    plt.xlabel("投票人数")
    plt.ylabel("方案")
    save_current("04_vote_barh.png")

    values = rng.normal(loc=80, scale=20, size=200).astype(int)
    bins = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=bins, edgecolor="white")
    plt.xticks(bins)
    plt.title("数据直方图")
    save_current("05_histogram.png")

    yield_rain = pd.DataFrame({"产量": [2200, 3300, 4400, 5500, 5700, 7300, 8000], "降水量": [22, 39, 55, 66, 105, 100, 122]})
    plt.figure(figsize=(7, 5))
    plt.scatter(yield_rain["降水量"], yield_rain["产量"])
    plt.xlabel("降水量")
    plt.ylabel("产量")
    plt.title("降水量与产量")
    save_current("06_scatter.png")

    scores = pd.DataFrame({"语文": rng.integers(60, 150, 10), "英语": rng.integers(40, 150, 10), "数学": rng.integers(20, 150, 10)})
    plt.figure(figsize=(8, 6))
    plt.boxplot([scores["语文"], scores["英语"], scores["数学"]], tick_labels=["语文", "英语", "数学"])
    plt.title("三科成绩箱线图")
    save_current("07_boxplot.png")

    grid = sns.displot(values, bins=bins, kde=True)
    grid.set_axis_labels("数值", "频数")
    grid.figure.suptitle("带核密度估计的直方图", y=1.02)
    grid.figure.savefig(ARTIFACT_DIR / "08_histogram_kde.png", dpi=160, bbox_inches="tight")
    plt.close("all")

    xy = rng.multivariate_normal([0, 1], [(1, 0.5), (0.5, 1)], 200)
    frame = pd.DataFrame(xy, columns=["x", "y"])
    joint = sns.jointplot(x="x", y="y", data=frame)
    joint.figure.savefig(ARTIFACT_DIR / "09_joint_scatter.png", dpi=160, bbox_inches="tight")
    plt.close("all")

    joint_kde = sns.jointplot(x="x", y="y", data=frame, kind="kde")
    joint_kde.figure.savefig(ARTIFACT_DIR / "10_joint_kde.png", dpi=160, bbox_inches="tight")
    plt.close("all")

    heat = pd.DataFrame(rng.uniform(-1, 1, (7, 7)), index=list("abcdefg"), columns=list("ABCDEFG"))
    plt.figure(figsize=(8, 6))
    sns.heatmap(heat, cmap="vlag", center=0)
    plt.title("随机矩阵热图")
    save_current("11_heatmap.png")

    print(f"已生成 11 张图，输出目录：{ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
