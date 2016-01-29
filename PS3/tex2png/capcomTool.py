import struct
import sys
import os,glob
from cStringIO import StringIO
from PIL import Image
from GIDecode import decodeDXT,encodeDXT,decodeDXT5


class TEX:
    def __init__(self , fname):
        self.filename = fname
        self.sig = "\x00\x58\x45\x54"
        self.width = 0
        self.height = 0
        self.dxt_type = ""
        self.global_dxtc_type = {0x18:"DXT5",0x14:"DXT1",0x19:"DXT1A",0x2B:"RBxG"}
        self.texture_offset = 0x14

    def parseHeader(self):
        fp = open(self.filename , "rb+")
        sig = fp.read(4)
        if sig != self.sig:
            fp.close()
            print("error: Not a TEX file")
            return None
        fp.seek(0x8)
        tmp = "\x00" +  fp.read(3)
        self.width = ((struct.unpack(">I" , tmp)[0]) & 0xfff) * 4 #lower 12bit * 4 is width
        self.height = ((struct.unpack(">I" , tmp)[0])>> 12) * 2#higher 12bit * 2 is height
        fp.seek(0xe)
        cdxt_type = ord(fp.read(1))
        if cdxt_type in self.global_dxtc_type:
            self.dxt_type = self.global_dxtc_type[cdxt_type]
        fp.seek(0x10)
        self.texture_offset = struct.unpack(">I" , fp.read(4))[0]
        fp.close()

    def unpackTextureFiles(self , dest_folder):
        self.parseHeader()
        print("Texture:%dx%d"%(self.width ,self.height))
        if self.width == 0 or self.dxt_type == "":
            return None
        fp = open(self.filename , "rb")
        fp.seek(self.texture_offset)
        data_chunk = fp.read()
        img_raw = self.imageDecode(data_chunk ,self.dxt_type )
        if img_raw != None :
               image = Image.frombytes('RGBA', (self.width, self.height), img_raw, 'raw', 'RGBA')
               filename = self.filename.replace("\\" , "__")
               if not self.dxt_type == "RBxG":
                   image.save("%s\\%s.%s.png"%(dest_folder , filename , self.dxt_type))
               else:
                   pixel_list = list(image.getdata())
                   base_list = []
                   mask_list = []
                   for (r,g,b,a) in pixel_list:
                       base_list.append((a,a,a,g))
                       mask_list.append((r,b,0,255))
                   imMask = Image.new('RGBA', (self.width, self.height))
                   imMask.putdata(tuple(mask_list))
                   image.putdata(tuple(base_list))
                   image.save("%s\\%s.%s.png"%(dest_folder , filename , self.dxt_type))
                   imMask.save("%s\\%s.%s.png"%(dest_folder , filename , "MASK"))
                   
        return None

    def reimportTextureFiles(self , import_folder , output_folder):
        print(self.filename)
        self.parseHeader()
        fp = open(self.filename , "rb")
        fBuffer = StringIO()
        fBuffer.write(fp.read())
        fp.close()
        fBuffer.seek(0)
        im = Image.open("%s\\%s.%s.png"%(import_folder ,\
                                                  self.filename.replace("\\" , "__") ,\
                                                  self.dxt_type)).convert('RGBA')
        if self.dxt_type == "RBxG":
            print("got RBxG , fixing RGBA data")
            imMask = Image.open("%s\\%s.%s.png"%(import_folder ,\
                                                  self.filename.replace("\\" , "__") ,\
                                                  "MASK")).convert('RGBA')
            mask_list = imMask.getdata()
            base_list = im.getdata()
            new_list = []
            for n in xrange(len(base_list)):
                r0,g0,b0,a0 = base_list[n]
                r1,g1,b1,a1 = mask_list[n]
                new_list.append((r1,a0,g1,g0))
            im.putdata(tuple(new_list))
        dxtc_data = self.imageEncode(self.width , self.height , im , self.dxt_type)
        print("compressed:%08x"%len(dxtc_data))
        fBuffer.seek(self.texture_offset)
        fBuffer.write(dxtc_data)
        ftx_data = fBuffer.getvalue()
        dir_name = os.path.dirname("%s\\%s"%(output_folder ,self.filename))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        dest = open("%s\\%s"%(output_folder ,self.filename) , "wb")
        dest.write(ftx_data)
        dest.close()


    def imageDecode(self , data_chunk , dxtc_type):
        if dxtc_type == "DXT1":
            img_raw = decodeDXT(self.width , self.height , data_chunk ,dxtc_type)
        if dxtc_type == "DXT3":
            img_raw = decodeDXT(self.width , self.height , data_chunk ,dxtc_type)
        if dxtc_type == "DXT5":
            img_raw = decodeDXT(self.width , self.height , data_chunk ,dxtc_type)
        if dxtc_type == "RBxG":
            img_raw = decodeDXT(self.width , self.height , data_chunk ,"DXT5")
        
        return img_raw


    def imageEncode(self , width , height , im , dxtc_type):
        dxt_data = ""
        if dxtc_type == "DXT1":
            dxt_data = encodeDXT(width , height ,im ,"DXT1")

        if dxtc_type == "DXT3":
            dxt_data = encodeDXT(width , height ,im ,"DXT3")

        if dxtc_type == "DXT5":
            dxt_data = encodeDXT(width , height ,im ,"DXT5")
            
        if dxtc_type == "RBxG":
            dxt_data = encodeDXT(width , height ,im ,"DXT5")
        return dxt_data


