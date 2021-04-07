import re


text = 'Happy \"love. I abandon easy/ easy does not work not Good\' cool stuff cool better!@  good@! pretty.nice Bad. BaD'

def readEmotionDictionary():
    emotion_dictionary_object = open("AFINN.txt", "r")
    emotion_word_items = emotion_dictionary_object.readlines()
    emotion_dictionary = {}
    for line in emotion_word_items:
        line_content = line.split("\t")
        emotion_dictionary[line_content[0]] = line_content[1].strip('\n')
    return emotion_dictionary

def searchPhraseInTwitterText(twitter_text, phrase_list, emotion_dictionary):
    phrase_points = 0
    for phrase in phrase_list:
        phrase_pattern = re.compile(r'[\s!,.\'\"]*' + phrase + r'[!,?.\'\"]*')
        phrase_list = re.findall(phrase_pattern, twitter_text)
        if len(phrase_list) != 0:
            print(phrase_list)
            phrase_points += (int(emotion_dictionary[phrase]) * len(phrase_list))
            for match_phrase in phrase_list:
                twitter_text = twitter_text.replace(match_phrase, '')
    return [phrase_points, twitter_text]


phrase_list = ['can\'t stand', 'cashing in', 'cool stuff', 'does not work', 'dont like', 'fed up', 'green wash',
                   'green washing', 'messing up', 'no fun', 'not good', 'not working', 'right direction', 'screwed up',
               'some kind']

text = text.lower()
emotion_dictionary = readEmotionDictionary()
[phrase_points, phrase_free_twitter_text] = searchPhraseInTwitterText(text, phrase_list, emotion_dictionary)
# word_list = re.findall('[a-z]+', phrase_free_twitter_text)
# print(phrase_free_twitter_text)

twitter_word_list = re.split(r'[\s!,?.\'\"]+', phrase_free_twitter_text)
valid_word_list = []
for word in twitter_word_list:
    pattern = re.compile('^[\!\,\?\.\'\"]*[a-z]+[\']?[a-z]*[\!\,\?\.\'\"]*$')
    pattern_final = re.compile('[a-z]+[\']?[a-z]*')
    valid_word = re.findall(pattern, word)
    if len(valid_word) == 0:
        continue
    for item in valid_word:
        final_word = re.findall(pattern_final, item)
        for each_word in final_word:
            valid_word_list.append(each_word)


index = 0
happiness_points = phrase_points
while index <= len(valid_word_list) - 1:
    word_happiness_points = emotion_dictionary.get(valid_word_list[index], 0)
    if int(word_happiness_points) != 0:
        print(valid_word_list[index] + '    ' + word_happiness_points)
    happiness_points += int(word_happiness_points)
    index += 1


print(happiness_points)
# print(valid_word_list)


