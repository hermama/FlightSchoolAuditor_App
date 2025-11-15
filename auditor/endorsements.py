"""
Module to check endorsement violations for a flight lesson (OPTIONAL)

There are three kinds of endorsement violations. (1) A student has not soloed
but flies without an instructor.  (2) A student flies a plane that he or she
has no endorsement for. (3) A student files an invalid IFR flight (which could
be for several reasons).

This module is actually no more difficult than violations.py (and can be quite
easy if you have finished that already).  This material was cut to make the
project shorter.  To implement this module, you need to familiarize yourself
with two files beyond what you have used already.

First, instructors.csv is a CSV file with the following header:

    ID  LASTNAME  FIRSTNAME  CFI  CFII  MEI

This lists the instructors in the flight school. The first three columns are
general strings, while the last three columns are Yes/No strings. They indicate
whether the instructor can teach a student on a VFR flight, whether the
instructor can teach a student on an IFR flight, and whether the instructor
can teach a student on a multiengine flight.

Next, fleet.csv is a CSV file with the following header:

    TAILNO  TYPE  CAPABILITY  ADVANCED  MULTIENGINE ANNUAL  HOURS

This lists the planes at the flight school.  The first three columns are
general strings.  The third column is one of the strings VFR/IFR, indicating
if the plane is outfitted for instrument flight.  The fourth and fifth columns
are Yes/No strings indicating the endorsments required for this plane.  The
last two columns may be ignored for this module.

The preconditions for many of these functions are quite messy.  While this
makes writing the functions simpler (because the preconditions ensure we have
less to worry about), enforcing these preconditions can be quite hard. That is
why it is not necessary to enforce any of the preconditions in this module.

Author: Mike Hermann
Date: 08/16/2024
"""
import pilots
import utils
import os.path
import datetime


def teaches_multiengine(instructor):
    """
    Returns True if this instructor can teach a student on a multiengine flight.
    False otherwise.
    
    Parameter instructor: The flight instructor
    Precondition: instructor is a 6-element list of strings representing an instructor
    """

    if instructor[5] == 'Yes':
        return True

    else:
        return False


def teaches_instrument(instructor):
    """
    Returns True if this instructor can teach a student on an IFR flight.
    False otherwise.
    
    Parameter instructor: The flight instructor
    Precondition: instructor is a 6-element list of strings representing an instructor
    """

    if instructor[4] == 'Yes':
        return True

    else:
        return False


def is_advanced(plane):
    """
    Returns True if the plane requires an advanced endorsement; False otherwise.
    
    Parameter plane: The school airplane
    Precondition: plane is a 7-element list of strings representing an airplane
    """

    if plane[3] == 'Yes':
        return True

    else:
        return False


def is_multiengine(plane):
    """
    Returns True if the plane requires a multiengine endorsement; False otherwise.
    
    Parameter plane: The school airplane
    Precondition: plane is a 7-element list of strings representing an airplane
    """

    if plane[4] == 'Yes':
        return True

    else:
        return False


def is_ifr_capable(plane):
    """
    Returns True if the plane is outfitted for IFR flight; False otherwise.
    
    NOTE: Just because a plane is IFR capable, does not mean that every flight
    with it is an IFR flight.
    
    Parameter plane: The school airplane
    Precondition: plane is a 7-element list of strings representing an airplane
    """

    if plane[2] == 'IFR':
        return True

    else:
        return False


