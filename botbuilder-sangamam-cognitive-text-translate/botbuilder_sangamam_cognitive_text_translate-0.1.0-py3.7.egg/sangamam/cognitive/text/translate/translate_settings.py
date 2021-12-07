class TranslateSettings:
    def __init__(self) -> None:
        self.url = ''
        self.subscription_key = ''
        self.from_lang = ''
        self.to_lang = [],
        self.subscription_region = ''

    def validate_settings(self) -> bool:
        if self.subscription_key == '':
            raise Exception('subscription_key is empty')
        if self.url == '':
            raise Exception('url is empty')
        if self.from_lang == '':
            raise Exception('from_lang is empty')
        if not self.to_lang:
            raise Exception('to_lang is empty')
        if self.subscription_region == '':
            raise Exception('subscription_region is empty')
        return True
