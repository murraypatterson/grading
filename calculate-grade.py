import sys
import csv
import argparse

#
# process weighted groups from a groups file
'''

   Note that a groups file is expected to have the format:

   ```
      ## some comment, any comment
      header column one
      header column two
      ...

      # homework 0.3
      Homework Week 1 [Total Pts: 100 Score] |...
      ...

      # midterm 0.2
      Midterm [Total Pts: 100 Score] |...
   ```

   where the first line starts with `##` and then contains some header
   columns (which do not count).  Then, the remaining "groups",
   starting with `#`, indicate groups of columns (e.g., "homework")
   which group together a set of items, each of which together have
   some weight towards the total grade for the course (e.g., 0.3, or
   30% of the grade comes from homework)

   Note that the set of columns comes from the csv, and so the
   expected way to get this groups file is to run

      `python calculate-grade.py -c grades.csv > groups.txt`

   and then to manually group columns, giving meaningful group names,
   and then weighting according to the breakdown (e.g., in the
   syllabus) of the final grade

   It is important to do it this way (not only because there a sanity
   check to ensure the columns of the group match that of the input
   csv file, but) because another thing which is done is the
   collection of scores for each column (e.g., [Total Pts: 100
   Score]).  At the moment, the actual score of each column is just
   normalized by this score, averaged, and then weighted by the group
   weight, i.e., each column contributes equally to the group.  If we
   wanted otherwise, the most general solution would be to have a set
   of column-specific weights, so that we would be taking a weighted
   average rather than weighting an average afterwords --- could be a
   solution for the future

'''
def process_groups(lines) :

    group = None
    groups = {}
    weight = {} # weight of a group
    universe = set([]) # universal set of columns
    score = {} # score for individual column

    for line in lines :

        # skip empty lines
        if not line.strip() :
            continue

        # the header group (groups file must start with a `##`)
        if line.startswith('##') :

            assert not group
            group = 'header'

            groups[group] = []
            weight[group] = float(0)

            continue

        # new group
        if line.startswith('#') :

            # set current group (weight)
            h, group, w = line.split()

            groups[group] = []
            weight[group] = float(w)

        # column of (the current) group
        else :

            column = line.strip()
            for sep in ['Score]', 'Percentage]'] :
                if sep in column :
                    column = column.split(sep,1)[0] + sep

            universe.add(column)

            assert group
            groups[group].append(column)

            if group == 'header' :
                continue

            # non-header group stuff..
            aux = column.split('[Total Pts:',1)[1]
            score[column] = float(aux.split('Score]',1)[0].strip())

    # weights should add up to 1
    regular = groups.keys() - ['bonus'] # exclude special "bonus" group
    assert round(sum(weight[group] for group in regular), 6) == float(1)

    return universe, groups, weight, score

#
# process a letter grading scheme from a scheme file
def process_scheme(lines) :

    letter = {}
    gpa = {}
    for line in lines :

        # skip empty lines or "comment" lines
        if not line.strip() :
            continue

        if line.startswith('#') :
            continue

        # A 4 93
        letter_grade, gpa_grade, grade = line.split()
        grade = float(grade)

        assert grade >= float(0)
        assert grade <= float(100)

        letter[grade] = letter_grade
        gpa[grade] = float(gpa_grade)

    return letter, gpa

#
# return a letter grade, given a grade and a letter grading scheme
def letter_grade(letter, grade) :

    indices = sorted(letter.keys())
    index = indices[0]
    for i in indices :

        if grade < i :
            break
        index = i

    return letter[index]

#
# Parser
#----------------------------------------------------------------------

