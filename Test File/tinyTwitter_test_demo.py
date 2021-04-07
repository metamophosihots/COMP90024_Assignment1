import json
import re

phrase_list = ['can\'t stand', 'cashing in', 'cool stuff', 'does not work', 'dont like', 'fed up', 'green wash',
               'green washing', 'messing up', 'no fun', 'not good', 'not working', 'right direction', 'screwed up',
               'some kind']


# Read the emotion dictionary file end with txt, convert it into two arrays.
# One of them is a word list, the other one is the corresponding emotion points
def readEmotionDictionary():
    emotion_dictionary_object = open("AFINN.txt", "r")
    emotion_word_items = emotion_dictionary_object.readlines()
    emotion_dictionary = {}
    for line in emotion_word_items:
        line_content = line.split("\t")
        emotion_dictionary[line_content[0]] = line_content[1].strip('\n')
    return emotion_dictionary


# Set up an empty form for final happiness points presentation
def initializeZoneHappinessPoints():
    zone_happiness_points = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'B4': 0,
                             'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'D3': 0, 'D4': 0, 'D5': 0}
    return zone_happiness_points


# Set up an empty form for the final twitter counts presentation
def initializeZoneTwitterCount():
    zone_twitter_counts = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'B4': 0,
                           'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'D3': 0, 'D4': 0, 'D5': 0}
    return zone_twitter_counts


# Read the twitter content and seize a single twitter from the provided json file
def getTwitter(twitter_file, twitter_index):
    single_twitter = twitter_file['rows'][twitter_index]
    return single_twitter


# Seize useful information for happiness points calculation
def seizeTwitterContent(twitter_file):
    twitter_id = twitter_file.get('doc').get('_id')
    twitter_coordinates = twitter_file.get('value').get('geometry').get('coordinates')
    twitter_location = twitter_file.get('value').get('properties').get('location')
    twitter_text = twitter_file.get('value').get('properties').get('text')
    twitter_content = {'id': twitter_id, 'location': twitter_location, 'coordinates': twitter_coordinates,
                       'text': twitter_text}
    return twitter_content


def calculateLongitudeZone(coordinates):
    longitude = coordinates[0]
    relative_longitude = format((longitude - 144.7), '.8f')
    relative_longitude = float(relative_longitude)
    if relative_longitude < 0 or relative_longitude > 0.6:
        # Stop searching this twitter
        longitude_zone = -1
    else:
        longitude_district = relative_longitude / 0.15
        if longitude_district <= 1:
            longitude_zone = 1
        elif longitude_district <= 2:
            longitude_zone = 2
        elif longitude_district <= 3:
            longitude_zone = 3
        elif longitude_district <= 4:
            longitude_zone = 4
        else:
            longitude_zone = 5
    return longitude_zone


def calculateLatitudeZone(coordinates):
    latitude = coordinates[1]
    relative_latitude = format((latitude + 38.1), '.8f')
    relative_latitude = float(relative_latitude)
    if relative_latitude < 0 or relative_latitude > 0.6:
        # Stop searching this twitter
        latitude_zone = 'X'
    else:
        latitude_district = relative_latitude / 0.15
        if latitude_district <= 1:
            latitude_zone = 'D'
        elif latitude_district <= 2:
            latitude_zone = 'C'
        elif latitude_district <= 3:
            latitude_zone = 'B'
        else:
            latitude_zone = 'A'
    return latitude_zone


# judge if the zone is one of the zones in melbGrid
def allocateZone(longitude_zone, latitude_zone):
    twitter_zone_list = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4', 'C5', 'D3', 'D4', 'D5']
    twitter_zone = latitude_zone + str(longitude_zone)
    if twitter_zone in twitter_zone_list:
        return twitter_zone
    else:
        return 'X0'


# Transform twitter text into all lower case situation, and then split them with all possible mark
def searchPhraseInTwitterText(twitter_text, phrase_list, emotion_dictionary):
    phrase_points = 0
    for phrase in phrase_list:
        phrase_pattern = re.compile(r'[\s!,.\'\"]*' + phrase + r'[!,?.\'\"]*')
        phrase_list = re.findall(phrase_pattern, twitter_text)
        if len(phrase_list) != 0:
            # print(phrase_list)
            phrase_points += (int(emotion_dictionary[phrase]) * len(phrase_list))
            for match_phrase in phrase_list:
                twitter_text = twitter_text.replace(match_phrase, '')
    return [phrase_points, twitter_text]


def splitTwitterText(twitter_text):
    twitter_word_list = re.split(r'[\s]+', twitter_text)
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
    return valid_word_list


# calculate happiness points for a twitter
def calculateHappinessPoints(emotion_dictionary, twitter_content):
    index = 0
    twitter_happiness_points = 0
    twitter_text = twitter_content['text'].lower()
    [phrase_points, phrase_free_twitter_text] = searchPhraseInTwitterText(twitter_text, phrase_list, emotion_dictionary)
    twitter_happiness_points += phrase_points

    twitter_word_list = splitTwitterText(phrase_free_twitter_text)
    while index <= len(twitter_word_list) - 1:
        word_happiness_points = emotion_dictionary.get(twitter_word_list[index], 0)
        twitter_happiness_points += int(word_happiness_points)
        index += 1
    twitter_content['happiness_points'] = twitter_happiness_points
    return twitter_content


# add single happiness points to the zone happiness points
def sumHappinessPoints(twitter_content, zone_happiness_points):
    zone_happiness_points[twitter_content['zone']] += twitter_content['happiness_points']


# demo for testing tiny json twitter file
with open("smallTwitter.json", "r") as read_file:
    twitter_file = json.load(read_file)
total_twitter_count = len(twitter_file['rows'])
twitter_index = 0
emotion_dictionary = readEmotionDictionary()
zone_happiness_points = initializeZoneHappinessPoints()
zone_twitter_counts = initializeZoneTwitterCount()

while twitter_index <= total_twitter_count - 1:
    single_twitter = getTwitter(twitter_file, twitter_index)
    twitter_index += 1
    twitter_content = seizeTwitterContent(single_twitter)
    longitude_zone = calculateLongitudeZone(twitter_content['coordinates'])
    latitude_zone = calculateLatitudeZone(twitter_content['coordinates'])
    twitter_zone = allocateZone(longitude_zone, latitude_zone)
    if twitter_zone == 'X0':
        continue
    twitter_content['zone'] = twitter_zone
    zone_twitter_counts[twitter_zone] += 1
    twitter_content = calculateHappinessPoints(emotion_dictionary, twitter_content)
    sumHappinessPoints(twitter_content, zone_happiness_points)
print(zone_happiness_points)
print(zone_twitter_counts)
