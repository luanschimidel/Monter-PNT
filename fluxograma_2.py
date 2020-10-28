#Codigo_final
import tarfile
from shutil import copyfile
def descompactar(file,out_path):
    #if os.path.isdir(out_path):
    #    pass
    #else :
    x = tarfile.open(file)
    x.extractall(out_path)
    return None
    
def StringToRaster(string):
    if isinstance(string,basestring):
        fileInfo = QFileInfo(string)
        basename  = fileInfo.baseName()
        path = fileInfo.filePath()
        if (basename and path):
            raster = QgsRasterLayer(path,basename)
            if not raster.isValid():
                print('filed to load')
                return
        else:
            print('Deu erro na string')
            return
    return raster
    

def clipFile(raster,shapefile,output_clip):
    if not os.path.isfile(output_clip):    
        processing.run("gdal:cliprasterbymasklayer", 
        {
        'INPUT':raster,
        'MASK':shapefile,
        'SOURCE_CRS':None,
        'TARGET_CRS':None,
        'NODATA':None,
        'ALPHA_BAND':False,
        'CROP_TO_CUTLINE':True,
        'KEEP_RESOLUTION':False,
        'SET_RESOLUTION':False,
        'X_RESOLUTION':None,
        'Y_RESOLUTION':None,
        'MULTITHREADING':False,
        'OPTIONS':'',
        'DATA_TYPE':0,
        'EXTRA':'',
        'OUTPUT':output_clip
        })

    return None





#Funçãp usada para extrair dados usados na correção radiometrica    

def ExtraiDados(mtl,n):
    file = mtl
    import math
    x = open(file,'r')
    A = x.readlines()
    for l in A:
        if 'REFLECTANCE_MULT_BAND_'+n in l:
            M = (l.split('=')[1])
            M = float(M)
           
        
        if 'REFLECTANCE_ADD_BAND_'+n in l:
            A = (l.split('=')[1])
            A = float(A)
           
        
        if 'SUN_ELEVATION' in l:
            s = l.split('=')[1]
            s = float(s)
            S = math.sin(math.radians(s))
           
 
    return M,A,S

def Rad_Correct(band1,metadata,output):
   
    entry = []
    if os.path.isfile(output):
        return 'Já é arquivo'
    
    
    else:
        
        band1 = QgsRasterLayer(band1)
        raster = QgsRasterCalculatorEntry()
        M,A,S =  ExtraiDados(metadata,'5')        
        M = str(M)
        A = str(A)
        S = str(S)
        
        
        raster.ref = 'band1@1'
        raster.raster = band1
        raster.bandNumber = 1
        entry.append(raster)
    
        
        calc = QgsRasterCalculator('((band1@1 * {})+{})/{}'.format(M,A,S),output, 'GTiff',band1.extent() , band1.width(),
        band1.height(),entry)
        x = calc.processCalculation()
    
    return None


#reclassify é usado para mascara de nuvem e para mascara de sombra
def reclassify(input,output,rules):
    if not os.path.isfile(output):
        processing.run("grass7:r.reclass", 
        {'input':input,
        'rules':rules,
        'txtrules':'',
        'output':output,
        'GRASS_REGION_PARAMETER':None,
        'GRASS_REGION_CELLSIZE_PARAMETER':0,
        'GRASS_RASTER_FORMAT_OPT':'',
        'GRASS_RASTER_FORMAT_META':''})
    else:
        pass
    
    return None
    

# Função usada para multiplicar os ndvis pelas mascaras
def product_file(band,mask,output):
    if not os.path.isfile(output):
        mask = QgsRasterLayer(mask) 
        band = QgsRasterLayer(band) 
        entry = []
        
        band1 = QgsRasterCalculatorEntry()
        band1.ref = 'band1@1'
        band1.raster = band
        band1.bandNumber = 1
        entry.append(band1)
    
        band2 = QgsRasterCalculatorEntry()
        band2.ref = 'band1@2'
        band2.raster = mask
        band2.bandNumber = 1
        entry.append(band2)    
    
        calc = QgsRasterCalculator(('band1@1*band1@2 '),output, 'GTiff',band.extent() , band.width(),
        band.height(),entry)
        calc.processCalculation()
    else:
        pass


def stats_band(raster):
    r = QgsRasterLayer(raster)
    stats = r.dataProvider().bandStatistics(1,QgsRasterBandStats.All)
    min = stats.minimumValue
    max = stats.maximumValue
    
    return min,max