def bad_endorsement(takeoff,student,instructor,plane):
    """
    Returns True if the student or instructor did not have the right endorsement.
    
    The endorsement depends on the plane type (advanced, multiengine).  All
    instructors are certified for advanced planes, so a flight with an instructor
    is only a problem if the plane is multiengine and the instructor does not
    have an MEI.
    
    If there is no instructor, the student must be endorsed for this type of
    plane before the time of takeoff.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    
    Parameter instructor: The flight instructor
    Precondition: instructor is a 6-element list of strings representing an instructor
    
    Parameter plane: The school airplane
    Precondition: plane is a 7-element list of strings representing an airplane
    """
    assert type(takeoff) == datetime.datetime

    #print('takeoff: ', takeoff,'/ takeoff_type: ', type(takeoff))
    #print('student: ', student)
    #print('instructor: ', instructor)
    #print('plane: ', plane)
    student_endorsed_multi = False
    student_endorsed_advance = False
    instructor_endorsed_multi = False
    instructor_endorsed_advance = True
    instructor_teaches_ifr = False


    plane_ifr_capable = is_ifr_capable(plane)
    plane_advanced = is_advanced(plane)
    plane_multieng = is_multiengine(plane)
    #print('plane_ifr_capable: ', plane_ifr_capable, '/ plane advanced: ', plane_advanced, \
    #      '/ plane_multieng: ', plane_multieng)

    student_certified = pilots.get_certification(takeoff,student)
    student_advanced = pilots.has_advanced_endorsement(takeoff,student)
    student_multieng = pilots.has_multiengine_endorsement(takeoff,student)

    if plane_multieng == True or plane_advanced == True:
        if plane_multieng == True and student_multieng == True:
            student_endorsed_multi = True

        elif plane_multieng == True and student_multieng == False:
            student_endorsed_multi = False

        if plane_advanced == True and student_advanced == True:
            student_endorsed_advance = True

        elif plane_advanced == True and student_advanced == False:
            student_endorsed_advance = False

        if instructor != None:
            instructor_teaches_ifr = teaches_instrument(instructor)
            instructor_multieng = teaches_multiengine(instructor)
        else:
            instructor_teaches_ifr = False
            instructor_multieng = False

        if plane_multieng == True and instructor_multieng == False:
            instructor_endorsed_multi = False
        elif plane_multieng == True and instructor_multieng == True:
            instructor_endorsed_multi = True
        else:
            instructor_endorsed_multi = False

        #print('std endorsed_multi: ', student_endorsed_multi, ' / std endorsed_advance: ', \
        #      student_endorsed_advance)
        #print('inst endorsed_multi: ', instructor_endorsed_multi, ' / inst teaches_ifr: ', \
        #    instructor_teaches_ifr )

        if ((instructor == None) and (plane_advanced == True) and (plane_multieng == False) and \
            (student_endorsed_advance == False)) or \
           ((instructor == None) and (plane_advanced == True) and (plane_multieng == True) and \
            (student_endorsed_multi == False)) or \
           ((instructor != None) and (plane_multieng == True) and \
            (instructor_endorsed_multi == False)): # or \
            return True
        else:
            return False

    else:
        return False


def bad_ifr(takeoff,student,instructor,plane):
    """
    Returns True if the student, instructor, or plane is not certified for IFR.
    
    For an IFR flight to be valid, the plane must be outfitted for IFR.  If there
    is an instructor, that instructor must have a CFII. If the student is alone,
    the student must have an instrument rating at the time of takeoff.
    
    NOTE: The precondition for takeoff does not assume anything about the flight. 
    It may be a VFR flight not subject to IFR rules.  This function should still
    return False if that flight COULD have been a successful IFR flight.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    
    Parameter instructor: The flight instructor
    Precondition: instructor is a 6-element list of strings representing an instructor
    
    Parameter plane: The school airplane
    Precondition: plane is a 7-element list of strings representing an airplane
    """
    assert type(takeoff) == datetime.datetime

    # print('takeoff: ', takeoff,'/ takeoff_type: ', type(takeoff))
    # print('student: ', student)
    # print('instructor: ', instructor)
    # print('plane: ', plane)
    instructor_endorsed_multi = False
    instructor_endorsed_advance = True
    instructor_teaches_ifr = False

    plane_ifr_capable = is_ifr_capable(plane)
    plane_advanced = is_advanced(plane)
    plane_multieng = is_multiengine(plane)
    # print('plane_ifr_capable: ', plane_ifr_capable)

    student_instrument_rated = pilots.has_instrument_rating(takeoff,student)
    student_advanced = pilots.has_advanced_endorsement(takeoff,student)
    student_multieng = pilots.has_multiengine_endorsement(takeoff,student)

    # print('instructor: ', instructor)
    if instructor != None:
        instructor_teaches_ifr = teaches_instrument(instructor)
        instructor_multieng = teaches_multiengine(instructor)
    else:
        instructor_teaches_ifr = False
        instructor_multieng = False

    # print('std endorsed_multi: ', student_multieng, ' / std endorsed_advance: ', \
    #       student_advanced, 'std instrumnt rated: ', student_instrument_rated)
    # print('inst endorsed_multi: ', instructor_endorsed_multi, ' / inst teaches_ifr: ', \
    #     instructor_teaches_ifr )

    if plane_ifr_capable == False:
        return True

    elif ((instructor == None) and (plane_ifr_capable == True) and (plane_advanced == True) and \
        (student_advanced == False)):
        return True

    elif ((instructor == None) and (plane_ifr_capable == True) and (plane_multieng == True) and \
        (student_multieng == False)):
        return True

    elif ((instructor == None) and (plane_ifr_capable == True) and ((student_multieng == False) and \
        (student_advanced == False) and (student_instrument_rated == False))):
        return True
        
    elif ((instructor != None) and (plane_ifr_capable == True) and (instructor_teaches_ifr == False)):
        return True

    else:
        return False


