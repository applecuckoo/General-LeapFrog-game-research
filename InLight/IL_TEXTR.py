import struct
import zlib
from PIL import Image
from io import BytesIO

def rgba5551_to_argb1555(rgba_data):
    argb_data = bytearray(len(rgba_data))  # Same length since it's still 16 bits per pixel
    for i in range(0, len(rgba_data), 2):
        # Extract the 16-bit pixel value
        pixel = (rgba_data[i] << 8) | rgba_data[i + 1]

        # Extract the RGBA components
        r = (pixel >> 11) & 0x1F  # Red: bits 15:11
        g = (pixel >> 6) & 0x1F  # Green: bits 10:6
        b = (pixel >> 1) & 0x1F  # Blue: bits 5:1
        a = pixel & 0x1        # Alpha: bit 0

        # Reassemble in ARGB1555 order
        argb_pixel = (a << 15) | (r << 10) | (g << 5) | b

        # Store the ARGB1555 pixel value
        argb_data[i] = argb_pixel >> 8
        argb_data[i + 1] = argb_pixel & 0xFF

    return argb_data

filename = (input("What is the name of your file (leave out the .tex extension): "))

with open((filename + ".tex"), "rb") as file:
    magic = struct.unpack("<8s", file.read(8))
    if magic[0] != b'IL_TEXTR':
        raise ValueError("Magic check failed: not an IL_TEXTR file!")
    unknown1, bytelayout, width, height, zsize, unknown2, unknown3 = struct.unpack("<7I", file.read(28))
    print(width, height)
    imagedata = zlib.decompress(file.read())
    if bytelayout == 1:
        print("RGBA4444")
        rawimage = Image.frombytes("RGBA", (width, height), imagedata, "raw", "RGBA;4B")
        # quick hack to get around PIL's lack of little-endian RGBA4 support
        rawimage = Image.merge('RGBA', rawimage.split()[::-1])
        rawimage.save((filename + ".png"))
    if bytelayout == 0:
        print("ABGR8888")
        rawimage = Image.frombytes("RGBA", (width, height), imagedata, "raw", "ABGR")
        rawimage.save((filename + ".png"))
    if bytelayout == 2:
        print("ARGB1555")
        imagedata_swapped = BytesIO(rgba5551_to_argb1555(imagedata)).read()
        rawimage = Image.frombytes("RGBA", (width, height), imagedata_swapped, "raw", "BGRA;15") # note - expects big endian. LeapFrog textures tend to be little-endian.
        rawimage.save((filename + ".png"))