parser = argparse.ArgumentParser(description = '''

   Do various things with a csv file downloaded from Blackboard,
   essentially inferring the final grade by aggregating weighted
   groups of columns.  Output is a table with the weighted groups, and
   the final grade to stdout

''', epilog = '''

   Note: that the output could be generalized to a choice of groups,
   or even better, output a csv file with the (added) groups.

   Also note: for some reason, the first character (an underscore-type
   character) of the csv that Blackboard dumps causes ascii decoding
   issues --- the current work-around is to open up this csv file and
   delete this character.  This should be fixed in the future

''')

parser.add_argument(
    'file', metavar = 'file.csv',
    type = argparse.FileType('r'), default = sys.stdin,
    help = 'input (csv) file (default: stdin)')
parser.add_argument(
    '-c', '--columns',
    action = 'store_true',
    help = 'dump column names of csv and exit')
parser.add_argument(
    '-g', '--groups', metavar = 'groups.txt',
    type = argparse.FileType('r'),
    help = 'file containing the weighted groups')
parser.add_argument(
    '-l', '--letter', metavar = 'scheme.txt',
    type = argparse.FileType('r'),
    help = 'add column of letter grades according to scheme.txt')
parser.add_argument(
    '-t', '--tabseparated',
    action = 'store_true',
    help = 'output in tab-separated format (default is CSV)')

args = parser.parse_args()

#
# Main
#----------------------------------------------------------------------

# process the groups, if applicable
universe, groups, weight, score = None, None, None, None
columns = []
if args.groups :

    universe, groups, weight, score = process_groups(args.groups)

    # gather groups we want to report (i.e., those which carry weight)
    for group in groups :
        if weight[group] :
            columns.append(group)

    # print header
    sep = '\t' if args.tabseparated else ','
    print('First', 'Last', sep = sep, end = sep)
    if args.letter :
        print('Letter', end = sep)
    print('Grade', 'Course', sep = sep, end = sep)
    print(*('{:s}({:.3f})'.format(col, weight[col]) for col in columns), sep = sep)

# process letter grading scheme, if applicable
letter = None
gpa = None
if args.letter :
    letter, gpa = process_scheme(args.letter)

# read in csv as a dictionary
rows = csv.DictReader(args.file)

raw_columns = {}
count = 0
for row in rows :

    # first row, do some prep
    if not count :

        if args.columns :

            # dump column names of the header and exit
            for column in row :
                print(column)

            sys.exit(0)

        if args.groups :

            # gather raw columns dict, check that columns match groups
            for column in row :

                col = column.strip()
                for sep in ['Score]', 'Percentage]'] :
                    if sep in col :
                        col = col.split(sep,1)[0] + sep

                raw_columns[col] = column

            assert raw_columns.keys() == universe, universe ^ raw_columns.keys()

        # no need to proceed w\o the groups..
        else :
            sys.exit(0)

    # now move on with the student profile
    course = float(0)
    for group in groups :
        if group == 'header' : # blow by the header
            continue

        total = float(0)
        for column in groups[group] :

            grade = float(0)
            raw = row[raw_columns[column]]

            if raw == 'Needs Grading' : # just a warning here
                print('warning: a column needs grading', file = sys.stderr)

            if raw.startswith('In Progress') :
                print('warning: a column is in progress', file = sys.stderr)

                raw = raw.strip('In Progress')
                raw = raw.lstrip('(').rstrip(')') # 2nd attempt in progress

            if raw : # column is "" (not submitted)
                grade = float(raw)

            total += grade / score[column] # add normalized score

        # take average, weight it, and add it to final course grade
        row[group] = total * weight[group] / len(groups[group])
        course += row[group]

    row['course'] = course
    grade = round(float(100) * row['course'])

    # print out student profile in terms of groups
    sep = '\t' if args.tabseparated else ','
    print(row['First Name'], row['Last Name'], sep = sep, end = sep)
    if args.letter :
        print(letter_grade(letter, float(grade)), end = sep)
    print(grade, '{:.6f}'.format(row['course']), sep = sep, end = sep)
    print(*('{:.6f}'.format(row[col]) for col in columns), sep = sep)

    count += 1
