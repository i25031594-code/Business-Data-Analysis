"""第 4 章：pandas 数据整合和数据清洗复现。"""

from pathlib import Path

import numpy as np
import pandas as pd


def find_project_root() -> Path:
    """兼容 Python 脚本和没有 ``__file__`` 的 Jupyter Notebook。"""
    if "__file__" in globals():
        return Path(__file__).resolve().parents[1]

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "data" / "chapter4").is_dir():
            return candidate
    raise FileNotFoundError("找不到项目根目录，请先将工作目录切换到 cda-quant-python。")


ROOT = find_project_root()
DATA_DIR = ROOT / "data" / "chapter4"
ARTIFACT_DIR = ROOT / "artifacts" / "chapter4"


def section(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


def show(label: str, value: object) -> None:
    print(f"\n[{label}]\n{value}")


def cap(series: pd.Series, quantile: tuple[float, float] = (0.01, 0.99)) -> pd.Series:
    """用上下分位数对连续变量进行盖帽处理。"""
    lower, upper = series.quantile(quantile).tolist()
    return series.clip(lower=lower, upper=upper)


def read_data_demo() -> None:
    section("读取与写出数据")
    sample_path = DATA_DIR / "sample.csv"
    frame = pd.read_csv(sample_path)
    show("完整 CSV", frame)
    show("指定列与行数", pd.read_csv(sample_path, usecols=["id", "name"], nrows=2))

    chunks = pd.read_csv(DATA_DIR / "big.csv", chunksize=900)
    chunk_sizes = [chunk.shape for chunk in chunks]
    show("分块尺寸", chunk_sizes)
    combined = pd.concat(pd.read_csv(DATA_DIR / "big.csv", chunksize=900), ignore_index=True)
    show("合并后尺寸", combined.shape)

    missing = pd.read_csv(sample_path, na_values="99999")
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    missing.to_csv(ARTIFACT_DIR / "write.csv", encoding="utf-8-sig", index=False)


def row_column_demo() -> None:
    section("行列操作与条件查询")
    rng = np.random.default_rng(0)
    sample = pd.DataFrame(rng.standard_normal((4, 5)), columns=list("abcde"))
    show("原始数据", sample)
    show("选择 a 列（Series）", sample["a"])
    show("选择 a 列（DataFrame）", sample[["a"]])
    show("loc 切片", sample.loc[:1, :"b"])
    show("iloc 切片", sample.iloc[:2, :2])

    sample["new_col"] = sample["a"] - sample["b"]
    show("新增列", sample)
    show("assign 新增多列", sample.assign(new_col2=sample["a"] - sample["b"], new_col3=sample["a"] + sample["b"]))
    show("删除列", sample.drop(columns=["a", "b"]))

    students = pd.DataFrame(
        {
            "group": [1, 1, 1, 2, 1, 2],
            "name": ["Bob", "Lindy", "Mark", "Miki", "Sully", "Rose"],
            "score": [98, 78, 87, 77, 65, 67],
        }
    )
    show("分数大于 70", students[students["score"] > 70])
    show("且条件", students[(students["score"] > 70) & (students["group"] == 1)])
    show("非条件", students[~(students["group"] == 1)])
    show("query", students.query("score > 90"))
    show("between", students[students["score"].between(70, 80, inclusive="both")])
    show("isin", students[students["name"].isin(["Bob", "Lindy"])])
    show("字符串匹配", students[students["name"].str.contains(r"M+")])


def combine_demo() -> None:
    section("连接、合并与排序")
    left = pd.DataFrame({"col1": ["a", "b", "c"], "id": [1, 2, 3]})
    right = pd.DataFrame({"col2": ["d", "e"], "id": [4, 3]})
    for how in ("inner", "left", "right", "outer"):
        show(f"{how} merge", left.merge(right, how=how, on="id"))

    indexed_left = pd.DataFrame({"id1": [1, 2, 3], "col1": ["a", "b", "c"]}, index=[1, 2, 3])
    indexed_right = pd.DataFrame({"id2": [1, 2, 3], "col2": ["aa", "bb", "cc"]}, index=[1, 3, 2])
    show("横向 concat", pd.concat([indexed_left, indexed_right], axis=1))
    show("按索引 join", indexed_left.join(indexed_right))

    upper = pd.DataFrame({"id": [1, 1, 1, 2, 3, 4, 6], "col": list("aab cveq".replace(" ", ""))})
    lower = pd.DataFrame({"id": [1, 2, 3, 3, 5], "col": list("xyzvw")})
    show("纵向 concat", pd.concat([upper, lower], ignore_index=True))
    show("合并后去重", pd.concat([upper, lower], ignore_index=True).drop_duplicates())
    renamed = upper.rename(columns={"col": "new_col"})
    show("列名不同的纵向合并", pd.concat([upper, renamed], ignore_index=True))

    scores = pd.DataFrame(
        {"group": [1, 1, 1, 2, 1, 2], "name": ["Bob", "Lindy", "Mark", "Miki", "Sully", "Rose"], "score": [98, 78, 87, 77, 77, np.nan]}
    )
    show("单列排序", scores.sort_values("score", ascending=False, na_position="last"))
    show("多列排序", scores.sort_values(["group", "score"]))


def summarize_demo() -> None:
    section("分组、透视与条件赋值")
    students = pd.DataFrame(
        {
            "name": ["Bob", "Lindy", "Mark", "Miki", "Sully", "Rose"],
            "class": [1, 1, 1, 2, 1, 2],
            "grade": [1, 1, 1, 2, 2, 2],
            "chinese": [88, 78, 86, 56, 77, 54],
            "math": [98, 78, 87, 77, 77, np.nan],
        }
    )
    show("按年级最大值", students.groupby("grade")[["math"]].max())
    show("多字段分组均值", students.groupby(["grade", "class"])[["math", "chinese"]].mean())
    grouped = students.groupby(["grade", "class"])[["math", "chinese"]].agg(["min", "max"])
    show("多指标汇总", grouped)
    show("MultiIndex 取值", grouped.loc[:, ("math", "min")])

    sales = pd.DataFrame(
        {
            "Monetary": [3608, 420, 1894, 3503, 4567],
            "cust_id": [10001, 10001, 10002, 10002, 10003],
            "type": ["Normal", "Special_offer", "Normal", "Special_offer", "Special_offer"],
        }
    )
    show("透视表", pd.pivot_table(sales, index="cust_id", columns="type", values="Monetary", fill_value=0, aggfunc="sum"))

    scores = pd.DataFrame(
        {"name": ["Bob", "Lindy", "Mark", "Miki", "Sully", "Rose"], "score": [99, 78, 999, 77, 77, np.nan], "group": [1, 1, 1, 2, 1, 2]}
    )
    show("替换异常编码", scores.replace({"score": {999: np.nan}, "name": {"Bob": np.nan}}))
    scores["class_n"] = scores["group"].map({1: "class1", 2: "class2"})
    show("条件赋值", scores)


def clean_demo() -> None:
    section("重复、缺失、异常与分箱")
    duplicates = pd.DataFrame(
        {"group": [1, 1, 1, 2, 1, 2], "id": [1, 1, 1, 3, 4, 5], "name": ["Bob", "Bob", "Mark", "Miki", "Sully", "Rose"], "score": [99, 99, 87, 77, 77, np.nan]}
    )
    show("重复行", duplicates[duplicates.duplicated()])
    show("整行去重", duplicates.drop_duplicates())
    show("按 id 去重", duplicates.drop_duplicates("id"))

    missing = pd.DataFrame(
        {"group": [1, 1, np.nan, 2, 1, np.nan], "id": [1, 1, 1, 3, 4, np.nan], "name": ["Bob", "Bob", "Mark", "Miki", "Sully", np.nan], "score": [99, np.nan, 87, 77, 77, np.nan]}
    )
    show("各列缺失率", missing.isna().mean())
    show("均值填充", missing["score"].fillna(missing["score"].mean()))
    show("中位数填充", missing["score"].fillna(missing["score"].median()))
    show("缺失指示变量", missing["score"].isna().astype(int))

    rng = np.random.default_rng(0)
    normal = pd.DataFrame({"normal": rng.standard_normal(1000)})
    capped = normal.apply(cap, quantile=(0.01, 0.99))
    show("盖帽前后范围", pd.DataFrame({"before": [normal.min().iloc[0], normal.max().iloc[0]], "after": [capped.min().iloc[0], capped.max().iloc[0]]}, index=["min", "max"]))

    small = pd.Series(rng.standard_normal(10), name="normal")
    show("等宽分箱", pd.cut(small, bins=5, labels=[1, 2, 3, 4, 5]))
    show("二分类分箱", pd.cut(small, bins=2, labels=["bad", "good"]))
    show("中位数分箱", pd.cut(small, bins=small.quantile([0, 0.5, 1]), labels=["bad", "good"], include_lowest=True))

    summary = pd.DataFrame({"original": normal["normal"].describe(), "capped": capped["normal"].describe()})
    summary.to_csv(ARTIFACT_DIR / "cap_summary.csv", encoding="utf-8-sig")


def main() -> None:
    read_data_demo()
    row_column_demo()
    combine_demo()
    summarize_demo()
    clean_demo()
    print(f"\n运行完成，输出目录：{ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
