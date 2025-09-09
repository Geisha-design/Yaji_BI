import pandas as pd
from geopy.geocoders import Nominatim
import folium

# 读取文件，这里假设是 CSV 文件，需要根据实际情况修改文件路径和文件类型
data = pd.read_excel('副本订单应收应付表1757052045483219.xlsx')

# 使用 geopy 获取地址的经纬度
geolocator = Nominatim(user_agent="address_plotter")

def get_lat_lon(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except:
        return None, None

# 示例数据，实际应用中请替换为从文件读取的数据
data = pd.DataFrame({
    '提箱点': ['地址1', '地址2'],
    '还箱点': ['地址3', '地址4'],
    '门点详情地址': ['地址5', '地址6']
})

# 获取提箱点的经纬度
data[['提箱点纬度', '提箱点经度']] = data['提箱点'].apply(lambda x: pd.Series(get_lat_lon(x)))

# 获取还箱点的经纬度
data[['还箱点纬度', '还箱点经度']] = data['还箱点'].apply(lambda x: pd.Series(get_lat_lon(x)))

# 获取门点详情地址的经纬度
data[['门点纬度', '门点经度']] = data['门点详情地址'].apply(lambda x: pd.Series(get_lat_lon(x)))

# 创建地图
m = folium.Map(location=[data['提箱点纬度'].mean(), data['提箱点经度'].mean()], zoom_start=10)

# 添加提箱点标记
for index, row in data.iterrows():
    if pd.notnull(row['提箱点纬度']) and pd.notnull(row['提箱点经度']):
        folium.Marker(
            location=[row['提箱点纬度'], row['提箱点经度']],
            popup=f"提箱点: {row['提箱点']}",
            icon=folium.Icon(color='blue')
        ).add_to(m)

# 添加还箱点标记
for index, row in data.iterrows():
    if pd.notnull(row['还箱点纬度']) and pd.notnull(row['还箱点经度']):
        folium.Marker(
            location=[row['还箱点纬度'], row['还箱点经度']],
            popup=f"还箱点: {row['还箱点']}",
            icon=folium.Icon(color='red')
        ).add_to(m)

# 添加门点详情地址标记
for index, row in data.iterrows():
    if pd.notnull(row['门点纬度']) and pd.notnull(row['门点经度']):
        folium.Marker(
            location=[row['门点纬度'], row['门点经度']],
            popup=f"门点: {row['门点详情地址']}",
            icon=folium.Icon(color='green')
        ).add_to(m)

# 保存地图为 HTML 文件
m.save('/mnt/address_distribution_map.html')