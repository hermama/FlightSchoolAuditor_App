"""
Module to check inspection violations for a flight lesson (OPTIONAL)

There are three kinds of inspection violations. (1) A plane has gone more than
a year since its annual inspection. (2) A plane has accrued 100 hours of flight
time since its last regular inspection. (3) A plane is used for a lesson despite
the repair logs claiming that it is in the shop for maintenance.

This module is MUCH more difficult than the others.  In the other modules, we
provided specifications for all of the helper functions, to make the main
function (listing all violations) easier.  We do not do that at all here.
You have one specification for one function.  Any additional functions (which
we do recommend) are up to you.

The other tricky part is keeping track of the hours since the last inspection
for each plane.  It is possible to do this with a nested loop, but the result
will be very slow (the application will take several minutes to complete).
To speed it up, you have to figure out how to "interleave" lessons with repairs.
This is a very advanced programming problem.

To implement this module, you need to familiarize yourself with two files
beyond what you have used already.

First of all, recall that fleet.csv is a CSV file with the following header:

    TAILNO  TYPE  CAPABILITY  ADVANCED  MULTIENGINE ANNUAL  HOURS

This lists the planes at the flight school.  For this module you need the
last two columns, which are strings representing a date and an number,
respectively.  The date is the last annual inspection for that plane as of
the beginning of the year (e.g. the start of the audit).  The number is
the number of hours since the last 100 hour inspection.

In addition, repairs.csv is a CSV file with the following header:

    TAILNO  IN-DATE  OUT-DATE  DESCRIPTION

The first column is the string identifying the plane.  The next two columns are
strings representing dates, for when the plane enters and leaves the shop (so
it should not fly during this time).  The last column is the type of repair.
A plane must be inspected/repaired every 100 hours.  In addition, it must have
an annual inspection once a year.  Other repairs happen as needed.  ANY repair
resets the number of hours on the plane.

The preconditions for many of these functions are quite messy.  While this
makes writing the functions simpler (because the preconditions ensure we have
less to worry about), enforcing these preconditions can be quite hard. That is
why it is not necessary to enforce any of the preconditions in this module.

Author: Mike Hermann
Date: 08/19/2024
"""
import os.path
import datetime
import utils

# FILENAMES
# Sunrise and sunset (mainly useful for timezones, since repairs do not have them)
DAYCYCLE = 'daycycle.json'
# The list of all take-offs (and landings)
#LESSONS  = 'lessons.csv'
LESSONS  = 'lessons-mini.csv'
# The list of all planes in the flight school
PLANES   = 'fleet.csv'
# The list of all repairs made to planes over the past year
REPAIRS  = 'repairs.csv'


def get_repairs(plane, repairs, takeoff):
    """
    Returns inspection records that occurred before the lesson takeoff time.

    The inspections is the 2-dimensional list (table) of repairs, including the header.
    The header for this table is as follows:

        TAIL NO,IN DATE,OUT DATE,DESCRIPTION

    If there are no rows that match the parameters this function returns None.

    Parameter plane: The school airplane
    Precondition: plane is a string representing an airplane id

    Parameter repairs: The school airplane
    Precondition: plane is a 4-element list of strings representing an airplane's repair history

    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object with a time zone
    """
    # Find all rows that can apply to this plane
    cert_time = '00:00'
    count = 0
    matches = []
    print('======= Run get repair data =======')

    for row in repairs:
        print('row: ', row)
        tail_id = row[0]
        time_in = row[1] + "T" + cert_time
        time_out = row[2] + "T" + cert_time
        repair_description = row[3]

        repair_in_date = utils.str_to_time(time_in,takeoff)
        repair_out_date = utils.str_to_time(time_out,takeoff)

        if tail_id == '684TM':
            print('takeoff: ', takeoff)
            print('time in: ', repair_in_date)
            print('time out: ', repair_out_date)

        if count > 0 and tail_id == '684TM':
            print('plane id: ', plane, '/ tail_id', tail_id)
            print('prev repair date: ', (repair_in_date < takeoff))

        if count > 0 and (tail_id == plane) and (repair_in_date < takeoff):
            print('### match found ###')
            print('tail id: ', tail_id)
            matches.append(row)
            print('matches: ', matches)
        else:
            pass

        count += 1

    print('num matches: ', len(matches))
    if len(matches) > 0:
        return matches

    else:
        return None

