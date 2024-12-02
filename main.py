import struct
import sys


class BMP:
    file_header = None
    dib_header = None
    pixel_data = None
    int_pixels = None

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

                row_size = int((BITMAPINFOHEADER_data["bit_count"] * 
                                BITMAPINFOHEADER_data["width"]+31) / 32) * 4
                pixel_array_size = row_size*abs(BITMAPINFOHEADER_data["height"])

                f.seek(header_fields["offset"])

                pixel_rows = []
                for row in range(abs(BITMAPINFOHEADER_data["height"])):
                    row_data = f.read(row_size)
                    pixel_rows.append(row_data[:BITMAPINFOHEADER_data["width"] * 3])  # Exclude padding

                int_pixels = []

                for row_index, row_pixels in enumerate(pixel_rows):
                    int_row = []
                    for col in range(0, len(row_pixels), 3):
                        # print(row_pixels[col:col+3])
                        int_row.append(list(row_pixels[col:col+3]))
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
                f.write(row)

    def construct_image(self, path, pixels):
        # expects 2d pixels array with RGB list as elements
        # [[(255,255,255), (255,0,0)],
        #  [(0,255,0), (0,0,255)]]

        header = [b"BM"]
        height, width = len(pixels), len(pixels[0])
        pixels_size = width*3 # width * 3 values (RGB)
        pixels_size = (pixels_size + (pixels_size%4))*height # Includes padding

        size = 14 + 40 + pixels_size
        header.append(size)
        header.append(0) # Reserve 1
        header.append(0) # Reserve 2
        header.append(14+40) # Offset

        standard_dpi = 96
        m_to_inch = 39.3701
        res_x = round(standard_dpi * m_to_inch)
        res_y = round(standard_dpi * m_to_inch)

        dib_header = [40] # Size of the header - BITMAPINFOHEADER version - 40
        dib_header.append(width)
        dib_header.append(height)
        dib_header.append(1) # Planes - has to be 1
        dib_header.append(24) # Bits per pixel - usually 24
        dib_header.append(0) # Compression - 0 for none
        dib_header.append(pixels_size)
        dib_header.append(res_x) # Horizontal res
        dib_header.append(res_y) # Vertical res
        dib_header.append(0) # Num of colors used
        dib_header.append(0) # Num of important colors

        with open(path, "wb") as f:
            format_string = "<2sIHHI"
            test = struct.pack(format_string, *header)
            f.write(test)

            format_string = "<IiiHHIIiiII"
            test = struct.pack(format_string, *dib_header)
            f.write(test)

            for row in pixels:
                temp = b""
                for col in row:
                    temp += struct.pack(f"{len(col)}B", *col)

                if len(temp) % 4 != 0:
                    temp += b"\x00" * (len(temp) % 4)
                f.write(temp)

    def grayscale(self, pixels):
        new_pix = []
        for row in pixels:
            temp = []
            for col in row:
                gray_val = int(0.299*col[0] + 0.587*col[1] + 0.114*col[2]) # RGB
                temp.append((gray_val, gray_val, gray_val))
            new_pix.append(temp)
        return new_pix

    def hex_to_pixels(self, image): # ==== MIGHT BE WRONG ====
        # Turn hex RGB values to ints
        int_pixels = []

        for row_index, row_pixels in enumerate(image):
            temp = []
            for col in range(0, len(row_pixels), 3):
                # print(row_pixels[col:col+3])
                temp.append((list(row_pixels[col:col+3])))
            int_pixels.append(temp)
        self.int_pixels = int_pixels
        return self.int_pixels

if __name__ == "__main__":
    bmp_image = BMP()
    output_name = "gray.bmp"

    if len(sys.argv) >= 2:
        bmp_image.load_bmp(sys.argv[1])
    else:
        print("No input file provided")
        sys.exit()

    if len(sys.argv) == 2:
        output_name = sys.argv[2]
    gray = bmp_image.grayscale(bmp_image.int_pixels)
    bmp_image.construct_image(output_name, gray)
