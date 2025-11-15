"""
Module to check violations for a flight lesson.

This module processes the primary violations, which are violations of weather restrictions. 
Weather restrictions express the minimum conditions that a pilot is allowed to fly in.  
So if a pilot has a ceiling minimum of 2000 feet, and there is cloud cover at 1500 feet, 
the pilot should not fly.To understand weather minimums, you have to integrate three 
different files: daycycle.json (for sunrise and sunset), weather.json (for hourly weather 
observations at the airport), and minimums.csv (for the schools minimums set by agreement 
with the insurance agency). You should look at those files BRIEFLY to familiarize yourself 
with them.

This module can get overwhelming if you panic and think too much about the big picture.  
Like a good software developer, you should focus on the specifications and do a little
at a time.  While these functions may seem like they require a lot of FAA knowledge, all
of the information you need is in the specifications. They are complex specifications,
but all of the information you need is there.  Combined with the provided unit tests
in tests.py, this assignment is very doable.

It may seem weird that these functions only check weather conditions at the time of 
takeoff and not the entire time the flight is in the air.  This is standard procedure 
for this insurance company.  The school is only liable if they let a pilot take off in 
the wrong conditions.  If the pilot stays up in adverse conditions, responsibility shifts 
to the pilot.

The preconditions for many of these functions are quite messy.  While this makes writing 
the functions simpler (because the preconditions ensure we have less to worry about), 
enforcing these preconditions can be quite hard. That is why it is not necessary to 
enforce any of the preconditions in this module.

Author: Mike Hermann
Date: 08/14/2024
"""
import utils
import pilots
import os.path
import datetime


# WEATHER FUNCTIONS
def bad_visibility(visibility,minimum):
    """
    Returns True if the visibility measurement violates the minimum, False otherwise
    
    A valid visibility measurement is EITHER the string 'unavailable', or a dictionary 
    with (up to) four values: 'minimum', 'maximum',  'prevailing', and 'units'. Only 
    'prevailing' and 'units' are required; the other two are optional. The units may be 
    'FT' (feet) or 'SM' for (statute) miles, and explain how to interpret other three 
    fields, which are all floats.
    
    This function should compare the visibility 'minimum' (if it exists) against the 
    minimum parameter. Else it compares the 'prevailing' visibility. This function returns
    True if minimum is more than the measurement. If the visibility is 'unavailable', 
    then this function returns True (indicating bad record keeping).
    
    Example: Suppose we have the following visibility measurement.
        
        {
            "prevailing": 21120.0,
            "minimum": 1400.0,
            "maximum": 21120.0,
            "units": "FT"
        }
    
    Given the above measurement, this function returns True if visibility is 0.25 (miles)
    and False if it is 1.
    
    Parameter visibility: The visibility information
    Precondition: visibility is a valid visibility measurement, as described above.
    (e.g. either a dictionary or the string 'unavailable')
    
    Parameter minimum: The minimum allowed visibility (in statute miles)
    Precondition: minimum is a float or int
    """
    
    if visibility == 'unavailable':
        return True
    else:

        unit = visibility['units']
        if 'minimum' in visibility:
            min_visibility = visibility['minimum']

            if unit == 'FT':           # Convert to miles
                min_visibility = min_visibility / 5280.0

            if min_visibility < minimum:
                return True
            else:
                return False

        elif 'prevailing' in visibility:
            prev_visibility = visibility['prevailing']

            if unit == 'FT':           # Convert to miles
                prev_visibility = prev_visibility / 5280.0

            if prev_visibility < minimum:
                return True
            else:
                return False