# FILENAMES
# Sunrise and sunset (mainly useful for timezones, since repairs do not have them)
DAYCYCLE = 'daycycle.json'
# The list of all take-offs (and landings)
LESSONS  = 'lessons.csv'
# The list of all registered students in the flight school
STUDENTS = 'students.csv'
# The list of all certified instructors in the flight school
TEACHERS = 'instructors.csv'
# The list of all planes in the flight school
PLANES   = 'fleet.csv'
# The list of all repairs made to planes over the past year
REPAIRS  = 'repairs.csv'


def list_endorsement_violations(directory):
    """
    Returns the (annotated) list of flight lessons that violate endorsement
    or rating regulations.
    
    This function reads the data files in the given directory (the data files
    are all identified by the constants defined above in this module).  It loops
    through the list of flight lessons (in lessons.csv), identifying those
    takeoffs for which (1) a student has not soloed but flies without an instructor,
    (2) a student or instructor flies a plane that he or she has no endorsement
    for, (3) a student files an invalid IFR flight.
    
    This function returns a list that contains a copy of each violating lesson,
    together with the violation appended to the lesson.  Violation of type (1)
    is annotated 'Solo'.  Violation of type (2) is annotated 'Endorsement'.
    Violations of type (3) is annotated 'IFR'.  If more than one is violated,
    it should be annotated 'Credentials'.
    
    Example: Suppose that the lessons
    
        S00898  426JQ        2017-01-02T11:00:00-05:00  2017-01-02T13:00:00-05:00  VFR  Pattern
        S00811  811AX  I077  2017-01-07T10:00:00-05:00  2017-01-07T12:00:00-05:00  IFR	Pattern
        S00526  446BU        2017-01-16T08:00:00-05:00	2017-01-16T10:00:00-05:00  VFR	Practice Area
    
    violate for reasons of 'SOLO', 'IFR', and 'Endorsement', respectively (and
    are the only violations).  Then this function will return the 2d list
    
        [['S00898', '426JQ', '',     '2017-01-02T11:00:00-05:00', '2017-01-02T13:00:00-05:00', 'VFR', 'Pattern', 'Solo'],
         ['S00811', '811AX', 'I077', '2017-01-07T10:00:00-05:00', '2017-01-07T12:00:00-05:00', 'IFR', 'Pattern', 'IFR'],
         ['S00526', '446BU', '',     '2017-01-16T08:00:00-05:00', '2017-01-16T10:00:00-05:00', 'VFR', 'Practice Area', 'Endorsement']]
    
    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files
    'daycycle.json', 'students.csv', 'instructors.csv', 'fleet.csv' and
    'lessons.csv'
    """
    # Load in all of the files
    file_daycycle = utils.read_json(os.path.join(directory,DAYCYCLE))
    file_lessons = utils.read_csv(os.path.join(directory,LESSONS))
    file_students = utils.read_csv(os.path.join(directory,STUDENTS))
    file_teachers = utils.read_csv(os.path.join(directory,TEACHERS))
    file_planes = utils.read_csv(os.path.join(directory,PLANES))
    file_repairs = utils.read_csv(os.path.join(directory,REPAIRS))
    
    
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

            # Get student, plane, and instructor data
            student_data = utils.get_for_id(lesson[0], file_students)
            plane_data = utils.get_for_id(lesson[1], file_planes)
            instructor_data = utils.get_for_id(lesson[2], file_teachers)

            # Check if the student is allowed to fly by themselves
            student_instrument_rated = pilots.has_instrument_rating(takeoff,student_data)
            student_advanced = pilots.has_advanced_endorsement(takeoff,student_data)
            student_multieng = pilots.has_multiengine_endorsement(takeoff,student_data)

            # Check if pilot/instructor is endorsed for the plane
            flight_not_endorsed = bad_endorsement(takeoff,student_data,instructor_data,plane_data)

            # Check if pilot/instructor is permitted to fly IFR in this plane
            flight_not_ifr_approved = bad_ifr(takeoff,student_data,instructor_data,plane_data)

            if (instructor == '' and lesson[5] == 'IFR' and student_instrument_rated == False):
                violation = 'SOLO'

            elif (flight_not_endorsed == True):
                violation = 'Endorsement' 

            elif(lesson[5] == 'IFR' and flight_not_ifr_approved == True):
                violation = 'IFR' 

            else:
                violation = ''

            # if lesson[0] == 'S00526':
            #     print('student: ', student_data)
            #     print('teacher: ', instructor_data)
            #     print('plane: ', plane_data)
            #     print('lesson: ', lesson)
            #     print('std endorsed_multi: ', student_multieng, ' / std endorsed_advance: ', \
            #       student_advanced, 'std instrumnt rated: ', student_instrument_rated)
            #     print('violation:', violation)

            # Add any violations to the result
            if (violation != ''):
                lesson.append(violation)
                result.append(lesson)

        count += 1

    return result
