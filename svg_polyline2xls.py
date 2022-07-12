'''
Created at 2022/07/11 15:30:20
By Ding Xia, cug.xia@gmail.com

本脚本用于提取svg矢量图像中的polyline数据, 需要搭配coreldraw使用。关键步骤如下:
1. 将PDF导入coreldraw中, 删除不相关的元素, 仅保留: 数据曲线/polylines, 横坐标(日期)/axis-x, 纵坐标(数值)/axis-y;
2. 对于横坐标, 标记日期最小值和最大值, 以key_value做标记, 例如date_2018-10-01, date_2022-12-30, 将两个元素编组, 组名axis-x;
3. 对于纵坐标, 标记数据最小值和最大值, 以key_value做标记, 例如y_0, y_500, 将两个元素编组, 组名axis-y;
4. 将导出的svg放到svg文件夹中, 并修改本代码中的filename;
5. 执行本脚本, 数据将保存在xlsx文件夹中。
'''

import os
import lxml.etree as ET
import pandas as pd
from datetime import datetime

filename = '三舟溪滑坡-Symbols.svg'

svgPath = os.path.join('./svg/', filename)

outputDir = './xlsx'

svg = ET.parse(svgPath)

root = svg.getroot()

# polylines = root.xpath("//*[local-name()='polyline']")

# find the axes
XLines = root.xpath(
    "//*[local-name()='g' and @id='axis-x']/*[local-name()='line']")
X = []
for x in XLines:
    X.append({
        'value': x.get('id'),
        'pixel': float(x.get('x1'))
    })
X = sorted(X, key=lambda x: x['pixel'])
YLines = root.xpath(
    "//*[local-name()='g' and @id='axis-y']/*[local-name()='line']")
Y = []
for y in YLines:
    Y.append({
        'value': float(y.get('id').split('_')[1]),
        'pixel': float(y.get('y1'))
    })
Y = sorted(Y, key=lambda x: x['pixel'])


def parserPolyline(e):
    id = e.get('id')
    XList = []
    YList = []
    for line in e.get('points').split(' '):
        d = line.split(',')
        if len(d) < 2:
            continue
        XList.append(float(d[0]))
        YList.append(float(d[1]))
    return (id, XList, YList)


def parserSymbol(e):
    # check the tag, polygon or path
    x, y = 0, 0
    if 'polygon' in e.tag:
        XList = []
        YList = []
        for p in e.get('points').split(' '):
            d = p.split(',')
            if len(d) < 2:
                continue
            XList.append(float(d[0]))
            YList.append(float(d[1]))
        x = sum(XList)/len(XList)
        y = sum(YList)/len(YList)
    elif 'path' in e.tag:
        c = e.get('d')
        startPos = c[c.find('M')+1:c.find('c')].split(' ')
        cP = c[c.find('c')+1:c.find('z')].split(' ')[2].split(',')
        x = float(startPos[0]) + float(cP[0])
        y = float(startPos[1])
    else:
        raise Exception('Error tag.')
    return (x, y)


def parserSymbolLine(e):
    id = e.get('id')
    XList = []
    YList = []
    for s in e:
        # parser symbol to get the center data
        x, y = parserSymbol(s)
        XList.append(x)
        YList.append(y)
    return (id, XList, YList)


def transformArrayfromPixelToT(line, pMin, pMax, tMin, tMax):
    out = []
    for p in line:
        out.append((p-pMin)/(pMax-pMin)*(tMax-tMin)+tMin)
    return out


# find all polyline
PolyLines = root.xpath("//*[local-name()='polyline']")

P = []
for line in PolyLines:
    P.append(parserPolyline(line))

# find all symbol lines
SymbolLines = root.xpath("//*[local-name()='g' and contains(@id,'-S')]")
for line in SymbolLines:
    P.append(parserSymbolLine(line))

# save data
outputPath = os.path.join(outputDir, os.path.basename(svgPath)+'.xlsx')
with pd.ExcelWriter(outputPath) as writer:
    pd.DataFrame(X).to_excel(writer, sheet_name='X')
    pd.DataFrame(Y).to_excel(writer, sheet_name='Y')

    for p in P:
        # transform X and Y
        xpMin, xpMax = X[0]['pixel'], X[1]['pixel']
        xvMin, xvMax = datetime.strptime(X[0]['value'].split('_')[1], '%Y-%m-%d').timestamp(
        ), datetime.strptime(X[1]['value'].split('_')[1], '%Y-%m-%d').timestamp()
        Xt = transformArrayfromPixelToT(p[1], xpMin, xpMax, xvMin, xvMax)
        ypMin, ypMax, yvMin, yvMax = Y[0]['pixel'], Y[1]['pixel'], Y[0]['value'], Y[1]['value']
        Yt = transformArrayfromPixelToT(p[2], ypMin, ypMax, yvMin, yvMax)
        out = []
        for i in range(0, len(Xt)):
            out.append({
                'xp': p[1][i],
                'yp': p[2][i],
                'x': datetime.fromtimestamp(Xt[i]),
                'y': Yt[i]
            })
        pd.DataFrame(out).to_excel(writer, sheet_name=p[0])

print('Summary\r\nlines: %d' % (len(P)))
for p in P:
    print('%s: %d' % (p[0], len(p[1])))
print('Finished.')
