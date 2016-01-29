import codecs,struct,os
from cStringIO import StringIO
from PIL import Image
from GIDecode import decodeDXT,encodeDXT
def math_xy(char_code,x,y,char_width,char_height,pid):
    unicode_char = struct.pack('H',char_code).decode("utf-16")
    char_bin = struct.pack('>I',char_code)
    pid_bin = chr(pid)

    xybin = struct.pack('>I',((x*16)<<8)|y)[1:]
    nullbin = chr(0)

    chr_wh_bin = struct.pack('>I',((char_width*16)<<8)|char_height)[1:]
    rw_bin = struct.pack(">H" , char_width*16)
    nullbin2 = struct.pack(">H" , 0)
    return char_bin+pid_bin+xybin+nullbin+chr_wh_bin+rw_bin+nullbin2

def csv2data(csv_name):
    data_list = []
    fp = open(csv_name , "rb")
    lines = fp.readlines()
    for line in lines:
        if "," in line:
            line = line.replace("\r\n" , "")
            char_code , x, y ,char_width , char_height , pid = line.split(",")[:6]
            char_code = int(char_code)
            x = int(x)
            y = int(y)
            char_width = int(char_width)
            char_height = int(char_height)
            pid = int(pid) - 1
            data = math_xy(char_code,x,y,char_width,char_height,pid)
            data_list.append(data)
    fp.close()
    return data_list

def build_font_gfd(original_name, o_header_size , csv_name , dest_gfd_name, char_width):
    fp = open(original_name , "rb")

    header = fp.read(o_header_size)
    v0 = fp.read(4)
    name = struct.unpack(">I" , v0)[0]
    v1 = fp.read(name)
    v2 = fp.read(1)
    header = header + v0 + v1 + v2
    fp.close()
    data_list = csv2data(csv_name)
    dest = open(dest_gfd_name , "wb")
    dest.write(header)
    dest.write("".join(data_list))
    dest.seek(0x14)
    dest.write(struct.pack(">I" ,char_width ))
    dest.seek(0x1c)
    dest.write(struct.pack(">I" ,len(data_list)))
    dest.close()
    return None
def imageEncode(width , height , im , dxtc_type):
    dxt_data = ""
    if dxtc_type == "DXT1":
        dxt_data = encodeDXT(width , height ,im ,"DXT1")

    if dxtc_type == "DXT3":
        dxt_data = encodeDXT(width , height ,im ,"DXT3")

    if dxtc_type == "DXT5":
        dxt_data = encodeDXT(width , height ,im ,"DXT5")

    return dxt_data
def png2tex(png_name , tex_name , width):
    im = Image.open("%s"%(png_name)).convert('RGBA')
    data = imageEncode(width , width ,im , "DXT5")
    dest = open(tex_name , "wb")
    if width == 2048:
        dest.write("\x00\x58\x45\x54" +
                   "\x20\x00\x20\x9d" +
                   "\x40\x02\x00\x01" +
                   "\x00\x01\x18\x01" +
                   "\x00\x00\x00\x14")
    if width == 1024:
        dest.write("\x00\x58\x45\x54" +
                   "\x20\x00\x20\x9d" +
                   "\x20\x01\x00\x01" +
                   "\x00\x01\x18\x01" +
                   "\x00\x00\x00\x14")
    dest.write(data)
    dest.close()


def batch_mode():
    build_font_gfd( "origin\\font_eng.bin", \
                    0x34,\
                    "font_eng\\font_eng.csv", \
                    "build\\Font_eng.bin",\
                    26)
    png2tex("font_eng\\font.0.Png" , "build\\font_eng_00_ID.tex" , 2048)

    return None

batch_mode()
