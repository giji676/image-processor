import struct


class BMP:
    header = None

    def __init__(self):
        pass

    def read_BITMAPINFOHEADER(self, file, size):
        data = file.read(size)
        unpack_format = "<iiHHIIiiII"
        data = struct.unpack(unpack_format, data)
        BITMAPINFOHEADER_keys = [
            "width",
            "height",
            "planes",
            "bit_count",
            "compression",
            "size_image",
            "horizontal_resolution",
            "vertical_resolution",
            "colors_used",
            "colors_important",
        ]
        return dict(zip(BITMAPINFOHEADER_keys, data))

    def read_BITMAPV5HEADER(self, file, size):
        data = file.read(size)
        unpack_format = "<IIII36sIIIIIIII"
        data = struct.unpack(unpack_format, data)
        BITMAPV5HEADER_keys = [
            "red_mask",
            "green_mask",
            "blue_mask",
            "alpha_mask",
            "cs_type",
            "endpoints",
            "gamma_red",
            "gamma_green",
            "gamma_blue",
            "intent",
            "profile_data",
            "profile_size",
            "reserved",
        ]

        return dict(zip(BITMAPV5HEADER_keys, data))

    def extract_CIEXYZTRIPLE(self, endpoint_data):
        # Unpack the first 12 bytes as 3 LONGs (4 bytes each)
        unpack_format = "<3I"  # 3 long integers (each 4 bytes)
        endpoints = struct.unpack(unpack_format, endpoint_data)
        return endpoints

    def read_file_header(self, file, size):
        header = file.read(size)  # File header size: 14
        header_keys = [
            "signature",
            "size",
            "reserve1",
            "reserve2",
            "offset"
        ]
        header_values = struct.unpack("<2sIHHI", header)
        return dict(zip(header_keys, header_values))

    def read_1_pixel(self, file, size):
        data = file.read(size // 8)
        unpack_format = "<BBB"
        return struct.unpack(unpack_format, data)

    def load_bmp(self, path):
        with open(path, "rb") as f:
            header_fields = self.read_file_header(f, 14)
            BITMAPINFOHEADER_data = None

            print("FILE HEADER")
            for index, (key, value) in enumerate(header_fields.items()):
                if isinstance(value, bytes):
                    print(key, value.hex())
                else:
                    print(key, hex(value))
            print()

            f.seek(14)  # DIB header offset: 14
            header_size = int.from_bytes(f.read(4), "little")  # DIB header size: 4

            print("DIB HEADER")
            print("size", hex(header_size))
            if header_size == 40 or header_size == 124:
                BITMAPINFOHEADER_data = self.read_BITMAPINFOHEADER(f, 40 - 4)
                for index, (key, value) in enumerate(BITMAPINFOHEADER_data.items()):
                    if isinstance(value, bytes):
                        print(key, value.hex())
                    else:
                        print(key, hex(value))
                row_size = int((BITMAPINFOHEADER_data["bit_count"] * 
                                BITMAPINFOHEADER_data["width"]+31) / 32) * 4
                pixel_array_size = row_size*abs(BITMAPINFOHEADER_data["height"])
                print(row_size)
                print(pixel_array_size)
                f.seek(header_fields["offset"])

                pixels = []
                for row in range(abs(BITMAPINFOHEADER_data["height"])):
                    row_data = f.read(row_size)
                    pixels.append(row_data[:BITMAPINFOHEADER_data["width"] * 3])  # Exclude padding

                # Print pixel values
                for row_index, row_pixels in enumerate(pixels):
                    for col in range(0, len(row_pixels), 3):
                        print(row_pixels[col:col+3])  # Print RGB values

BMP().load_bmp("image.bmp")
