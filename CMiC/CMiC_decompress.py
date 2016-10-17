#CMiC Reference Decoder
#CMiC Image Compressor Starter file
#first some imports

import sys
import scipy
import scipy.ndimage
import numpy as np
import PIL
import pywt
from collections import Counter
from heapq import merge
import re
import struct
import itertools
import json


def show(image):
	scipy.misc.toimage(image).show()

def main():
	#quantization factor. Might change

	try:
		input_file_name = sys.argv[1]
		print "Attempting to open %s..." % input_file_name
		input_file = open(sys.argv[1], 'rb')
	except:
		print "Unable to open input file. Qutting."
		quit()

	try:
		output_file_name = sys.argv[2]
		print "Attempting to open %s..." % output_file_name
		output_file = open(sys.argv[2], 'wb')
	except:
		print "Unable to open output file. Qutting."
		quit()

	header = json.loads(input_file.readline())
	code_dict = json.loads(input_file.readline())
	print header
	height = int(header['height'])
	width = int(header['width'])
	wavelet = header['wavelet']
	q = int(header['q'])
	decode_dict = {v : k for k, v in code_dict.iteritems()}
	#print decode_dict

	binary_data = input_file.read()
	binary_string = ""
	
	for byte in binary_data:
		binary_string += format(ord(byte),'08b')
	
	decoded_data = []
	
	while len(decoded_data) != 4*(0.5*height * 0.5*width):
		sub_str = ""
		i = 0
		while sub_str not in decode_dict:
			sub_str = binary_string[0:i]
			i=i+1
		decoded_data += [int(decode_dict[sub_str])]
		binary_string = binary_string[i-1:]

	print height, width
	LL = (np.cumsum(np.array(decoded_data[0:int(height/2 * width/2)]))).reshape(height/2, width/2)
	LH = (np.array(decoded_data[int(height/2 * width/2):2*int(height/2 * width/2)])*q).reshape(height/2, width/2)
	HL = (np.array(decoded_data[2*int(height/2 * width/2):3*int(height/2 * width/2)])*q).reshape(height/2, width/2)
	HH = (np.array(decoded_data[3*int(height/2 * width/2):4*int(height/2 * width/2)])*q).reshape(height/2, width/2)
	
	im = pywt.idwt2( (LL, (LH, HL, HH)), wavelet,mode='periodization' )
	show(im)
	scipy.misc.toimage(im).save(output_file)
if __name__ == '__main__':
	main()