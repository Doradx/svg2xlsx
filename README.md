# svg2xlsx

本脚本用于提取svg矢量图像中的polyline数据, 需要搭配coreldraw使用。

# How to use?
关键步骤如下:
1. 将PDF导入coreldraw中, 删除不相关的元素, 仅保留: 数据曲线/polylines, 横坐标(日期)/axis-x, 纵坐标(数值)/axis-y;
2. 对于横坐标, 标记日期最小值和最大值, 以key_value做标记, 例如date_2018-10-01, date_2022-12-30, 将两个元素编组, 组名axis-x;
3. 对于纵坐标, 标记数据最小值和最大值, 以key_value做标记, 例如y_0, y_500, 将两个元素编组, 组名axis-y;
4. 将导出的svg放到svg文件夹中, 并修改本代码中的filename;
5. 执行本脚本, 数据将保存在xlsx文件夹中。


# Author
Ding Xia, cug.xia@gmail.com