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
from svgelements import Path, Polygon, SimpleLine, Line

filename = '木鱼包滑坡-GPS-Rainfall.svg'

svgPath = os.path.join('./svg/', filename)

outputDir = './xlsx'

svg = ET.parse(svgPath)

root = svg.getroot()

# polylines = root.xpath("//*[local-name()='polyline']")

# find the axes
XLines = root.xpath(
    "//*[local-name()='g' and @id='axis-x']/*")
X = []
YLines = root.xpath(
    "//*[local-name()='g' and @id='axis-y']/*")
Y = []

# string to value


def s2n(value, type='INT'):
    match type.upper():
        case 'INT':
            value = int(value)
        case 'FLOAT':
            value = float(value)
        case 'DATE':
            value = datetime.strptime(value, '%Y-%m-%d').timestamp()
        case 'DATETIME':
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timestamp()
    return value

# value to string


def n2s(value, type='INT'):
    match type.upper():
        case 'INT':
            value = int(value)
        case 'FLOAT':
            value = float(value)
        case 'DATE':
            value = datetime.fromtimestamp(value).strftime('%Y-%m-%d')
        case 'DATETIME':
            value = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    return value


def parseAxis(e):
    label, value = e.get('id').replace('_x0020_',' ').split('_')
    xPixel = 0
    yPixel = 0
    if 'line' in e.tag:
        xPixel = (float(e.get('x1')) + float(e.get('x2')))/2
        yPixel = (float(e.get('y1')) + float(e.get('y2')))/2
    elif 'polygon' in e.tag:
        bbox = Polygon(e.get('points')).bbox()
        xPixel = (bbox[0] + bbox[2])/2
        yPixel = (bbox[1] + bbox[3])/2
    else:
        raise Exception('Unexpect type of Axis: %s' % e.tag)
    label = label.upper()
    # int, float, date, datetime
    value = s2n(value, label)
    return {
        'fl': e.get('id'),
        't': label,
        'v': value,
        'xp': xPixel,
        'yp': yPixel
    }


for x in XLines:
    X.append(parseAxis(x))

for y in YLines:
    Y.append(parseAxis(y))

X = sorted(X, key=lambda x: x['xp'])
Y = sorted(Y, key=lambda x: x['yp'])

# Polyline
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


def parserSymbol(e, type='CC'):
    '''
    e: element
    type: type of output: up, down, center; left, center, right; default: cc 
    '''
    def getXyFromBbox(b, type='CC'):
        x, y = 0, 0
        match type[0].upper():
            case 'D':
                # low
                x = max(b[0], b[2])
            case 'C':
                # center
                x = sum([b[0], b[2]])/2
            case 'U':
                # up
                x = min(b[0], b[2])
        match type[1].upper():
            case 'L':
                y = min(b[1], b[3])
            case 'C':
                y = sum([b[1], b[3]])/2
            case 'R':
                y = max(b[1], b[3])
        return (x, y)
    # check the tag, polygon or path
    x, y = 0, 0
    if 'polygon' in e.tag:
        p = Polygon(e.get('points'))
        bbox = p.bbox()
    elif 'path' in e.tag:
        p = Path(e.get('d'))
        bbox = p.bbox()
    elif 'line' in e.tag:
        p = SimpleLine(e.get('x1'), e.get('y1'), e.get('x2'), e.get('y2'))
        bbox = (p.x1, p.y1, p.x2, p.y2)
    else:
        raise Exception('Error tag.')
    x, y = getXyFromBbox(bbox, type)
    return (x, y)

# Symbolline


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

# Histogram


def parserHistogram(e):
    id = e.get('id')
    XList = []
    YList = []
    for s in e:
        # parser symbol to get the center data
        x, y = parserSymbol(s, 'UC') # up center
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

# find all histogram
HistogramLines = root.xpath("//*[local-name()='g' and contains(@id,'-H')]")
for bar in HistogramLines:
    P.append(parserHistogram(bar))

# save data
outputPath = os.path.join(outputDir, os.path.basename(svgPath)+'.xlsx')
with pd.ExcelWriter(outputPath) as writer:
    pd.DataFrame(X).to_excel(writer, sheet_name='X')
    pd.DataFrame(Y).to_excel(writer, sheet_name='Y')

    for p in P:
        # transform X and Y
        xpMin, xpMax = X[0]['xp'], X[1]['xp']
        xvMin, xvMax = X[0]['v'], X[1]['v']
        Xt = transformArrayfromPixelToT(p[1], xpMin, xpMax, xvMin, xvMax)
        ypMin, ypMax, yvMin, yvMax = Y[0]['yp'], Y[1]['yp'], Y[0]['v'], Y[1]['v']
        Yt = transformArrayfromPixelToT(p[2], ypMin, ypMax, yvMin, yvMax)
        out = []
        for i in range(0, len(Xt)):
            out.append({
                'xp': p[1][i],
                'yp': p[2][i],
                'x': n2s(Xt[i], X[0]['t']),
                'y': n2s(Yt[i], Y[0]['t'])
            })
        pd.DataFrame(out).to_excel(writer, sheet_name=p[0])

print('Summary\r\nlines: %d' % (len(P)))
for p in P:
    print('%s: %d' % (p[0], len(p[1])))
print('Finished.')