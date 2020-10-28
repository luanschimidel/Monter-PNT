# criando StackFile
import os
from osgeo import gdal,ogr,osr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import rasterio
from rasterio.plot import show
from random import randint
from statistics import pstdev

#GetPixelValue = raster.dataProvider().sample(QgsPointXY(671865.0,-2535825.0),1)



path = r'C:\Users\ximis\workspace\pnt\imagens_landsat\landsat8\ndvi_analises'
file1 = r'C:\Users\ximis\workspace\pnt\imagens_landsat\landsat8\ndvi_analises\LC08_L1TP_217076_20140226_20170425_01_T1_NDVI.tif'





# funcao para extrair as extremidades 
def GetExtent(gt,cols,rows):
    #Return list of corner coordinates from a geotransform
    ext = []
    xarr=[0,cols]
    yarr=[0,rows]
    
    
    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            
            #print (x,y)
        yarr.reverse()
    return ext
    





# Cria uma lista com a ordem em data correta dos rasters

rasters = []

for el in os.listdir(path): 
    if el.endswith('tif') or el.endswith('TIF'):
        
        data = (el.split('_')[3])
        data = data[0:4]+'-'+data[4:6]+'-'+data[6:8]
        data = datetime.strptime(data,'%Y-%m-%d')
        x = {'file':path+'/'+el , 'data': data}
        rasters.append(x)

datas = []
for el in rasters:
    datas.append(el['data'])

datas.sort()


rasters_ordem=[]
for el in datas:
    for r in rasters:
        if el == r['data']:
            rasters_ordem.append(r['file'])
    
    

#gera Array com o primeiro raster
raster1 = gdal.Open(rasters_ordem[0])
gt_1 = raster1.GetGeoTransform()
rows = raster1.RasterYSize
cols = raster1.RasterXSize
ext_1 = GetExtent(gt_1,cols,rows)
array1 = np.array(raster1.GetRasterBand(1).ReadAsArray())





#Cria Matriz Multidimensional com todos os Rasters
def Stack(list_rasters,array1):
    n = len(list_rasters)

    stack = np.zeros((n,array1.shape[0],array1.shape[1]),np.float32)

    c=0
    for el in list_rasters:

        raster=''
        raster = gdal.Open(el)
        gt = raster.GetGeoTransform()
        cols = raster.RasterXSize
        rows = raster.RasterYSize
        ext = GetExtent(gt,cols,rows)
   
        if not ext == ext_1:
            print('FILE: '+el )
            print('EXT: '+str(gt[0])+str(gt[3]))
    
        array = np.array(raster.GetRasterBand(1).ReadAsArray())
        stack[c] = array
        c+=1
    
    return stack


#Extrai os pixels validos para um mês escolhido   
def getMonthsDatas(datas,points,listvalues,n):
    
    c=0
    soma=0
    meses = []
    values =[]
    valores_pixels = []
    for d in datas[1:]: 
        if d.month == n:
            meses.append(d)
            values.append(points[c])
            soma+=points[c]
    
        c+=1
    media = 'Null'
    stdev = 'Null'
    if not len(values)==0:
        media = soma/len(values)
        stdev = pstdev(values)
    b=0
    for d in datas:
        if d.month == n:
            valores_pixels.append(listvalues[b])
            print(listvalues[b])
            print(datas[b])
        b+=1    
        
    #print(listvalues)
    x = {'meses':meses, 'valores_diferencas':values , 'media': media, 'stdev':stdev,'valores_pixels': valores_pixels}
    
    return x








