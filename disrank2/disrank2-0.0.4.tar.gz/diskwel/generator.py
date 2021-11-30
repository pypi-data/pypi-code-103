from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
import math
import os


class Generator:
    def __init__(self):
        self.default_bg = os.path.join(os.path.dirname(__file__), 'assets', 'card.png')
        self.online     = os.path.join(os.path.dirname(__file__), 'assets', 'online.png')
        self.offline    = os.path.join(os.path.dirname(__file__), 'assets', 'offline.png')
        self.idle       = os.path.join(os.path.dirname(__file__), 'assets', 'idle.png')
        self.dnd        = os.path.join(os.path.dirname(__file__), 'assets', 'dnd.png')
        self.streaming  = os.path.join(os.path.dirname(__file__), 'assets', 'streaming.png')
        self.font1      = os.path.join(os.path.dirname(__file__), 'assets', 'font.ttf')
        self.font2      = os.path.join(os.path.dirname(__file__), 'assets', 'font2.ttf')

    def generate_rank(self, bg_image:str=None, profile_image:str=None, level:int=1, current_xp:int=0, user_xp:int=20, next_xp:int=100, user_position:int=1, user_name:str='Just a normal guy', user_status:str='online', text_color:str='#ff7300' ):
        if not bg_image:
            card = Image.open(self.default_bg).convert("RGBA")
        else:
            bg_bytes = BytesIO(requests.get(bg_image).content)
            card = Image.open(bg_bytes).convert("RGBA")

            width, height = card.size
            if width == 900 and height == 238:
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

                card = card.crop((x1, y1, x2, y2)).resize((900, 238))

        profile_bytes = BytesIO(requests.get(profile_image).content)
        profile = Image.open(profile_bytes)
        profile = profile.convert('RGBA').resize((180, 180))

        if user_status == 'online':
            status = Image.open(self.online)
        if user_status == 'offline':
            status = Image.open(self.offline)
        if user_status == 'idle':
            status = Image.open(self.idle)
        if user_status == 'streaming':
            status = Image.open(self.streaming)
        if user_status == 'dnd':
            status = Image.open(self.dnd)

        status = status.convert("RGBA").resize((40,40))

        profile_pic_holder = Image.new(
            "RGBA", card.size, (255, 255, 255, 0)
        )  # Is used for a blank image so that i can mask

        # Mask to crop image
        mask = Image.new("RGBA", card.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(
            (29, 29, 209, 209), fill=(255, 25, 255, 255)
        )  # The part need to be cropped

        # Editing stuff here

        # ======== Fonts to use =============
        font_user = ImageFont.truetype(self.font1, 45)
        font_slash = ImageFont.truetype(self.font1, 30)
        font_discr = ImageFont.truetype(self.font1, 25)
        font_rank = ImageFont.truetype(self.font1, 30)
        font_small = ImageFont.truetype(self.font1, 20)
        font_numbers = ImageFont.truetype(self.font1, 50)
        font_hashtag = ImageFont.truetype(self.font1, 55)
        font_signa = ImageFont.truetype(self.font2, 25)

        # ======== Colors ========================
        colorr = ImageColor.getcolor(text_color, "RGB")
        DISC = (103, 107, 110)
        BLANC = (255, 255, 255)
        WHITE = (189, 195, 199)
        YELLOW = (255, 234, 167)

        # ======== Username and xp ===============
        def get_str(xp):
            if xp < 1000:
                return str(xp)
            if xp >= 1000 and xp < 1000000:
                return str(round(xp / 1000, 1)) + "k"
            if xp > 1000000:
                return str(round(xp / 1000000, 1)) + "M"

        discriminator = user_name[-5:]
        lengt = len(user_name)
        length_username = int(lengt) - 5
        usernam = user_name[0:length_username]
        wid_user = font_user.getsize(usernam)[0]
        wid_discr = font_discr.getsize(discriminator)[0]


        str_user_xp = get_str(user_xp)
        str_next_xp = get_str(next_xp) + ' XP'
        wid_user_xp = font_discr.getsize(str_user_xp)[0]
        wid_next_xp = font_discr.getsize(str_next_xp)[0]
        wid_slash = font_slash.getsize('/')[0]
        x_next_xp = 830 - wid_next_xp
        x_slash = x_next_xp - 13 
        x_user_xp = x_slash - 5 - wid_user_xp
        space_xps = wid_user_xp + wid_next_xp + wid_slash + 13 + 5 
        space_xp_username = 830 - space_xps - wid_discr - 270

        size_font_username = 45
        while font_user.getsize(usernam)[0] > space_xp_username : 
            size_font_username = size_font_username - 1
            font_user = ImageFont.truetype(self.font1, size_font_username)
            
        wid_user = font_user.getsize(usernam)[0]
        x_dis = 278 + wid_user
        draw = ImageDraw.Draw(card)
        width_ok, height_ok = draw.textsize(usernam, font=font_user)
        y_user = 155 - height_ok
        width_ok, height_ok = draw.textsize(discriminator, font=font_discr)
        y_discr = 155 - height_ok
        width_ok, height_ok = draw.textsize(str_next_xp, font=font_discr)
        y_xp = 155 - height_ok
 
        draw.text((270, y_user), usernam, BLANC, font=font_user)
        draw.text((x_dis, y_discr), discriminator, DISC, font=font_discr)
        draw.text((x_next_xp, y_xp), f"{str_next_xp}", DISC, font=font_discr)
        draw.text((x_slash, 122), "/", BLANC, font=font_slash)
        draw.text((x_user_xp, y_xp), f"{str_user_xp}", BLANC, font=font_discr)

        # ======== Level and rank ===============
        str_level = str(level)
        wid_leveln = font_numbers.getsize(str_level)[0]
        x_leveln = 830 - wid_leveln
        wid_level = font_rank.getsize('Level')[0]
        x_level = x_leveln - 10 - wid_level

        posit = str(user_position)
        wid_rankn = font_numbers.getsize(posit)[0]
        x_rankn = x_level - 20 - wid_rankn
        wid_hashtag = font_hashtag.getsize('#')[0]
        x_hashtag = x_rankn - wid_hashtag
        wid_rank = font_rank.getsize('Rank')[0]
        x_rank = x_hashtag - 10 - wid_rank

        draw.text((x_leveln, 20), f"{level}", colorr, font=font_numbers)
        draw.text((x_level, 40), "Level", colorr, font=font_rank)
        draw.text((x_rankn, 20), f"{posit}", BLANC, font=font_numbers)
        draw.text((x_hashtag, 15), "#", BLANC, font=font_hashtag)
        draw.text((x_rank, 40), f"Rank", BLANC, font=font_rank)
        

        # ======== Progress Bar ==================
        # Adding another blank layer for the progress bar
        # Because drawing on card dont make their background transparent
        blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
        blank_draw = ImageDraw.Draw(blank)
        blank_draw.rectangle(
            (270, 162, 830, 193), fill=(255, 255, 255, 0), outline=colorr
        )

        xpneed = next_xp - current_xp
        xphave = user_xp - current_xp

        current_percentage = (xphave / xpneed) * 100
        length_of_bar = (current_percentage * 4.9) + 273

        blank_draw.rectangle((273, 165, length_of_bar, 190), fill=colorr)
        blank_draw.ellipse((20, 20, 218, 218), fill=(255, 255, 255, 0), outline=colorr)

        profile_pic_holder.paste(profile, (29, 29, 209, 209))

        pre = Image.composite(profile_pic_holder, card, mask)
        pre = Image.alpha_composite(pre, blank)

        # Status badge
        # Another blank
        blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))
        blank.paste(status, (169, 169))

        final = Image.alpha_composite(pre, blank)
        final_bytes = BytesIO()
        final.save(final_bytes, 'png')
        final_bytes.seek(0)
        return final_bytes

