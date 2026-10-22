"""第 5 章：描述性统计分析复现。"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
DATA_PATH = ROOT / "data" / "chapter5" / "sndHsPr.csv"
ARTIFACT_DIR = ROOT / "artifacts" / "chapter5_statistics"


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(DATA_PATH)

    summary = data["price"].agg(["mean", "median", "std"])
    quartiles = data["price"].quantile([0.25, 0.5, 0.75]).rename("price")
    dispersion = pd.Series(
        {"range": data["price"].max() - data["price"].min(), "variance": data["price"].var(), "std": data["price"].std()}
    )

    rng = np.random.default_rng(0)
    normal = pd.Series(rng.standard_normal(1000), name="normal")
    shape = pd.Series({"skew": normal.skew(), "kurtosis": normal.kurtosis()})
    correlations = pd.concat(
        {method: data[["AREA", "price"]].corr(method=method) for method in ("pearson", "spearman", "kendall")},
        names=["method"],
    )

    summary.to_csv(ARTIFACT_DIR / "central_tendency.csv", encoding="utf-8-sig")
    quartiles.to_csv(ARTIFACT_DIR / "quartiles.csv", encoding="utf-8-sig")
    dispersion.to_csv(ARTIFACT_DIR / "dispersion.csv", encoding="utf-8-sig")
    shape.to_csv(ARTIFACT_DIR / "distribution_shape.csv", encoding="utf-8-sig")
    correlations.to_csv(ARTIFACT_DIR / "correlations.csv", encoding="utf-8-sig")

    ax = data["price"].hist(bins=20, figsize=(8, 5), edgecolor="white")
    ax.set(title="House Price Distribution", xlabel="price", ylabel="frequency")
    ax.figure.tight_layout()
    ax.figure.savefig(ARTIFACT_DIR / "price_histogram.png", dpi=160)
    plt.close(ax.figure)

    print("集中趋势：\n", summary)
    print("\n四分位数：\n", quartiles)
    print("\n离散程度：\n", dispersion)
    print("\n偏度与峰度：\n", shape)
    print("\n相关系数：\n", correlations)
    print(f"\n运行完成，输出目录：{ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
