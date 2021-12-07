from telegram import (Update, ReplyKeyboardRemove)
from telegram.ext import (CallbackContext)

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate

def telegram_eval_jahreszahl(update: Update, context: CallbackContext, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    import re
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(r"\d{1,4}", update.message.text)[0])
    if schaetzung == echter_wert:
        update.message.reply_text(richtig_text,
                                  reply_markup=ReplyKeyboardRemove())

    differenz = schaetzung - echter_wert
    if differenz == -1:
        update.message.reply_text(spaeter_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz < -1:
        update.message.reply_text(spaeter_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz == 1:
        update.message.reply_text(vorher_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz > 1:
        update.message.reply_text(vorher_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())


def whatsapp_eval_jahreszahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    import re
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(r"\d{1,4}", update.Body)[0])
    if schaetzung == echter_wert:
        client.messages.create(
            body=richtig_text,
            from_=update.To,
            to=update.From
        )

    differenz = schaetzung - echter_wert
    if differenz == -1:
        client.messages.create(
            body=spaeter_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz < -1:
        client.messages.create(
            body=spaeter_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )

    elif differenz == 1:
        client.messages.create(
            body=vorher_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz > 1:
        client.messages.create(
            body=vorher_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )


def telegram_eval_prozentzahl(update: Update, context: CallbackContext, echter_wert, richtig_text, falsch_text):
    echter_wert = float(echter_wert)
    import re
    match = re.search(
        r"(?P<vorkomma>\d{1,2}),? ?(?P<nachkomma>\d{,2})", update.message.text)

    schaetzung = int(match.group('vorkomma')) + \
        float("0."+match.group('nachkomma'))

    if schaetzung == echter_wert:
        update.message.reply_text(richtig_text,
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(falsch_text,
                                  reply_markup=ReplyKeyboardRemove())

def whatsapp_eval_prozentzahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, falsch_text):
    echter_wert = float(echter_wert)
    import re
    match = re.search(
        r"(?P<vorkomma>\d{1,2}),? ?(?P<nachkomma>\d{,2})", update.Body)

    schaetzung = int(match.group('vorkomma')) + \
        float("0."+match.group('nachkomma'))

    if schaetzung == echter_wert:
        client.messages.create(
            body=richtig_text,
            from_=update.To,
            to=update.From
        )

    else:
        client.messages.create(
            body=falsch_text,
            from_=update.To,
            to=update.From
        )

def telegram_eval_kommazahl(update: Update, context: CallbackContext, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    import re
    match = re.search(
        r"(?P<vorkomma>\d{1,2}),? ?(?P<nachkomma>\d{,2})", update.message.text)

    schaetzung = int(match.group('vorkomma')) + \
        float("0."+match.group('nachkomma'))

    if schaetzung == echter_wert:
        update.message.reply_text(richtig_text,
                                  reply_markup=ReplyKeyboardRemove())
    
    differenz = schaetzung - echter_wert
    if differenz == -1:
        update.message.reply_text(spaeter_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz < -1:
        update.message.reply_text(spaeter_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz == 1:
        update.message.reply_text(vorher_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz > 1:
        update.message.reply_text(vorher_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())

def whatsapp_eval_kommazahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    import re
    match = re.search(
        r"(?P<vorkomma>\d{1,2}),? ?(?P<nachkomma>\d{,2})", update.Body)

    schaetzung = int(match.group('vorkomma')) + \
        float("0."+match.group('nachkomma'))

    if schaetzung == echter_wert:
        client.messages.create(
            body=richtig_text,
            from_=update.To,
            to=update.From
        )

    differenz = schaetzung - echter_wert
    if differenz == -1:
        client.messages.create(
            body=spaeter_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz < -1:
        client.messages.create(
            body=spaeter_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )

    elif differenz == 1:
        client.messages.create(
            body=vorher_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz > 1:
        client.messages.create(
            body=vorher_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )


telegram_action_functions = {"eval_jahreszahl": telegram_eval_jahreszahl,
                             "eval_prozentzahl": telegram_eval_prozentzahl,
                             "eval_kommazahl": telegram_eval_kommazahl,
                             }

whatsapp_action_functions = {"eval_jahreszahl": whatsapp_eval_jahreszahl,
                             "eval_prozentzahl": whatsapp_eval_prozentzahl,
                             "eval_kommazahl": whatsapp_eval_kommazahl,
                             }
