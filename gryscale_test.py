from PIL import Image
import sys

if __name__ == "__main__":
    output_name = "gray.bmp"

    if len(sys.argv) >= 2:
        image = Image.open(sys.argv[1])
    else:
        print("No input file provided")
        sys.exit()

    if len(sys.argv) == 3:
        output_name = sys.argv[2]
    gray = image.convert("L")
    gray.save(output_name)
