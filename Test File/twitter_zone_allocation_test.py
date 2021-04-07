def calculateLongitudeZone(coordinates):
    longitude = coordinates[0]
    relative_longitude = format((longitude - 144.7), '.8f')
    relative_longitude = float(relative_longitude)
    print(relative_longitude)
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
    print(relative_latitude)
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



input_coordinates = [144.85, -37.8]
longitude_zone = calculateLongitudeZone(input_coordinates)
latitude_zone = calculateLatitudeZone(input_coordinates)
print(latitude_zone, longitude_zone)
print(allocateZone(longitude_zone, latitude_zone))