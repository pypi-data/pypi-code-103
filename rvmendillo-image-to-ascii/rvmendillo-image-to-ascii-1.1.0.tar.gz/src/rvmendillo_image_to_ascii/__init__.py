from PIL import Image, ImageDraw, ImageFont

class ImageToASCII:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
        self.charset = list('#Wo- ')
        self.font = ImageFont.truetype('Consolas.TTF', 15)
    
    def generate_ascii_text(self, target_width=100, character_width=8, character_height=18, inverted=False):
        if inverted:
            charset = self.charset[::-1]
        else:
            charset = self.charset
        resized_image = self.resize_image(self.image, target_width, character_width, character_height)
        grayscale_image = self.convert_image_to_grayscale(resized_image)
        ascii_characters = self.convert_pixels_to_ascii(grayscale_image, charset)
        number_of_pixels = len(ascii_characters)
        ascii_text = '\n'.join(ascii_characters[i:i+target_width] for i in range(0, number_of_pixels, target_width))
        return ascii_text
    
    def generate_colored_ascii_image(self, target_width=100, character_width=8, character_height=18, inverted=True):
        if inverted:
            charset = self.charset[::-1]
            color = (0, 0, 0)
        else:
            charset = self.charset
            color = (255, 255, 255)
        resized_image = self.resize_image(self.image, target_width, character_width, character_height)
        grayscale_image = self.convert_image_to_grayscale(resized_image)
        ascii_characters = self.convert_pixels_to_ascii(grayscale_image, charset)
        rgb_pixels = resized_image.load()
        colored_ascii_image = Image.new('RGB', (character_width*target_width, character_height*resized_image.height), color=color)
        drawer = ImageDraw.Draw(colored_ascii_image)
        charset_length = len(charset)
        for y in range(resized_image.height):
            for x in range(target_width):
                r, g, b = rgb_pixels[x, y]
                h = int((r+g+b) / 3)
                drawer.text((x*character_width, y*character_height), charset[h*charset_length//256], font=self.font, fill=(r, g, b))
        return colored_ascii_image
    
    def resize_image(self, image, target_width, character_width, character_height):
        width, height = image.size
        ratio = height / width
        new_height = int(target_width * ratio * character_width / character_height)
        resized_image = image.resize((target_width, new_height))
        return resized_image
    
    def convert_image_to_grayscale(self, colored_image):
        grayscale_image = colored_image.convert('L')
        return grayscale_image
    
    def convert_pixels_to_ascii(self, image, charset):
        pixels = image.getdata()
        charset_length = len(charset)
        ascii_characters = ''.join([charset[pixel*charset_length//256] for pixel in pixels])
        return ascii_characters
    
    def save_text(self, text, filename='ascii_text.txt'):
        with open(filename, 'w') as text_file:
            text_file.write(text)
        
    def save_image(self, image, filename='colored_ascii_image.png'):
        image.save(filename)