def bad_winds(winds,maxwind,maxcross):
    """
    Returns True if the wind measurement violates the maximums, False otherwise
    
    A valid wind measurement is EITHER the string 'calm', the string 'unavailable' or 
    a dictionary with (up to) four values: 'speed', 'crosswind', 'gusts', and 'units'. 
    Only 'speed' and 'units' are required if it is a dictionary; the other two are 
    optional. The units will either be 'KT' (knots) or 'MPS' (meters per second), and 
    explain how to interpret other three fields, which are all floats.
    
    This function should compare 'speed' or 'gusts' against the maxwind parameter
    (whichever is worse) and 'crosswind' against the maxcross. If either measurement is greater
    than the allowed maximum, this function returns True.
    
    If the winds are 'calm', then this function always returns False. If the winds are
    'unavailable', then this function returns True (indicating bad record keeping).
    
    For conversion information, 1 MPS is roughly 1.94384 knots.
    
    Example: Suppose we have the following wind measurement.
        
        {
            "speed": 12.0,
            "crosswind": 10.0,
            "gusts": 18.0,
            "units": "KT"
        }
    
    Given the above measurement, this function returns True if maxwind is 15 or maxcross is 5.
    If both maxwind is 20 and maxcross is 10, it returns False.  (If 'units' were 'MPS'
    it would be false in both cases).
    
    Parameter winds: The wind speed information
    Precondition: winds is a valid wind measurement, as described above.
    (e.g. either a dictionary, the string 'calm', or the string 'unavailable')
    
    Parameter maxwind: The maximum allowable wind speed (in knots)
    Precondition: maxwind is a float or int
    
    Parameter maxcross: The maximum allowable crosswind speed (in knots)
    Precondition: maxcross is a float or int
    """

    wind_speed = 0.0
    wind_gust = 0.0
    cross_wind = 0.0
    high_speed = False
    high_xwind = False

    if winds == 'calm':
        return False

    elif winds == 'unavailable':
        return True

    else:
        unit = winds['units']
        if 'speed' in winds:
            wind_speed = winds['speed']
            if unit == 'MPS':           # Convert to knots
                wind_speed = wind_speed * 1.94384

        if 'gusts' in winds:
            wind_gust = winds['gusts']
            if unit == 'MPS':           # Convert to knots
                wind_gust = wind_gust * 1.94384

        if wind_speed > wind_gust:
            if wind_speed > maxwind:
                high_speed = True
            else:
                high_speed = False

        else:
            if wind_gust > maxwind:
                high_speed = True
            else:
                high_speed = False

        if 'crosswind' in winds:
            cross_wind = winds['crosswind']

            if unit == 'MPS':           # Convert to knots
                cross_wind = cross_wind * 1.94384

            if cross_wind > maxcross:
                high_xwind = True
            else:
                high_xwind = False

    if high_speed or high_xwind:
        return True
    else:
        return False


def bad_ceiling(ceiling,minimum):
    """
    Returns True if the ceiling measurement violates the minimum, False otherwise
    
    A valid ceiling measurement is EITHER the string 'clear', the string 'unavailable', 
    or a list of cloud layer measurements. A cloud layer measurement is a dictionary with 
    three required keys: 'type', 'height', and 'units'.  Type is one of 'a few', 
    'scattered', 'broken', 'overcast', or 'indefinite ceiling'. The value 'units' must 
    be 'FT', and specifies the units for the float associated with 'height'.
    
    If the ceiling is 'clear', then this function always returns False. If the ceiling 
    is 'unavailable', then this function returns True (indicating bad record keeping).
    Otherwise, it compares the minimum allowed ceiling against the lowest cloud layer 
    that is either 'broken', 'overcast', or 'indefinite ceiling'. If the only type of
    cloud layer is 'a few' or 'scattered', then this function should return False.
    
    Example: Suppose we have the following ceiling measurement.
        
        [
            {
                "cover": "clouds",
                "type": "scattered",
                "height": 700.0,
                "units": "FT"
            },
            {
                "type": "overcast",
                "height": 1200.0,
                "units": "FT"
            }
        ]
    
    Given the above measurement, this function returns True if minimum is 2000,
    but False if it is 1000.
    
    Parameter ceiling: The ceiling information
    Precondition: ceiling is a valid ceiling measurement, as described above.
    (e.g. either a dictionary, the string 'clear', or the string 'unavailable')
        
    Parameter minimum: The minimum allowed ceiling (in feet)
    Precondition: minimum is a float or int
    """
    height = 0.0

    if ceiling == 'clear':
        return False

    if ceiling == 'unavailable':
        return True

    if len(ceiling) == 1:
        if ((ceiling[0]['type'] == 'a few') or (ceiling[0]['type'] == 'scattered')):
            return False

        else:
            if ceiling[0]['height'] < minimum:
                return True
            
            else:
                return False

    else:
        for cover in ceiling:
            height = cover['height']

            if ((cover['type'] != 'a few') and (cover['type'] != 'scattered')):
                if height < minimum:
                    return True

        return False    


