# -*- coding: utf-8 -*-
import os,codecs,zlib,trace
import struct,traceback
from libMT_Framework import repack_arc,dir_fn
def main():
    if not os.path.exists('assets/'):
        os.makedirs('assets/')
    fl = dir_fn('assets')

    for fn in fl:
        repack_arc(fn)
if __name__=='__main__':
    try:
        main()
    except:
        traceback.print_exc()
    os.system('pause')
    os._exit(0)
