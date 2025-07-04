import pandas as pd

# 读取Excel文件
file_path = '大笨鸟 6月数据.xlsx'
df = pd.read_excel(file_path)

# 获取数据部分的起始行索引（假设数据从第五行开始）
data_start_row = 4

# 获取C、F、G列的数据，并将其加到H、K、L列对应位置
for i in range(data_start_row, len(df)):
    if pd.notna(df.iloc[i, 2]):  # 判断C列数据是否为非空
        df.iloc[i, 7] = df.iloc[i, 7] + df.iloc[i, 2] if pd.notna(df.iloc[i, 7]) else df.iloc[i, 2]
    if pd.notna(df.iloc[i, 5]):  # 判断F列数据是否为非空
        df.iloc[i, 10] = df.iloc[i, 10] + df.iloc[i, 5] if pd.notna(df.iloc[i, 10]) else df.iloc[i, 5]
    if pd.notna(df.iloc[i, 6]):  # 判断G列数据是否为非空
        df.iloc[i, 11] = df.iloc[i, 11] + df.iloc[i, 6] if pd.notna(df.iloc[i, 11]) else df.iloc[i, 6]

# 保存修改后的数据到新的Excel文件
output_file_path = '大笨鸟 6月数据_修改后.xlsx'
df.to_excel(output_file_path, index=False)
