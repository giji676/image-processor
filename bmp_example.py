
from PIL import Image

def create_bmp_v5():
    # Create a 2x2 image with RGB colors
    image = Image.new("RGB", (2, 2))
    
    # Define the colors for the 2x2 pixels (red, green, blue, white)
    pixels = [
        (255, 0, 0),   # Red
        (0, 255, 0),   # Green
        (0, 0, 255),   # Blue
        (255, 255, 255)  # White
    ]
    
    # Set the pixels in the image
    image.putdata(pixels)
    
    # Save the image as a BMP file
    # Pillow automatically saves BMP in a compatible format
    image.save("example_v5.bmp", "BMP")
    print("2x2 BMP image saved as 'example_v5.bmp'")

# Run the function to create the BMP
create_bmp_v5()
