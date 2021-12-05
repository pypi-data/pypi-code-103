from speech_features_kit.Emotion.speech_toolkit import SpeechEmotionToolkit

# set the path of pre-trained model for speech emotion model
speech_kit = SpeechEmotionToolkit()

# load the model
speech_kit.load()

# obtain emotion list with timestamp given an audio file
list_emo, list_timestamp = speech_kit.get_emotion_list_by_blocks(audio_file="../data/english.wav",
                                                                     num_sec_each_file=1)

# print the list of emotion over timestamp
print("Time interval\tEmotion")
for idx, e in enumerate(list_emo):
    print(list_timestamp[idx], "\t", e)