def list_inspection_violations(directory):
    """
    Returns the (annotated) list of flight lessons that violate inspection
    or repair requirements.

    This function reads the data files in the given directory (the data files
    are all identified by the constants defined above in this module).  It loops
    through the list of flight lessons (in lessons.csv), identifying those
    takeoffs for which (1) a plane has gone MORE than a year since its annual
    inspection, (2) a plane has accrued OVER 100 hours of flight time since its
    last repair or inspection, and (3) a plane is used for a lesson despite
    the repair logs claiming that it is in the shop for maintenance.

    Note that a plane landing with exactly 100 hours used is not a violation.
    Nor is a plane that has flown with 365 days since its last inspection. This
    school likes to cut things close to safe money, but these are technically
    not violations.

    This function returns a list that contains a copy of each violating lesson,
    together with the violation appended to the lesson.  Violation of type (1)
    is annotated 'Annual'.  Violation of type (2) is annotated 'Inspection'.
    Violations of type (3) is annotated 'Grounded'.  If more than one is
    violated, it should be annotated 'Maintenance'.

    Example: Suppose that the lessons

        S00898  811AX  I072  2017-01-27T13:00:00-05:00  2017-01-27T15:00:00-05:00  VFR  Pattern
        S00681  684TM  I072  2017-02-26T14:00:00-05:00  2017-02-26T17:00:00-05:00  VFR  Practice Area
        S01031  738GG  I010  2017-03-19T13:00:00-04:00  2017-03-19T15:00:00-04:00  VFR  Pattern

    violate for reasons of 'Annual', 'Inspection', and 'Grounded', respectively
    (and are the only violations).  Then this function will return the 2d list

        [['S00898', '811AX', 'I072', '2017-01-27T13:00:00-05:00', '2017-01-27T15:00:00-05:00', 'VFR', 'Pattern', 'Annual'],
         ['S00681', '684TM', 'I072', '2017-02-26T14:00:00-05:00', '2017-02-26T17:00:00-05:00', 'VFR', 'Practice Area', 'Inspection'],
         ['S01031', '738GG', 'I010', '2017-03-19T13:00:00-04:00', '2017-03-19T15:00:00-04:00', 'VFR', 'Pattern', 'Grounded']]

    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files
    'daycycle.json', 'fleet.csv', 'repairs.csv' and 'lessons.csv'
    """
    # Load in all of the files
    file_daycycle = utils.read_json(os.path.join(directory,DAYCYCLE))
    file_lessons = utils.read_csv(os.path.join(directory,LESSONS))
    file_planes = utils.read_csv(os.path.join(directory,PLANES))
    file_repairs = utils.read_csv(os.path.join(directory,REPAIRS))

    cert_time = '00:00'
    violation = ''
    last_repair_date = None
    last_annual_repair_date = None

    result = []
    count = 0

    # For each of the lessons
    for lesson in file_lessons:
        print('lesson: ', lesson)
        if count == 0:
            pass
        else:
            # Get the takeoff and landing times
            takeoff = utils.str_to_time(lesson[3])
            landing = utils.str_to_time(lesson[4])
            print('takeoff: ', takeoff)
            print('landing: ', landing)

            # Get plane and repair data using plane ID
            plane_data = utils.get_for_id(lesson[1], file_planes)
            print('plane_data: ', plane_data)
            repair_data = get_repairs(plane_data[0], file_repairs, takeoff)
            print('repair_data: ', repair_data, 'num recs: ', len(repair_data))

        count += 1

    return result
"""
            if len(repair_data) > 0:
                for repair in repair_data:
                    print('repair rec: ', repair)
                    time_in = repair[1] + "T" + cert_time
                    time_out = repair[2] + "T" + cert_time
                    repair_description = repair[3]
                    print('time in: ', time_in)
                    print('time out: ', time_out)

                    repair_in_date = utils.str_to_time(time_in,takeoff)
                    repair_out_date = utils.str_to_time(time_out,takeoff)
                    print('time in: ', repair_in_date)
                    print('time out: ', repair_out_date)

                    if last_repair_date == None:
                        last_repair_date = repair_out_date
                    elif repair_out_date > last_repair_date:
                        last_repair_date = repair_out_date

                    if repair_description == 'annual inspection' and last_annual_repair_date == None:
                        last_annual_repair_date = repair_out_date
                    elif repair_description == 'annual inspection' and last_annual_repair_date < repair_out_date:
                        last_annual_repair_date = repair_out_date

                    if (takeoff > repair_in_date) and (landing < repair_out_date):      # flight during maintenance
                        violation = 'Grounded'

                    elif (landing < repair_in_date):    # flight before maintenance
                        time_since_last_repair_takeoff = takeoff - last_repair_date
                        time_since_last_repair_landing = landing - last_repair_date
                        print('time since last repair takeoff: ', time_since_last_repair_takeoff)
                        print('time since last repair landing: ', time_since_last_repair_landing)

                        if last_annual_repair_date != None:
                            time_since_last_annual = takeoff - last_annual_repair_date
                            print('time since last annual: ', time_since_last_annual)

                        if time_since_last_repair_takeoff.seconds > 360000 or \
                            time_since_last_repair_landing.seconds > 360000:
                            violation = 'Inspection'

                    elif (takeoff > repair_out_date):    # flight after maintenance
                        pass

                    # if (time_since_last_annual.days > 365):
                    #     violation = 'Annual'

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
"""
