# svg2xlsx

本脚本用于提取svg矢量图像中的polyline数据, 需要搭配coreldraw使用。

# How to use it?
本脚本用于提取svg矢量图像中的polyline数据, 需要搭配coreldraw使用。关键步骤如下:
1. 将PDF导入coreldraw中, 删除不相关的元素, 仅保留: 数据曲线/polylines, 横坐标(日期)/axis-x, 纵坐标(数值)/axis-y;
2. 对于横坐标, 标记日期最小值和最大值, 以key_value做标记, 例如date_2018-10-01, date_2022-12-30, 将两个元素编组, 组名axis-x;
3. 对于纵坐标, 标记数据最小值和最大值, 以key_value做标记, 例如y_0, y_500, 将两个元素编组, 组名axis-y;
4. 对于数据曲线, 目前支持4种类型: polyline, path line, symbol, histogram, 分别对应折线, 路径线, 符号, 直方图; 
    将需要提取的曲线编组, 图层命名为name-type, 其中name为曲线名称, type为曲线类型(需要根据实际情况选取)
4. 将导出的svg放到svg文件夹中, 并修改本代码中的filename;
5. 执行本脚本, 数据将保存在xlsx文件夹中。

对于坐标系，坐标单位:
- int
- float
- date
- datetime

曲线类型:
- PL: polyline, 折线
- PTL: path line, 路径线
- S: symbol, 符号
- H: histogram, 直方图

对于Symbol line, 可添加一个属性，标记symbol需要读取的数据位置, 包括：左(left)、中(center)、右(right); 上(up)、中(center)、下(down)。例如：
- CC: 中心
- LC: 左中
- RC: 右中
- UC: 上中
- DC: 下中
- LU: 左上
- RU: 右上
- LD: 左下
- RD: 右下

# coreldraw setting for svg
1. axis-x: X轴, 每个标记为type_value; type包含 int, float, date, datetime; value为坐标轴刻度;
2. axis-y: Y轴, 与X轴规则相同;
3. XXX-S: symbol line, 作为分组，里面包含 N 个符号, 支持polygon, line, path;
4. XXX: polyline, 为 Polyline 对象, 直接提取折线坐标;

# Author
Ding Xia, cug.xia@gmail.com