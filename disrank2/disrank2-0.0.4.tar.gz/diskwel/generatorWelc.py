from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
import math
import os



class Welcomegenerator:
    def __init__(self):
        self.default_bg = os.path.join(os.path.dirname(__file__), 'assets', 'welcome.jpg')
        self.font1      = os.path.join(os.path.dirname(__file__), 'assets', 'font.ttf')
        self.font2      = os.path.join(os.path.dirname(__file__), 'assets', 'font2.ttf')

    def generate_welcome(self, bg_image:str=None, profile_image:str=None, server_name:str=None, user_name:str='Just a normal guy', text_color:str='#ff7300' ):
        if not bg_image:
            card = Image.open(self.default_bg).convert("RGBA")
        else:
            bg_bytes = BytesIO(requests.get(bg_image).content)
            card = Image.open(bg_bytes).convert("RGBA")

            width, height = card.size
            if width == 1000 and height == 400:
                pass
            else:
                x1 = 0
                y1 = 0
                x2 = width
                nh = math.ceil(width * 0.264444)
                y2 = 0

                if nh < height:
                    y1 = (height / 2) - 119
                    y2 = nh + y1

                card = card.crop((x1, y1, x2, y2)).resize((1000, 400))

        profile_bytes = BytesIO(requests.get(profile_image).content)
        profile = Image.open(profile_bytes)
        profile = profile.convert('RGBA').resize((180, 180))



        profile_pic_holder = Image.new(
            "RGBA", card.size, (255, 255, 255, 0)
        )  # Is used for a blank image so that i can mask

        # Mask to crop image
        mask = Image.new("RGBA", card.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(
            (410, 29, 590, 209), fill=(255, 25, 255, 255)
        )  # The part need to be cropped

        # Editing stuff here

        # ======== Fonts to use =============
        font_welcome = ImageFont.truetype(self.font1, 55)
        font_user = ImageFont.truetype(self.font1, 55)
        font_signa = ImageFont.truetype(self.font2, 25)

        # ======== Colors ========================
        colorr = ImageColor.getcolor(text_color, "RGB")
        DISC = (103, 107, 110)
        BLANC = (255, 255, 255)
        WHITE = (189, 195, 199)
        YELLOW = (255, 234, 167)

        # ======== Welcome and username ===============
 
        draw = ImageDraw.Draw(card)

        msg = 'WELCOME'
        wid_welcome = font_welcome.getsize(msg)[0]
        x_welcome = 500 - (1/2 * wid_welcome)

        draw.text((x_welcome, 430), msg, colorr, font=font_welcome)

        # ======== Progress Bar ==================
        # Adding another blank layer for the progress bar
        # Because drawing on card dont make their background transparent
        blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
        blank_draw = ImageDraw.Draw(blank)

        blank_draw.ellipse((401, 20, 599, 218), fill=(255, 255, 255, 0), outline=colorr)

        profile_pic_holder.paste(profile, (29, 29, 209, 209))

        pre = Image.composite(profile_pic_holder, card, mask)
        pre = Image.alpha_composite(pre, blank)

        # Status badge
        # Another blank
        blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))

        final = Image.alpha_composite(pre, blank)
        final_bytes = BytesIO()
        final.save(final_bytes, 'png')
        final_bytes.seek(0)
        return final_bytes