def get_weather_report(takeoff,weather):
    """
    Returns the most recent weather report at or before take-off.
    
    The weather is a dictionary whose keys are ISO formatted timestamps and whose values 
    are weather reports.  For example, here is an example of a (small portion of) a
    weather dictionary:
        
        {
            "2017-04-21T08:00:00-04:00": {
                "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704211056Z"
        },
        "2017-04-21T07:00:00-04:00": {
            "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "type": "overcast",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704210956Z"
        }
        ...
    },
    
    If there is a report whose timestamp matches the ISO representation of takeoff, 
    this function uses that report.  Otherwise it searches the dictionary for the most
    recent report before (but not equal to) takeoff.  If there is no such report, it
    returns None.
    
    Example: If takeoff was as 8 am on April 21, 2017 (Eastern), this function returns 
    the value for key '2017-04-21T08:00:00-04:00'.  If there is no additional report at
    9 am, a 9 am takeoff would use this value as well.
    
    Parameter takeoff: The takeoff time
    Precondition: takeoff is a datetime object
    
    Paramater weather: The weather report dictionary 
    Precondition: weather is a dictionary formatted as described above
    """
    # HINT: Looping through the dictionary is VERY slow because it is so large
    # You should convert the takeoff time to an ISO string and search for that first.
    # Only loop through the dictionary as a back-up if that fails.
    
    # Search for time in dictionary
    # As fall back, find the closest time before takeoff
    takeoff_weather = None
    close_key = None
    current_diff = datetime.timedelta(seconds=0)
    str_takeoff = takeoff.isoformat()
    #print('takeoff date: ', str_takeoff, 'take off time zone: ', takeoff.tzinfo)

    try:
        takeoff_weather = weather[str_takeoff]
        #print('takeoff weather: ', takeoff_weather)

        return takeoff_weather

    except:
        #print('take off weather not found with exact key')
        pass

    takeoff_date = takeoff.strftime("%Y-%m-%d")
    #if str_takeoff == '2017-03-12T03:00:00-05:00':
    #    print('take off date: ', takeoff_date)
       
    for key in weather:
        key_date = utils.str_to_time(key)
        key_day = utils.str_to_time(key).strftime("%Y-%m-%d")

        if key_day == takeoff_date:
            takeoff_tz = takeoff.replace(tzinfo=key_date.tzinfo)
            #if str_takeoff == '2017-03-12T03:00:00-05:00':
            #   print('key_date: ', key_date, 'key date time zone: ', key_date.tzinfo)
            #   print('new takeoff time: ', takeoff_tz, 'time zone: ', takeoff_tz.tzinfo)

            date_diff = takeoff_tz - key_date
            #if str_takeoff == '2017-03-12T03:00:00-05:00':
            #    print('date diff days: ', date_diff.days, 'date diff sec: ', date_diff.seconds)

            if date_diff.days >= 0 and date_diff.seconds > 0:
                if close_key == None or (date_diff <= current_diff):
                    current_diff = date_diff
                    close_key = key
                    #print('close key: ', close_key, 'close code: ', weather[close_key]['code'])

    takeoff_weather = weather[close_key]
    return takeoff_weather


def get_weather_violation(weather,minimums):
    """
    Returns a string representing the type of weather violation (empty string if flight is ok)
    
    The weather reading is a dictionary with the keys: 'visibility', 'wind', and 'sky'.
    These correspond to a visibility, wind, and ceiling measurement, respectively. It
    may have other keys as well, but these can be ignored. For example, this is a possible 
    weather value:
        
        {
            "visibility": {
                "prevailing": 21120.0,
                "minimum": 1400.0,
                "maximum": 21120.0,
                "units": "FT"
            },
            "wind": {
                "speed": 12.0,
                "crosswind": 3.0,
                "gusts": 18.0,
                "units": "KT"
            },
            "temperature": {
                "value": -15.6,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 2100.0,
                    "units": "FT"
                }
            ],
            "weather": [
                "light snow"
            ]
        }
    
    The minimums is a list of the four minimums ceiling, visibility, and max windspeed,
    and max crosswind speed in that order.  Ceiling is in feet, visibility is in statute
    miles, max wind and cross wind speed are both in knots. For example, 
    [3000.0,10.0,20.0,8.0] is a potential minimums list.
    
    This function uses bad_visibility, bad_winds, and bad_ceiling as helpers. It returns
    'Visibility' if the only problem is bad visibility, 'Winds' if the only problem is 
    wind, and 'Ceiling' if the only problem is the ceiling.  If there are multiple
    problems, it returns 'Weather', It returns 'Unknown' if no weather reading is 
    available (e.g. weather is None).  Finally, it returns '' (the empty string) if 
    the weather is fine and there are no violations.
    
    Parameter weather: The weather measure
    Precondition: weather is dictionary containing a visibility, wind, and ceiling measurement,
    or None if no weather reading is available.
    
    Parameter minimums: The safety minimums for ceiling, visibility, wind, and crosswind
    Precondition: minimums is a list of four floats
    """

    if weather == None:
        return 'Unknown'
    
    visibility = weather['visibility']
    winds = weather['wind']
    ceiling = weather['sky']

    min_ceiling = minimums[0]
    min_visibility = minimums[1]
    max_windspeed = minimums[2]
    max_xwinds = minimums[3]

    visibility_violation = bad_visibility(visibility,min_visibility)
    wind_violation = bad_winds(winds,max_windspeed,max_xwinds)
    ceiling_violation = bad_ceiling(ceiling,min_ceiling)

    if visibility_violation == False and wind_violation == False and ceiling_violation == False:
        return ''

    elif visibility_violation == True and wind_violation == False and ceiling_violation == False:
        return 'Visibility'
    
    elif visibility_violation == False and wind_violation == True and ceiling_violation == False:
        return 'Winds'

    elif visibility_violation == False and wind_violation == False and ceiling_violation == True:
        return 'Ceiling'

    else:
        return 'Weather'