def translate(input,output,max , min):
    extra = '-ot Byte -scale {} {} -co TFW=YES'.format(min,max)
    processing.run("gdal:translate", {'INPUT':input,
    'TARGET_CRS':None,
    'NODATA':None,
    'COPY_SUBDATASETS':False,
    'OPTIONS':'',
    'EXTRA':extra,
    'DATA_TYPE':0,
    'OUTPUT':output})
    return None
    
def Raster_GRIR(Green,Red,IR,output):
    if not os.path.isfile(output):
        green = QgsRasterLayer(Green) 
        red = QgsRasterLayer(Red)
        ir = QgsRasterLayer(IR)
        entry = []
        
        band1 = QgsRasterCalculatorEntry()
        band1.ref = 'band1@1'
        band1.raster = green
        band1.bandNumber = 1
        entry.append(band1)
    
        band2 = QgsRasterCalculatorEntry()
        band2.ref = 'band1@2'
        band2.raster = red
        band2.bandNumber = 1
        entry.append(band2)    
        
        band3 = QgsRasterCalculatorEntry()
        band3.ref = 'band1@3'
        band3.raster = ir
        band3.bandNumber = 1
        entry.append(band3)    
        
        calc = QgsRasterCalculator((' (band1@1+band1@2+band1@3)/3 '),output, 'GTiff',green.extent() , green.width(),
        green.height(),entry)
        calc.processCalculation()

def filter(input,output):

    processing.run("saga:userdefinedfilter", {'INPUT':input,
    'FILTER':None,
    'FILTER_3X3':[-0.125,-0.125,-0.125,-0.125,4,-0.125,-0.125,-0.125,-0.125],
    'RESULT':output})
    return None



def Create_Ndvi(red_band,infra_band,extent,output):
    
    entry = []
    if os.path.isfile(output):
        pass
    
    else:
        
        red_band = QgsRasterLayer(red_band)
        infra_band = QgsRasterLayer(infra_band)
        extent = red_band
        
        red = QgsRasterCalculatorEntry()
        red.ref = 'band1@1'
        red.raster = red_band
        red.bandNumber = 1
        entry.append(red)
    
        infra = QgsRasterCalculatorEntry()
        infra.ref = 'band2@1'
        infra.raster = infra_band
        infra.bandNumber = 1
        entry.append(infra)
    
        calc = QgsRasterCalculator('(band2@1 - band1@1) / (band2@1 + band1@1)',output, 'GTiff',extent.extent() , extent.width(),
        extent.height(),entry)
        calc.processCalculation()
    
    return None


