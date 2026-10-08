# 银行贷款申请归因分析：Python 复现版

这是 WPS 银行归因分析案例的 Python 复现版本，使用 `pandas + matplotlib` 从贷款申请明细数据重新计算并绘制结果图表。

## 复现内容

- 2020 年 11 月至 2021 年 5 月贷款申请量趋势
- 各申请渠道的月度申请量构成
- 2021 年 4 月到 5 月的申请量变化归因图
- 2021 年 5 月渠道贡献度表

## 运行

```bash
pip install -r requirements.txt
python attribution_dashboard.py
```

默认读取 `data/application_data.xlsx`，生成：

- `output/attribution_dashboard.png`
- `output/monthly_application_trend.png`
- `output/channel_composition.png`
- `output/april_may_attribution.png`
- `output/channel_contribution.csv`

也可以指定自己的数据文件：

```bash
python attribution_dashboard.py --input data/your_data.xlsx
```

## 数据格式

Excel 中需要有一张工作表，包含以下字段：

`申请书编号（主键）`、`申请日期`、`申请渠道`

渠道名称可以是手机银行、理财经理（柜台）、自助机。程序会按照日期自动生成申请年月。

## 指标口径

- 贷款申请量：按申请书编号去重计数
- 月度环比变化率：本月申请量 / 上月申请量 - 1
- 渠道贡献度：渠道申请量变化 / 总申请量变化
- 当前案例的 2021 年 4 月到 5 月总申请量从 269 降至 230，变化为 -39

如果总量下降，渠道贡献度为负数表示该渠道拖累总量；正数表示该渠道对冲了部分下降。

