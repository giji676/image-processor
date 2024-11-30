import struct


class BMP:
    header = None

    def __init__(self):
        pass

    def read_BITMAPINFOHEADER(self, file, size):
        data = file.read(size)
        unpack_format = "<iiHHIIiiII"
        return struct.unpack(unpack_format, data)

    def read_BITMAPV5HEADER(self, file, size):
        data = file.read(size)
        unpack_format = "<IIII36sIIIIIIII"
        return struct.unpack(unpack_format, data)

    def extract_CIEXYZTRIPLE(self, endpoint_data):
        # Unpack the first 12 bytes as 3 LONGs (4 bytes each)
        unpack_format = "<3l"  # 3 long integers (each 4 bytes)
        endpoints = struct.unpack(unpack_format, endpoint_data[:12])
        return endpoints
    
    def read_1_pixel(self, file, size):
        data = file.read(size//8)
        unpack_format = "<BBB"
        return struct.unpack(unpack_format, data)

    def load_bmp(self, path):
        with open(path, "rb") as f:
            header = f.read(14)  # File header size: 14
            header_fields = struct.unpack("<2sIHHI", header)

            print("FILE HEADER")
            print(header_fields)
            print()

            f.seek(14)  # DIB header offset: 14
            header_size = int.from_bytes(f.read(4), "little")  # DIB header size: 4

            print("DIB HEADER")
            if header_size == 40:
                dib_header = self.read_BITMAPINFOHEADER(f, 40-4)
                print(dib_header)
            elif header_size == 124:
                dib_header1 = self.read_BITMAPINFOHEADER(f, 40-4)
                dib_header2 = self.read_BITMAPV5HEADER(f, 124-40)
                CIEXYZTRIPLE = self.extract_CIEXYZTRIPLE(dib_header2[4])
                print(dib_header1)
                print(dib_header2)
                print(CIEXYZTRIPLE)
                print(self.read_1_pixel(f, dib_header1[3]))


BMP().load_bmp("image.bmp")