def main():
    
    compactas = r'C:\Users\ximis\workspace\pnt\imagens_landsat\landsat8\processamento_completo\compactas'
    descompactas = r'C:\Users\ximis\workspace\pnt\imagens_landsat\landsat8\processamento_completo\descompactas'     
    path = os.path.dirname(compactas)
    
    #pastas dos processamentos
    clip_dir = path+'\clip'
    sem_nuvens = path+'\sem_nuvens'
    sem_sombras = path+'\sem_sombras'
    TOA = path+'\Toa'
    arquivos_sombra = path+'\pasta_sombras'
    
    # shapefile parque
    shapefile_parque =r'C:\Users\ximis\workspace\pnt\PNT_ZA_Limites_mask\pnt_za_limite.shp' 
    
    #Arquivos txt para função reclass
    cloud_mask = r'C:\Users\ximis\workspace\pnt\imagens_landsat\clouds.txt'
    shadow_mask = r'C:\Users\ximis\workspace\pnt\imagens_landsat\shadow_GRIR8BITS.txt'
    
    ndvi =r'C:\Users\ximis\workspace\pnt\imagens_landsat\landsat8\processamento_completo\ndvi'
    for file in os.listdir(compactas):
        Tar_file = compactas+'/'+file
        outpath = descompactas+'/'+file[:-7]
        if not os.path.isdir(outpath):
            descompactar(Tar_file,outpath)
    
    for file in os.listdir(descompactas):
        bandas = descompactas+'/'+file
        for banda in os.listdir(bandas):
            if not os.path.isdir(clip_dir+'/'+file):
                os.mkdir(clip_dir+'/'+file)
            if banda[-4:] == '.TIF':
                input_clip = bandas+'/'+banda
                output_clip = clip_dir +'/'+file+'/'+banda 
                clipFile(input_clip,shapefile_parque,output_clip)
            else:
                x =(bandas+'/'+banda)                
                outfile = clip_dir +'/'+file+'/'+banda
                if not os.path.isfile(outfile):
                    copyfile(x,outfile)
    
    for clip in os.listdir(clip_dir):
        #Cria mascara de nuvem
        BQA = clip_dir+'/'+clip+'/'+clip+'_BQA.TIF'
        BQA_reclassificada = clip_dir+'/'+clip+'/'+'cloud_mask.TIF'
        if not os.path.isfile(BQA_reclassificada):
            reclassify(BQA,BQA_reclassificada,cloud_mask)
            
        #aplica mascara de nuvem em todos os arquivos 
        for b in os.listdir(clip_dir+'/'+ clip):
            if b.endswith('.TIF') and 'BQA' not in b:
                input_file = clip_dir+'/'+'/'+clip+'/'+b
                output_dir = sem_nuvens + '/' + clip
                if not os.path.isdir(output_dir):
                    os.mkdir(output_dir)
                output_file = output_dir+'/'+ b
                product_file(input_file,BQA_reclassificada,output_file)
            
            elif b.endswith('.txt'):
                input_file = clip_dir+'/'+'/'+clip+'/'+b
                output_file = output_dir+'/'+ b
                copyfile(input_file,output_file)
    
    for files in os.listdir(sem_nuvens):
        mtl = sem_nuvens+'/'+files+'/'+files+'_MTL.txt'
        ExtraiDados(mtl,'4')
        output_toa = TOA+'/'+files
        
    #Faz a correção radiometrica    
        if not os.path.isdir(output_toa):
            os.mkdir(output_toa)
        for file in os.listdir(sem_nuvens+'/'+files):
            if file.endswith('.TIF'):
                input_toa = sem_nuvens+'/'+files+'/'+file
                output_Toafile = output_toa+'/'+file
                Rad_Correct(input_toa,mtl,output_Toafile)
                
            elif b.endswith('.txt'):
                input_file = sem_nuvens+'/'+files+'/'+file
                output_file = output_toa+'/'+file
                copyfile(input_file,output_file)
    
    
    for file in os.listdir(TOA):

        
        pasta_sombras = arquivos_sombra+'/'+file 
        if not os.path.isdir(pasta_sombras):
            os.mkdir(pasta_sombras)
        
        #  CONVERSAO DOS RASTERS PARA 8 bits
        B3= TOA+'/{}/{}'.format(file,file+'_B3.TIF')
        output_band3 = pasta_sombras+'/B3_sombras.TIF'
        min,max = stats_band(B3)
        translate(B3,output_band3,max,min)
        
        B4= TOA+'/{}/{}'.format(file,file+'_B4.TIF')
        output_band4 = pasta_sombras+'/B4_sombras.TIF'        
        min,max = stats_band(B4)
        translate(B4,output_band4,max,min)
        
        B5= TOA+'/{}/{}'.format(file,file+'_B5.TIF')
        output_band5 = pasta_sombras+'/B5_sombras.TIF'        
        min,max = stats_band(B5)
        translate(B5,output_band5,max,min)
        
        # GERA OS RASTERS DE COMPOSIÇÃO VERDE VEREMLHO E INFRAVERMELHO
        GRIR =  pasta_sombras+'/GRIR_band.TIF'
        if not os.path.isfile(GRIR):
            Raster_GRIR(output_band3,output_band4,output_band5,GRIR)
        
        # Passa  O FILTRO  DE SOMBRA        
        output_filter = pasta_sombras + '/filterGRIR.sdat'
        if not os.path.isfile(output_filter):
            filter(GRIR,output_filter)
        
        # GERA a MASCARA DE SOMBRA
        shadow = pasta_sombras+ '/shadow.TIF'

        reclassify(output_filter,shadow,shadow_mask)

        
        Red_clean = pasta_sombras +'/Red_noShadow.TIF'
        InfraRed_clean = pasta_sombras +'/InfraRed_noShadow.TIF'
        
        product_file(B4,shadow,Red_clean)
        product_file(B5,shadow,InfraRed_clean)
        
        mtl = (os.path.join(TOA,file,file+'_MTL.txt'))
        mtl_destiny = os.path.join(ndvi,file,file+'_MTL.txt')
        #NDVI
        Ndvi = ndvi+'/{}/{}_ndvi.TIF'.format(file,file)
        if not os.path.isdir(ndvi+'/'+file):
            os.mkdir(ndvi+'/'+file)
        Create_Ndvi(Red_clean,InfraRed_clean,Red_clean,Ndvi)
        copyfile(mtl,mtl_destiny)
        
   
        
        
main()
