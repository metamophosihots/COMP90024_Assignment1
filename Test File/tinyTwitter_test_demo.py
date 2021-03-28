import json
import re

# Read the emotion dictionary file end with txt, convert it into two arrays.
# One of them is a word list, the other one is the corresponding emotion points
def readEmotionDictionary():
    emotion_dictionary_object = open("AFINN.txt", "r")
    emotion_word_items = emotion_dictionary_object.readlines()
    word_list_array = []
    word_points_array = []
    for line in emotion_word_items:
        line_content = line.split("\t")
        word_list_array.append(line_content[0])
        word_points_array.append(int(line_content[1].rstrip("\n")))
    return [word_list_array, word_points_array]

# Set up an empty form for final happiness points presentation
def initializeZoneHappinessPoints():
    zone_happiness_points = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'B4': 0,
                             'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'D3': 0, 'D4': 0, 'D5': 0}
    return zone_happiness_points


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
    longitude_district = (longitude - 144.7) / 0.15
    if longitude_district < 0 or longitude_district > 5:
        # Stop searching this twitter
        longitude_zone = -1
    else:
        if 0 <= longitude_district <= 1:
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
    latitude_district = (latitude + 38.1) / 0.15
    if latitude_district < 0 or latitude_district > 4:
        # Stop searching this twitter
        latitude_zone = 'X'
    else:
        if 0 <= latitude_district < 1:
            latitude_zone = 'D'
        elif latitude_district < 2:
            latitude_zone = 'C'
        elif latitude_district < 3:
            latitude_zone = 'B'
        else:
            latitude_zone = 'A'
    return latitude_zone

# judge if the zone is one of the zones in melbGrid
def allocateZone(longitude_zone, latitude_zone):
    if longitude_zone == 1 and latitude_zone == 'A':
        twitter_zone = 'A1'
    elif longitude_zone == 2 and latitude_zone == 'A':
        twitter_zone = 'A2'
    elif longitude_zone == 3 and latitude_zone == 'A':
        twitter_zone = 'A3'
    elif longitude_zone == 4 and latitude_zone == 'A':
        twitter_zone = 'A4'
    elif longitude_zone == 1 and latitude_zone == 'B':
        twitter_zone = 'B1'
    elif longitude_zone == 2 and latitude_zone == 'B':
        twitter_zone = 'B2'
    elif longitude_zone == 3 and latitude_zone == 'B':
        twitter_zone = 'B3'
    elif longitude_zone == 4 and latitude_zone == 'B':
        twitter_zone = 'B4'
    elif longitude_zone == 1 and latitude_zone == 'C':
        twitter_zone = 'C1'
    elif longitude_zone == 2 and latitude_zone == 'C':
        twitter_zone = 'C2'
    elif longitude_zone == 3 and latitude_zone == 'C':
        twitter_zone = 'C3'
    elif longitude_zone == 4 and latitude_zone == 'C':
        twitter_zone = 'C4'
    elif longitude_zone == 5 and latitude_zone == 'C':
        twitter_zone = 'C5'
    elif longitude_zone == 3 and latitude_zone == 'D':
        twitter_zone = 'D3'
    elif longitude_zone == 4 and latitude_zone == 'D':
        twitter_zone = 'D4'
    elif longitude_zone == 5 and latitude_zone == 'D':
        twitter_zone = 'D5'
    else:
        twitter_zone = 'X0'
    return twitter_zone


# Transform twitter text into all lower case situation, and then split them with all possible mark
def transformTwitterText(twitter_text):
    twitter_text = twitter_text.lower()
    split_pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）'
    word_list = re.split(split_pattern, twitter_text)
    return word_list


# Use Binary Search to make sure if target word is in the emotion dictionary
# global variable emotion dictionary length
# dictionary_length = len(emotion_dictionary)
def searchEmotionDictionary(word_list, lower_bound, upper_bound, target_word):
    if upper_bound >= lower_bound:
        mid = (lower_bound + upper_bound) // 2
        if word_list[mid] == target_word:
            return mid
        elif word_list[mid] > target_word:
            return searchEmotionDictionary(word_list, lower_bound, mid - 1, target_word)
        else:
            return searchEmotionDictionary(word_list, mid + 1, upper_bound, target_word)
    else:
        return -1


# calculate happiness points for a twitter
def calculateHappinessPoints(twitter_content, word_points, emotion_dictionary):
    index = 0
    happiness_points = 0
    twitter_word_list = transformTwitterText(twitter_content['text'])
    # print(twitter_word_list)
    while index <= len(twitter_word_list) - 1:
        word_list_position = searchEmotionDictionary(emotion_dictionary, 0, len(emotion_dictionary) - 1, twitter_word_list[index])
        if word_list_position == -1:
            index += 1
            continue
        else:
            happiness_points += word_points[word_list_position]
            index += 1
    twitter_content['happiness_points'] = happiness_points
    return twitter_content


# add single happiness points to the zone happiness points
def sumHappinessPoints(twitter_content, zone_happiness_points):
    zone_happiness_points[twitter_content['zone']] += twitter_content['happiness_points']


# demo for testing tiny json twitter file
with open("smallTwitter.json", "r") as read_file:
    twitter_file = json.load(read_file)
total_twitter_count = len(twitter_file['rows'])
twitter_index = 0
[word_list, word_points_list] = readEmotionDictionary()
zone_happiness_points = initializeZoneHappinessPoints()
dictionary_length = len(word_list)
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
    twitter_word_list = transformTwitterText(twitter_content['text'])
    twitter_content = calculateHappinessPoints(twitter_content, word_points_list, word_list)
    sumHappinessPoints(twitter_content, zone_happiness_points)
print(zone_happiness_points)