"""银行贷款申请归因分析：WPS 案例的 Python 复现版。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BG = "#F5F7FA"
NAVY = "#173B57"
BLUE = "#3B82F6"
TEAL = "#16A6A1"
ORANGE = "#F59E0B"
PURPLE = "#7C5CFC"
RED = "#E76F51"
GRAY = "#718096"


def chinese_font() -> str | None:
    """寻找常见中文字体，避免中文标题显示为方框。"""
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Zen Hei"]
    try:
        from matplotlib import font_manager
        paths = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
    except (KeyError, OSError):
        paths = []
    paths += [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in paths:
        if not Path(path).exists():
            continue
        stem = Path(path).stem.lower().replace(" ", "")
        if any(name.lower().replace(" ", "") in stem for name in candidates):
            return path
    return None


def read_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到 Excel 文件：{path}\n请使用 --input 指定文件路径。")
    sheets = pd.read_excel(path, sheet_name=None)
    data = next((df for df in sheets.values() if {"申请日期", "申请渠道"}.issubset(df.columns)), None)
    if data is None:
        raise ValueError("Excel 中没有找到包含‘申请日期’和‘申请渠道’的明细表")
    data = data.copy()
    data["申请日期"] = pd.to_datetime(data["申请日期"], errors="coerce")
    data = data.dropna(subset=["申请日期", "申请渠道"])
    if "申请书编号（主键）" in data.columns:
        data = data.drop_duplicates("申请书编号（主键）")
    data["月份"] = data["申请日期"].dt.to_period("M")
    return data


def prepare_metrics(data: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    monthly = data.groupby("月份").size().sort_index().rename("申请量")
    monthly.index = monthly.index.astype(str)
    channel = pd.crosstab(data["月份"].astype(str), data["申请渠道"]).reindex(monthly.index, fill_value=0)
    channel = channel.reindex(columns=sorted(channel.columns), fill_value=0)
    return monthly, channel, data


def base_style(ax, title: str) -> None:
    ax.set_facecolor("white")
    ax.set_title(title, loc="left", fontsize=14, color=NAVY, fontweight="bold", pad=14)
    ax.grid(axis="y", color="#E6ECF2", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=9)


def plot_trend(monthly: pd.Series, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=BG)
    x = np.arange(len(monthly))
    ax.plot(x, monthly.values, color=BLUE, marker="o", linewidth=3, markersize=7)
    ax.fill_between(x, monthly.values, 0, color=BLUE, alpha=0.08)
    ax.set_xticks(x, monthly.index)
    ax.set_ylabel("申请量（笔）", color=GRAY)
    for i, value in enumerate(monthly.values):
        ax.text(i, value + max(monthly.values) * 0.035, f"{value:,}", ha="center", color=NAVY, fontsize=9)
    base_style(ax, "贷款申请量变化趋势")
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def plot_channel(channel: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=BG)
    colors = [ORANGE, BLUE, TEAL, PURPLE]
    bottom = np.zeros(len(channel))
    for i, col in enumerate(channel.columns):
        values = channel[col].to_numpy()
        ax.bar(channel.index, values, bottom=bottom, label=col, color=colors[i % len(colors)], width=0.68)
        for j, value in enumerate(values):
            if value >= max(channel.to_numpy().ravel()) * 0.04:
                ax.text(j, bottom[j] + value / 2, str(int(value)), ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        bottom += values
    ax.set_ylabel("申请量（笔）", color=GRAY)
    ax.legend(frameon=False, ncol=len(channel.columns), loc="upper left")
    base_style(ax, "贷款申请量的渠道构成")
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def plot_attribution(channel: pd.DataFrame, output: Path) -> pd.DataFrame:
    if len(channel) < 2:
        raise ValueError("至少需要两个不同月份，才能计算归因变化")
    previous, current = channel.index[-2], channel.index[-1]
    changes = channel.loc[current] - channel.loc[previous]
    total_change = changes.sum()
    contribution = changes / total_change if total_change else changes * np.nan
    result = pd.DataFrame({"上月申请量": channel.loc[previous], "本月申请量": channel.loc[current], "申请量变化": changes, "贡献度": contribution})

    labels = ["上月总量", *result.index, "本月总量"]
    values = [channel.loc[previous].sum(), *changes.values, channel.loc[current].sum()]
    colors = [NAVY, *[TEAL if v >= 0 else RED for v in changes.values], NAVY]
    fig, ax = plt.subplots(figsize=(11, 5.8), facecolor=BG)
    ax.bar(labels, values, color=colors, width=0.65)
    ax.axhline(0, color="#A0AEC0", linewidth=0.8)
    ax.set_ylabel("申请量 / 变化量（笔）", color=GRAY)
    ax.set_title(f"{previous} → {current} 贷款申请量变化归因", loc="left", fontsize=14, color=NAVY, fontweight="bold", pad=14)
    for i, value in enumerate(values):
        y = value + (max(values) * 0.035 if value >= 0 else -max(values) * 0.08)
        ax.text(i, y, f"{value:+,}" if i not in (0, len(values) - 1) else f"{value:,}", ha="center", fontsize=9, color=NAVY)
    base_style(ax, ax.get_title())
    ax.set_title(f"{previous} → {current} 贷款申请量变化归因", loc="left", fontsize=14, color=NAVY, fontweight="bold", pad=14)
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return result


def plot_dashboard(monthly: pd.Series, channel: pd.DataFrame, attribution: pd.DataFrame, output: Path) -> None:
    fig = plt.figure(figsize=(16, 10), facecolor=BG)
    grid = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.22)
    ax1 = fig.add_subplot(grid[0, 0])
    x = np.arange(len(monthly))
    ax1.plot(x, monthly.values, color=BLUE, marker="o", linewidth=2.5)
    ax1.set_xticks(x, monthly.index, rotation=25)
    ax1.set_ylabel("申请量（笔）", color=GRAY)
    base_style(ax1, "贷款申请量变化趋势")
    for i, value in enumerate(monthly.values): ax1.text(i, value + 8, str(value), ha="center", fontsize=8, color=NAVY)

    ax2 = fig.add_subplot(grid[0, 1])
    bottom = np.zeros(len(channel))
    colors = [ORANGE, BLUE, TEAL, PURPLE]
    for i, col in enumerate(channel.columns):
        values = channel[col].to_numpy()
        ax2.bar(channel.index, values, bottom=bottom, label=col, color=colors[i % len(colors)])
        bottom += values
    ax2.set_xticks(np.arange(len(channel)), channel.index, rotation=25)
    ax2.set_ylabel("申请量（笔）", color=GRAY)
    ax2.legend(frameon=False, fontsize=8)
    base_style(ax2, "贷款申请量的渠道构成")

    ax3 = fig.add_subplot(grid[1, :])
    previous, current = channel.index[-2], channel.index[-1]
    changes = attribution["申请量变化"]
    labels = [f"{previous}\n总量", *changes.index.tolist(), f"{current}\n总量"]
    values = [channel.loc[previous].sum(), *changes.values, channel.loc[current].sum()]
    colors = [NAVY, *[TEAL if v >= 0 else RED for v in changes.values], NAVY]
    ax3.bar(labels, values, color=colors, width=0.6)
    ax3.axhline(0, color="#A0AEC0", linewidth=0.8)
    ax3.set_ylabel("申请量 / 变化量（笔）", color=GRAY)
    base_style(ax3, f"{previous} → {current} 贷款申请量变化归因")
    for i, value in enumerate(values):
        ax3.text(i, value + (8 if value >= 0 else -12), f"{value:+}" if 0 < i < len(values) - 1 else str(value), ha="center", fontsize=9, color=NAVY)
    fig.suptitle("银行贷款申请月度归因分析", fontsize=20, fontweight="bold", color=NAVY, y=0.98)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="生成银行贷款申请归因分析图表")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args, _ = parser.parse_known_args(argv)
    project_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    if args.input is None:
        local_input = Path(r"C:\Users\sangchenge\归因分析数据.xlsx")
        if not local_input.exists():
            extensionless_input = Path(r"C:\Users\sangchenge\归因分析数据")
            if extensionless_input.exists():
                local_input = extensionless_input
        project_input = project_dir / "data" / "application_data.xlsx"
        args.input = local_input if local_input.exists() else project_input
    args.output_dir = args.output_dir or project_dir / "output"
    font_path = chinese_font()
    if font_path:
        plt.rcParams["font.sans-serif"] = [Path(font_path).stem]
    else:
        # Windows 用户通常可以直接使用微软雅黑；Linux 用户可替换为本机中文字体。
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    data = read_data(args.input)
    monthly, channel, _ = prepare_metrics(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_trend(monthly, args.output_dir / "monthly_application_trend.png")
    plot_channel(channel, args.output_dir / "channel_composition.png")
    attribution = plot_attribution(channel, args.output_dir / "april_may_attribution.png")
    plot_dashboard(monthly, channel, attribution, args.output_dir / "attribution_dashboard.png")
    attribution.to_csv(args.output_dir / "channel_contribution.csv", encoding="utf-8-sig")
    print(f"看板已生成：{args.output_dir / 'attribution_dashboard.png'}")


if __name__ == "__main__":
    main()
