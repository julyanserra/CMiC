#Justin Chan and Julian Serra
#Claremont Mckenna College - CS181
#CMiC Image Compressor

#some imports
import os
import hashlib
import sys
import scipy
import scipy.ndimage
import numpy as np
import PIL
import pywt
import argparse
import json
import struct
np.set_printoptions(threshold='nan')

#wrapper for showing np.array() as an image
def show(image):
    scipy.misc.toimage(image).show()

#open the image and take the 2D DWT
#After that, it's up to you!
def differential(LL):
    arry = np.array(LL) 
    arry1 = np.round(arry).astype(int)
    arry2 = np.insert(arry1,0,0.0) 
#is this only adding a zero to the front of the array??
    
    return np.diff(arry2)


#huffuffman encoder methods
  
def getStats(array): 
    d= {} 
    for item in array:
        if item not in d: 
            d[item]=1
        else:
            d[item]=d[item] +1
    return d   
  
def listConvert(input):
    convertedArray = []
    for key, value in input.iteritems(): 
        convertedArray.append((key, value))
    return convertedArray
  
def huff(lst,side,code): 
    #print lst
    
    if (isinstance(lst, list)) and len(lst) == 1:
        #print 'godsaveus'
        code.append((lst,side))

    elif (isinstance(lst, np.int64)) and lst.size == 1:
        code.append((lst,side))
        #print 'godsaveusnpint'
    else:
        left = huff(lst[0], side + "0", code)
        right = huff(lst[1], side + "1", code)

def encode(items):
    #print items
    lst = sorted(items, key = lambda y: y[1])
    #print lst   
    while len(lst) >1:
        z = lst[0]
        y = lst[1]
        v = z[1] + y[1]
        k = [z[0], y[0]]
        lst = lst[2:]+[(k,v)]
        lst = sorted(lst,key = lambda y: y[1]) 

    tree = lst[0][0]
    code = []
    huff(tree,"",code)
    return dict(code)
  
def packer(dict, list):
    r=""
    for i in range (len(list)):
       r += dict[list[i]]
    return r

def padder(binarystring):
    i = 0
    for c in binarystring:
        i+=1
    if(i%8==0):
        return binarystring
    else:
        d=i%8
        f=8-d
        pad = f*"0"
        binarystring += pad 
    #print i
    return binarystring

def headerMaker(file,output, height, width, wavelet, quantization, alpha):
    size = os.path.getsize(file)
    hash = hashlib.md5(open(file,'rb').read()).hexdigest()
    newheader = {"Version": "CMiCV1", "height": height, "width": width, "wavelet":wavelet, "q": quantization}
    compressed_file = open(output, "wb")
    compressed_file.write(json.dumps(newheader)+"\n")
    compressed_file.write(json.dumps(alpha)+"\n")
    return compressed_file

def stringToData(string, out):
    for i in range(0, len(string),8):
        s=0
        int_str = string[i:i+8]
        for j in range(7,-1,-1):
            s+= pow(2,j)*int(int_str[7-j])
        out.write(struct.pack("B",s))
 

 ### closing huffman input

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image")
    parser.add_argument("output_file")
    parser.add_argument("--wavelet", help="wavelet name to use. Default=haar", default="db9")
    parser.add_argument("--quantize", help="quantization level to use. Default=4", type=int, default=4)
    args = parser.parse_args()

    input_file_name = args.input_image
    try:
        im = scipy.ndimage.imread(input_file_name, flatten=True, mode="L")
        print "Attempting to open %s..." % input_file_name
    except:
        print "Unable to open input image. Qutting."
        quit()
    #show(im)
    #get height and width
    (height, width) = im.shape
    wavelet = args.wavelet
    q = args.quantize
    file = args.input_image 
    out = args.output_file

    LL, (LH, HL, HH) = pywt.dwt2(im, wavelet, mode='periodization')

    flatLL = LL.flatten()
    
    
    LHq = LH/q
    HLq = HL/q
    HHq = HH/q
    flatLHq = LHq.flatten()
    flatHLq = HLq.flatten()
    flatHHq = HHq.flatten()
    diffArray = differential(flatLL)
    LLint = diffArray
    LHint = np.round(flatLHq).astype(int)
    HLint = np.round(flatHLq).astype(int)
    HHint = np.round(flatHHq).astype(int)
    
    Huffready = list(np.concatenate([LLint,LHint,HLint,HHint]))
    
    #print Huffready
    
    '''the following block of code will let you look at the decomposed image. Uncomment it if you'd like
    '''
    dwt = np.zeros((height, width))
    dwt[0:height/2, 0:width/2] = LL
    dwt[height/2:,0:width/2] = HL
    dwt[0:height/2, width/2:] = LH
    dwt[height/2:,width/2:] = HH
    show(dwt)
     
  
    ##main for huff 
    d = getStats(Huffready) 
    
    converted = listConvert(d)
    #print type(converted)
    #print converted
    
    #acquire huffman codes, list in dictionary
    alpha = encode(converted) 
    #print alpha
    
    #print type(Huffready)
    #substitute characters for their codes in string 
    binstring = packer(alpha,Huffready) 
    binfinal = padder(binstring) 
    #print binfinal
    #print json.dumps({"String ": binfinal})


    #making header for new compressed file
    compressed_file= headerMaker(file, out, height, width, wavelet, q, alpha)

    #convert to binary data
    stringToData(binfinal, compressed_file)
  
  

if __name__ == '__main__':
    main()