# geradorDeGraficos
def getpointGraph(i,j,stack,gt,enter,lastRaster,MesRaster):

    # enter =  1 - plotar grafico inteiro
    # enter = 2 - plotar grafico pelo mes
    # enter = 3 - plotar grafico pelas estacoes
    
    dataValid = []
    ndviValid = []
    band_number = stack.shape[0]
    Xgeo = gt[0] + i*gt[1] + j*gt[2]
    Ygeo = gt[3] + i*gt[4] + j*gt[5]
    
    pixelValue = lastRaster[j][i]
    
    
    #pega os valores validos com as datas validas para cada pixel
    
    for c in range(band_number):
        if stack[c][j][i] >=-1 and stack[c][j][i]<=1:
            ndviValid.append(stack[c][j][i])
            dataValid.append(datas[c])
     
           

    # pega variacao do ndvi
    diferenca_ndvi = []
    for c in range(len(ndviValid)):
        if c<=len(ndviValid)-2:
            ndvi1 = ndviValid[c]
            ndvi2 = ndviValid[c+1]
            diferenca_ndvi.append(ndvi2-ndvi1)
    
    #pega variacao das datas 
    diferenca_data = []
    for d in range(len(dataValid)):
        if d<=len(dataValid)-2:
            data1 = dataValid[d]
            data2 = dataValid[d+1]
            dif_data = (data2-data1).total_seconds()/86400
            diferenca_data.append(dif_data)
    
    taxa_ndvi = []
    for c in range(len(diferenca_ndvi)):
        ndvi = diferenca_ndvi[c]
        dif_data = diferenca_data[c]
        
        
        taxa_ndvi.append(ndvi/dif_data)
    
    jan= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,1)
    fev= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,2)
    mar= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,3)
    abr= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,4)
    mai= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,5)
    jun= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,6)
    jul= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,7)
    ago= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,8)
    set= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,9)
    out= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,10)
    nov= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,11)
    dez= getMonthsDatas(dataValid,taxa_ndvi,ndviValid,12)
    
    Mes = getMonthsDatas(dataValid[1:],taxa_ndvi,ndviValid,MesRaster)
    
    
    meses = [jan,fev,mar,abr,mai,jun,jul,ago,set,out,nov,dez]
    
    
    def plot_all():
      #  plotar grafico com a serie temporal inteira de pixels validos
        plt.plot(dataValid[1:],taxa_ndvi)     
        plt.grid(True)
        print(len(dataValid))
        #for el in dataValid[1:]:
        #    if el.month == 11:
        #        print(el)
        
        #coordenada = ('{} : {} , {} : {}').format(i,Xgeo,j,Ygeo)        
        #plt.title(coordenada)
        #plt.show()
        print('''
        
        next point 
        
        
        ''')
        return None
        
    def plot_mes(meses,jan):
        
        MesesNomes = ['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ']
        medias = []
        Sdtevs = []
        quantidades=[]
        lastRaster=[]
        p = 0
        k=1
        months = []
        for m in meses:
            medias.append(m['media'])
            if not m['stdev'] == 'Null':
                Sdtevs.append(m['media']-m['stdev']*k)
                quantidades.append(len(m['valores_diferencas']))

              
           
            
 
        plt.plot(MesesNomes,Sdtevs,color='blue')
        plt.plot(MesesNomes,medias,color = 'green')
        #plt.plot(MesesNomes,lastRaster,color='red')
        plt.legend('MDR')
        #plt.grid('True')
        #plt.title('{} , {}'.format(Xgeo,Ygeo))
        #plt.show()
        #print(MesRaster)
        #print(type(Mes))
        print(Mes['valores_pixels'])
        return Mes
        
        
    def plot_estaco():
        
        estacaos = ['VERAO','OUTONO','INVERNO','PRIMAVERA']
        verao = (jan['media']+fev['media']+mar['media'])/3
        outono = (abr['media']+mai['media']+jun['media'])/3
        inverno = (jul['media']+ago['media']+set['media'])/3
        primavera = (out['media']+nov['media']+dez['media'])/3
        
        plt.plot(estacaos,[verao,outono,inverno,primavera])
        plt.show()
    
    
    if len(taxa_ndvi)>0:
            
            if enter =='1':
                return True , plot_all()
            
            elif enter=='2':
                return True , plot_mes(meses,Mes)
            
            elif enter == '3':
                return True ,    plot_estaco()
               
    else :
        return False , []

   
        
    
def getMonths(datas,path,list):
    estacao = []
    for el in datas:
        for c in list:
            if el.month==c:
                data = el
                for r in rasters:
                    if r['data']== el:
                        estacao.append(r['file'])
    return estacao




lastRaster = gdal.Open(rasters_ordem[-1])
gt_2 = lastRaster.GetGeoTransform()
rows_2 = lastRaster.RasterYSize
cols_2 = lastRaster.RasterXSize
ext_2 = GetExtent(gt_1,cols,rows)


            
def GraficoAleatorio(listFiles,array1,array2):
 
    stack = Stack(listFiles,array1)
    c = 0
    while c<20:
        x = randint(0,540)
        y = randint(0,410)
        if array2[y][x] >=-1 and array2[y][x]<=1:    
            #print(array2[y][x])
            graph = getpointGraph(x,y,stack,gt_1,'2',array_2,12)            
            print(len(graph[1]['meses']))
        
            
            c+=1
#GraficoAleatorio(rasters_ordem,array1,array_2)

stack = Stack(rasters_ordem,array1)
array_2 = stack[-1]

FinalArray = np.zeros((array1.shape[0],array1.shape[1]),np.float32)


for i in range(100,120):
    for j in range(100,120):
        if array_2[j][i] >=-1 and array_2[j][i]<=1:                
            graph = getpointGraph(i,j,stack,gt_1,'2',array_2,4)
            stdev = (graph[1]['stdev'])
            media = (graph[1]['media'])
            sensor =[] 
            print(media, stdev)
            if type(graph[1]['stdev']) == float:
                if (media-stdev)*0.001 > array_2[j][i] :
                    FinalArray[j][i] = 1
                                
                elif (media-stdev)*0.001<array_2[j][i]:
                    FinalArray[j][i] = 0
                    #print('FALSE')
        elif array_2[j][i]<-1:
            FinalArray[j][i] = 2
                    
'''                

i = 100
j = 100
graph = getpointGraph(i,j,stack,gt_1,'2',array_2,4)
stdev = (graph[1]['stdev'])
media = (graph[1]['media'])
#for c in range(0,12):
print(graph[1]['valores_pixels'])
print(stack[-1][i][j])
print(array_2[i][j])


#plt.imshow(FinalArray)
#plt.show()    

