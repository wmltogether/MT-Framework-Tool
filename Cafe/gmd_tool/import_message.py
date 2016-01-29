# -*- coding: utf-8 -*-
from libMT_Framework import dir_fn
import codecs,os,struct
from StringIO import StringIO

def makestr(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index,line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index+i >= num:
                    break
                if '####' in lines[index+i]:
                    break
                string += lines[index+i]
                i += 1
            string_list.append(string[:-4])
    return string_list, head_list
def import_gmd(fn):
    endian = ">"
    original_name = fn[:-4]
    text = codecs.open('cn-text\\%s'%fn,'rb','utf-16')
    q = open(original_name.replace("__" , "\\"),'rb')
    fp =StringIO()
    fp.write(q.read())
    q.close()
    fp.seek(0)
    fp.seek(0x14)
    pnums = struct.unpack('>I',fp.read(4))[0]
    tnums = struct.unpack('>I',fp.read(4))[0]
    fp.seek(0x20)
    size = struct.unpack('>I',fp.read(4))[0]
    fp.seek(0x24)
    name_len = struct.unpack('>I',fp.read(4))[0]
    name = fp.read(name_len)
    null = fp.read(1)
    plist = []
    q_ofs = fp.tell()
    for i in xrange(pnums):
        pid = fp.read(4)
        pstr = fp.read(4)
        pstr2 = fp.read(4)
        pstr3 = fp.read(4)
        pstr4 = fp.read(4)
        if not pstr == '\xff\xff\xff\xff':
            plist.append((struct.unpack(endian+'I',pid)[0],struct.unpack(endian+'I',pstr3)[0]))
    unk = fp.read(0x400)
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
    fp.truncate(q_ofs)
    fp.seek(q_ofs)
    lines = text.readlines()
    string_list, head_list = makestr(lines)
    text_string_dict = {}
    for i in xrange(len(string_list)):
        string = string_list[i]
        string = string.replace('{PAGE}\r\n','<PAGE>')
        data = string.encode('utf-8')
        fp.write(data)
        fp.write('\x00')
    end_ofs = fp.tell()
    size = end_ofs - q_ofs
    fp.seek(0x20)
    fp.write(struct.pack('>I',size))
    finaldata = fp.getvalue()
    fp.flush()
    import_name = original_name.replace('assets\\','import\\')
    if not os.path.exists("import\\" + '\\'.join(import_name.split('__')[:-1])):
        os.makedirs("import\\" + '\\'.join(import_name.split('__')[:-1]))
    dest = open("import\\%s"%import_name.replace("__" ,"\\"),'wb')
    dest.write(finaldata)
    dest.close()

def main():
    fl=os.listdir('cn-text')
    for fn in fl:
        import_gmd(fn)
if __name__ == "__main__":
    main()
