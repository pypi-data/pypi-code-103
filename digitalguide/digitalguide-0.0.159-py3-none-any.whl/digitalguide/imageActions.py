from PIL import Image
from io import BytesIO

from telegram import (Update)
from telegram.ext import (CallbackContext)

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate

def generate_gif(im1, im2):
    im1 = im1.resize((round(im2.size[0]*1), round(im2.size[1]*1)))
    im1 = im1.convert(im2.mode)

    images = []
    frames = 10

    for i in range(frames+1):
        im = Image.blend(im1, im2, i/frames)
        images.append(im)
        
    for i in range(frames+1):
        im = Image.blend(im1, im2, 1-i/frames)
        images.append(im)


    bio = BytesIO()
    bio.name = 'image.gif'

    images[0].save(bio, 'GIF', save_all=True, append_images=images[1:], duration=150, loop=0, optimize=True)
    bio.seek(0)
    return bio

def overlay_images(background, foreground):
    foreground = foreground.resize((round(background.size[0]), round(background.size[1])))
    background.paste(foreground, (0, 0), foreground)
    bio = BytesIO()
    bio.name = 'image.png'
    background.save(bio, 'PNG')
    bio.seek(0)
    return bio

def telegram_eval_gif_generation(update: Update, context: CallbackContext, picture):
    im_bytes = update.message.photo[-1].get_file().download_as_bytearray()

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/' + picture)

    gif = generate_gif(im1, im2)

    update.message.reply_document(gif)

def whatsapp_eval_gif_generation(client, update: WhatsAppUpdate, context, picture):
    pass

telegram_action_functions = {"eval_gif_generation": telegram_eval_gif_generation,
                    }

whatsapp_action_functions = {"eval_gif_generation": whatsapp_eval_gif_generation,
                    }