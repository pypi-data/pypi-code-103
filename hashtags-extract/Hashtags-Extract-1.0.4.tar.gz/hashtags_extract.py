def hashtags(string, hash=True):
    hashtags = []
    for word in string.replace('\n', '').split():
        if word.startswith("#") and word != "#":
            if hash:
                hashtag = word
            else:
                hashtag = word.replace("#", "")
            hashtags.append(hashtag)
    return hashtags