# FILES TO AUDIT
# Sunrise and sunset
DAYCYCLE = 'daycycle.json'
# Hourly weather observations
WEATHER  = 'weather.json'
# The list of insurance-mandated minimums
MINIMUMS = 'minimums.csv'
# The list of all registered students in the flight school
STUDENTS = 'students.csv'
# The list of all take-offs (and landings)
LESSONS  = 'lessons.csv'


def list_weather_violations(directory):
    """
    Returns the (annotated) list of flight reservations that violate weather minimums.
    
    This function reads the data files in the given directory (the data files are all
    identified by the constants defined above in this module).  It loops through the
    list of flight lessons (in lessons.csv), identifying those takeoffs for which
    get_weather_violation() is not the empty string.
    
    This function returns a list that contains a copy of each violating lesson, together 
    with the violation appended to the lesson.
    
    Example: Suppose that the lessons
        
        S00687  548QR  I061  2017-01-08T14:00:00-05:00  2017-01-08T16:00:00-05:00  VFR  Pattern
        S00758  548QR  I072  2017-01-08T09:00:00-05:00  2017-01-08T11:00:00-05:00  VFR  Pattern
        S00971  426JQ  I072  2017-01-12T13:00:00-05:00  2017-01-12T15:00:00-05:00  VFR  Pattern
    
    violate for reasons of 'Winds', 'Visibility', and 'Ceiling', respectively (and are the
    only violations).  Then this function will return the 2d list
        
        [[S00687, 548QR, I061, 2017-01-08T14:00:00-05:00, 2017-01-08T16:00:00-05:00, VFR, Pattern, Winds],
         [S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, VFR, Pattern, Visibility],
         [S00971, 426JQ, I072, 2017-01-12T13:00:00-05:00, 2017-01-12T15:00:00-05:00, VFR, Pattern, Ceiling]]
    
    REMEMBER: VFR flights are subject to minimums with VMC in the row while IFR flights 
    are subject to minimums with IMC in the row.  The examples above are all VFR flights.
    If we changed the second lesson to
    
        S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, IFR, Pattern
    
    then it is possible it is no longer a visibility violation because it is subject to
    a different set of minimums.
    
    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files 'daycycle.json',
    'weather.json', 'minimums.csv', 'students.csv', and 'lessons.csv'
    """
    # Load in all of the files
    file_daycycle = utils.read_json(os.path.join(directory,DAYCYCLE))
    file_weather = utils.read_json(os.path.join(directory,WEATHER))
    file_minimums = utils.read_csv(os.path.join(directory,MINIMUMS))
    file_students = utils.read_csv(os.path.join(directory,STUDENTS))
    file_lessons = utils.read_csv(os.path.join(directory,LESSONS))
    
    result = []
    count = 0

    # For each of the lessons
    for lesson in file_lessons:
        if count == 0:
            pass
        else:
            # Get the takeoff time
            takeoff = utils.str_to_time(lesson[3])

            # Get lesson data
            instructor = lesson[2]
            area = lesson[6]

            if lesson[5] == 'VFR':
                filed = True
            else:
                filed = False

            if (instructor == ''):
                instructed = False
            else:
                instructed = True 

            # Get the pilot credentials
            student_data = utils.get_for_id(lesson[0], file_students)
            student_cert = pilots.get_certification(takeoff,student_data)
            #print('student_data: ', student_data)
            #print('student_cert: ', student_cert)

            day_flight = utils.daytime(takeoff,file_daycycle)
            #print('daytime: ', day_flight)

            # Get the pilot minimums
            student_mins = pilots.get_minimums(student_cert, area, instructed, filed, day_flight, file_minimums)
            #print('student_mins: ', student_mins)

            # Get the weather conditions
            flight_weather = get_weather_report(takeoff,file_weather)
            #print('weather elements: ', len(flight_weather))

            # Check for a violation and add to result if so
            violation = get_weather_violation(flight_weather,student_mins)
            #print('violation: ', violation)

            if (violation != '') and (violation != 'Unknown') and (violation != None):
                lesson.append(violation)
                result.append(lesson)

        count += 1

    return result

