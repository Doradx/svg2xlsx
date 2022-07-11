from ast import Num
import os
import lxml.etree as ET
import pandas as pd
from datetime import datetime

svgPath = './svg/白家包-Crack.svg'

outputDir = './xlsx'

svg = ET.parse(svgPath)

print(svg)

# find the axes
XLines = svg.xpath('//g[@id="axis-x"]/line')
X = []
for x in XLines:
    X.append({
        'value': x.get('id'),
        'pixel': float(x.get('x1'))
    })
X=sorted(X,key=lambda x:x['pixel'])
YLines = svg.xpath('//g[@id="axis-y"]/line')
Y = []
for y in YLines:
    Y.append({
        'value': float(y.get('id').split('_')[1]),
        'pixel': float(y.get('y1'))
    })
Y=sorted(Y, key=lambda x:x['pixel'])

def parserPolyline(e):
    id = e.get('id')
    # data = []
    XList = []
    YList = []
    for line in e.get('points').split(' '):
        d = line.split(',')
        if len(d) < 2:
            continue
        XList.append(float(d[0]))
        YList.append(float(d[1]))
        # data.append({
        #     'x': float(d[0]),
        #     'y': float(d[1])
        # })
    return (id, XList, YList)

def transformArrayfromPixelToT(line,pMin,pMax,tMin,tMax):
    out = []
    for p in line:
        out.append((p-pMin)/(pMax-pMin)*(tMax-tMin)+tMin)
    return out

# find all polyline
polylines = svg.xpath('//polyline')
P = []
for line in polylines:
    P.append(parserPolyline(line))

# save data
outputPath = os.path.join(outputDir, os.path.basename(svgPath)+'.xlsx')
with pd.ExcelWriter(outputPath) as writer:
    pd.DataFrame(X).to_excel(writer, sheet_name='X')
    pd.DataFrame(Y).to_excel(writer, sheet_name='Y')

    for p in P:
        # transform X and Y
        xpMin, xpMax = X[0]['pixel'], X[1]['pixel']
        xvMin, xvMax = datetime.strptime(X[0]['value'].split('_')[1],'%Y-%m-%d').timestamp(), datetime.strptime(X[1]['value'].split('_')[1],'%Y-%m-%d').timestamp()
        Xt = transformArrayfromPixelToT(p[1], xpMin, xpMax, xvMin, xvMax)
        ypMin,ypMax, yvMin, yvMax = Y[0]['pixel'], Y[1]['pixel'], Y[0]['value'], Y[1]['value']
        Yt = transformArrayfromPixelToT(p[2], ypMin,ypMax, yvMin, yvMax)
        out = []
        for i in range(0,len(Xt)):
            out.append({
                'xp': p[1][i],
                'yp': p[2][i],
                'x': datetime.fromtimestamp(Xt[i]),
                'y': Yt[i]
            })
        pd.DataFrame(out).to_excel(writer, sheet_name=p[0])

print('Summary\r\nPolylines: %d' % (len(P)))
for p in P:
    print('%s: %d'%(p[0],len(p[1])))
print('Finished.')
