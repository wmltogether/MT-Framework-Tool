# -*- coding: utf-8 -*-
from libMT_Framework import dir_fn
import os,struct,codecs
global endian
endian = ">"
def export_gmd_msg():
    if not os.path.exists('assets/'):
        print('NO assets folder found,please put .gmd into assets folder')
        os.makedirs('assets/')
    if not os.path.exists('cn-text/'):
        print('NO assets folder found')
        os.makedirs('cn-text/')
    if not os.path.exists('en-text/'):
        print('NO assets folder found')
        os.makedirs('en-text/')
    if not os.path.exists('import/'):
        print('NO import folder found')
        os.makedirs('import/')
    fl=dir_fn('assets')
    a=0
    if len(fl) == 0:
        print('Please put gmd folder into "assets" ')
    for filename in fl:
        if not "_eng.gmd" in filename:continue
        print(filename)
        fp=open(filename,'rb')
        fp.seek(0x14)
        pnums = struct.unpack(endian+'I',fp.read(4))[0]
        tnums = struct.unpack(endian+'I',fp.read(4))[0]
        fp.seek(0x20)
        size = struct.unpack(endian+'I',fp.read(4))[0]
        fp.seek(0x24)
        name_len = struct.unpack(endian+'I',fp.read(4))[0]
        name = fp.read(name_len)
        null = fp.read(1)
        plist = []
        datalist = []
        for i in xrange(pnums):
            pid = fp.read(4)
            pstr = fp.read(4)
            if not pstr == '\xff\xff\xff\xff':
                plist.append((struct.unpack(endian+'I',pid)[0],struct.unpack(endian+'I',pstr)[0]))
        tmp_ofs = fp.tell()
        for i in xrange(len(plist)):
            (pid,p_addr) = plist[i]
            real_offset = p_addr - plist[0][1] + tmp_ofs
            fp.seek(real_offset)
            bstr = ""
            while True:
                b=fp.read(1)
                if b == '\x00':
                    break
                else:
                    bstr+=b
            string = bstr.decode('utf-8')
            #dest.write('#### control,%d ####\r\n%s\r\n\r\n'%(pid,string))
            q_ofs = real_offset + len(bstr) + 1
        datalist = fp.read().split('\x00')[:tnums]
        destname = "en-text\\%s"%(filename.replace("\\" , "__"))
        dfile=codecs.open(destname+'.txt','wb',encoding='utf-16')
        for i in xrange(len(datalist)):
            data = datalist[i]
            data = data.decode('utf-8')
            data = data.replace('<PAGE>','{PAGE}\r\n')
            dfile.write('#### %d ####\r\n%s\r\n\r\n'%(i,data))
        fp.close()
        dfile.close()
export_gmd_msg()