def dir_fn(adr ,ext_name):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            if ext.lower() in ext_name:
                dirlst.append(adrlist)
    return dirlst

def export(name):
    print(name)
    fname = name
    ftex = TEX(fname)
    dest_folder = "images"
    if not os.path.exists(dest_folder):os.makedirs(dest_folder)
    ftex.unpackTextureFiles(dest_folder)

def gogoftx(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    fl = dir_fn(folder , ["tex"])
    for fn in fl:
        export(fn)

def import_data(name):
    fname = name.replace("__" , "\\")
    ftex = TEX(fname)
    ftex.reimportTextureFiles("cnpng" , "import")


def gogoImportFxt(folder):
    print("current folder:%s"%folder)
    if not os.path.exists(folder):
        os.makedirs(folder)
    fl = dir_fn(folder , ["png"])
    need_patched_files = []
    for fn in fl:
        o_ftx_name = ".".join(fn.split("\\")[-1].split(".")[:-2])
        if not o_ftx_name in need_patched_files:
            need_patched_files.append(o_ftx_name)
        else:
            pass
    print("searching :%d files need patch"%len(need_patched_files))
    for subFilename in need_patched_files:
        import_data(subFilename)


def main():
    args = sys.argv
    if len(args) <= 2:
        print("usage : ")
        print("capcomToold TEX_FOLDER_NAME convert tex to png")
        print("capcomToolc PNG_FOLDER_NAME convert PNG to tex")
    elif len(args) >= 3:
        command = args[1]
        print(command)
        if command == "d":
            TEX_FOLDER_NAME = args[2]
            print("current Export Folder:%s"%TEX_FOLDER_NAME)
            gogoftx("%s"%TEX_FOLDER_NAME)
        elif command == "c":
            TEX_FOLDER_NAME = args[2]
            print("current Import Folder:%s"%TEX_FOLDER_NAME)
            gogoImportFxt("%s"%TEX_FOLDER_NAME)
        else:
            print("error :invalid args given")
            print("usage : ")
            print("capcomToold TEX_FOLDER_NAME convert tex to png")
            print("capcomToolc PNG_FOLDER_NAME convert PNG to tex")
    else:
        print("error :invalid args")
        print("usage : ")
        print("capcomToold TEX_FOLDER_NAME convert tex to png")
        print("capcomToolc PNG_FOLDER_NAME convert PNG to tex")


if __name__ == "__main__":
    main()







