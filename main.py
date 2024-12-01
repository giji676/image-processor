import struct


class BMP:
    file_header = None
    dib_header = None
    pixel_data = None

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

    def load_bmp(self, path):
        with open(path, "rb") as f:
            header_fields = self.read_file_header(f, 14)
            BITMAPINFOHEADER_data = None

            # print("FILE HEADER")
            for index, (key, value) in enumerate(header_fields.items()):
                if isinstance(value, bytes):
                    continue
                    print(key, value.hex())
                else:
                    continue
                    print(key, hex(value))
            # print()

            f.seek(14)  # DIB header offset: 14
            header_size = int.from_bytes(f.read(4), "little")  # DIB header size: 4

            # print("DIB HEADER")
            if header_size == 40 or header_size == 124:
                BITMAPINFOHEADER_data = self.read_BITMAPINFOHEADER(f, 40 - 4)

                # We get size from outside the header read file
                # so it's added in manually at 0th position
                temp = list(BITMAPINFOHEADER_data.items())
                temp.insert(0, ("size", header_size))
                BITMAPINFOHEADER_data = dict(temp)

                for index, (key, value) in enumerate(BITMAPINFOHEADER_data.items()):
                    if isinstance(value, bytes):
                        continue
                        print(key, value.hex())
                    else:
                        continue
                        print(key, hex(value))
                row_size = int((BITMAPINFOHEADER_data["bit_count"] * 
                                BITMAPINFOHEADER_data["width"]+31) / 32) * 4
                pixel_array_size = row_size*abs(BITMAPINFOHEADER_data["height"])
                # print(row_size)
                # print(pixel_array_size)
                f.seek(header_fields["offset"])

                pixel_rows = []
                for row in range(abs(BITMAPINFOHEADER_data["height"])):
                    row_data = f.read(row_size)
                    pixel_rows.append(row_data[:BITMAPINFOHEADER_data["width"] * 3])  # Exclude padding

                int_pixels = []

                # Print pixel values
                for row_index, row_pixels in enumerate(pixel_rows):
                    for col in range(0, len(row_pixels), 3):
                        # print(row_pixels[col:col+3])
                        int_row = list(row_pixels[col:col+3])
                        int_pixels.append(int_row)

                self.file_header = header_fields
                self.dib_header = BITMAPINFOHEADER_data
                self.pixel_data = pixel_rows
                self.int_pixels = int_pixels

    def save_bmp(self, path):
        with open(path, "wb") as f:
            format_string = "<2sIHHI"
            values = list(self.file_header.values())
            test = struct.pack(format_string, *values)
            f.write(test)

            format_string = "<IiiHHIIiiII"
            values = list(self.dib_header.values())
            test = struct.pack(format_string, *values)
            f.write(test)

            for row in self.pixel_data:
                if len(row) % 4 != 0:
                    row += b"\x00" * (len(row) % 4)
                print(len(row))
                f.write(row)



bmp_image = BMP()
bmp_image.load_bmp("image.bmp")
bmp_image.save_bmp("test.bmp")

