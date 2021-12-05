from speech_features_kit.Emotion.speech_toolkit import SpeechEmotionToolkit

# set the path of pre-trained model for speech emotion model
speech_kit = SpeechEmotionToolkit(
    model_path='../src/speech_features_kit/Emotion/models/speech_mfcc_model.h5',
    model_para_path='../src/speech_features_kit/Emotion/models/mfcc_model_para_dict.pkl')

# load the model
speech_kit.load()

# obtain emotion list with timestamp given an audio file
list_emo, list_timestamp = speech_kit.get_emotion_list_by_blocks(audio_file="../data/english.wav",
                                                                     num_sec_each_file=1)

# print the list of emotion over timestamp
print("Time interval\tEmotion")
for idx, e in enumerate(list_emo):
    print(list_timestamp[idx], "\t", e)


