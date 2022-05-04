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

      # homework 0.5 drop 1
      Homework 1 Points Grade <Numeric MaxPoints:100>
      ...

      # midterm 0.25
      Midterm Exam Points Grade <Numeric MaxPoint:100>
   ```

   where the first line starts with `##` and then contains some header
   columns (which do not count).  Then, the remaining "groups",
   starting with `#`, indicate groups of columns (e.g., "homework")
   which group together a set of items, each of which together have
   some weight towards the total grade for the course (e.g., 0.5, or
   50% of the grade comes from homework).  Note that "drop <number>"
   is optional: it means "drop the lowest <number> items in group".

   Note that the set of columns comes from the csv, and so the
   expected way to get this groups file is to run

      `python calculate-grade.py -c grades.csv > groups.txt`

   and then to manually group columns, giving meaningful group names,
   and then weighting according to the breakdown (e.g., in the
   syllabus) of the final grade

   It is important to do it this way (not only because there a sanity
   check to ensure the columns of the group match that of the input
   csv file, but) because another thing which is done is the
   collection of scores for each column (e.g., <Numeric
   MaxPoints:100>).  At the moment, the actual score of each column is
   just normalized by this score, averaged, and then weighted by the
   group weight, i.e., each column contributes equally to the group.
   If we wanted otherwise, the most general solution would be to have
   a set of column-specific weights, so that we would be taking a
   weighted average rather than weighting an average afterwords ---
   could be a solution for the future

'''
def process_groups(lines) :

    group = None
    universe = set([]) # universal set of columns
    members = {} # members of a group
    weight = {} # weight of a group
    drop = {} # number to drop from a group
    score = {} # score for individual column

    for line in lines :

        # skip empty lines
        if not line.strip() :
            continue

        # the header group (groups file must start with a `##`)
        if line.startswith('##') :

            assert not group
            group = 'header'

            members[group] = []
            weight[group] = float(0)
            drop[group] = 0
            
            continue

        # new group
        if line.startswith('#') :

            # set current group (weight)
            _, group, w, *tail = line.split()

            members[group] = []
            weight[group] = float(w)

            n = 0
            if tail :
                _, n = tail

            drop[group] = int(n)

        # column of (the current) group
        else :

            column = line.strip()
            universe.add(column)

            assert group
            members[group].append(column)

            if group == 'header' :
                continue

            # non-header group stuff..
            _, aux = column.split('<Numeric MaxPoints:', 1)
            score[column] = float(aux.rstrip('>'))

    # weights should add up to 1
    assert round(sum(weight[g] for g in members), 6) == float(1)

    return universe, members, weight, drop, score

#
# process a letter grading scheme from a scheme file
def process_scheme(handle) :

    letter = {}
    rows = csv.DictReader(handle)
    a, b = rows.fieldnames

    for row in rows :
        letter[float(row[b])] = row[a]

    return letter

#
# return a letter grade, given a grade and a letter grading scheme
def letter_grade(letter, numerical) :

    indices = sorted(letter)
    index = indices[0]
    for i in indices :

        if numerical < i :
            break

        index = i

    return letter[index]

#
# Parser
#----------------------------------------------------------------------

parser = argparse.ArgumentParser(description = '''

   Do various things with a csv file downloaded from iCollege,
   essentially inferring the final grade by aggregating weighted
   groups of columns.  Output is a table with the weighted groups, and
   the final grade to stdout

''', epilog = '''

   Note: that the output could be generalized to a choice of groups,
   or even better, output a csv file with the (added) groups.

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
    '-l', '--letter', metavar = 'scheme.csv',
    type = argparse.FileType('r'),
    help = 'add a column of letter grades according to scheme')

parser.add_argument(
    '-t', '--tabs',
    action = 'store_true',
    help = 'output in tab-separated format (default is CSV)')

parser.add_argument(
    '-u', '--human',
    action = 'store_true',
    help = 'for inputting a human-readable grades (csv) file')

args = parser.parse_args()

#
# Main
#----------------------------------------------------------------------

# read in csv as a dictionary
rows = csv.DictReader(args.file)
columns = rows.fieldnames

# dump column names of the header and exit
if args.columns :

    for column in columns :
        print(column)

    sys.exit(0)

# process the groups, if applicable
universe, members, weight, drop, score = None, None, None, None, None
groups = []
if args.groups :

    universe, members, weight, drop, score = process_groups(args.groups)

    # gather groups we want to report (i.e., those which carry weight)
    for group in members :
        if weight[group] :
            groups.append(group)

    u = set([]) # for sanity check against universe
    for column in columns :
        u.add(column.strip())

    if not args.human :
        assert u == universe, universe ^ u

# w\o groups, no need to proceed..
else :
    sys.exit(0)

letter = None
if args.letter :
    letter = process_scheme(args.letter)

# process human-readable form of grades
if args.human :
    d = {}

    a, b = columns
    for row in rows :
        d[row[a] + ' Points Grade <Numeric MaxPoints:100>'] = row[b]

    rows = [d]

# now we process the rows
output = {}
for row in rows :

    last, user = 'last', 'user'
    a = []
    if not args.human :
        last = row['Last Name']
        user = row['Username'].lstrip('#')
        a = [last, row['First Name'], user]

    course = float(0)
    for group in members :
        if group == 'header' : # blow by the header
            continue

        grades = []
        for column in members[group] :
            grade = float(0)

            if args.human :
                assert column in row, '\n\nAssessement "{}" is missing!'.format(column.split('Points')[0].strip())

            g = row[column].strip()
            if g : # column is not "" (not submitted)
                grade = float(g) / score[column]

            grades.append(grade)

        grades = sorted(grades)[drop[group]:] # drop the n lowest..
        average = sum(grades) / len(grades)

        # weight average, and add it to final course grade
        row[group] = average * weight[group]
        course += row[group]

    # prepare remainder of the row of output
    percentage = round(100 * course + 0.0000001) # avoid round-downs
    if args.letter :
        a.append(letter_grade(letter, percentage))

    a.append(percentage)
    a.append('{:.6f}'.format(course))
    
    for group in groups :
        a.append('{:.6f}'.format(row[group]))

    output[last+user] = a # output indexed by lastname+username

sep = '\t' if args.tabs else ','

# prepare the header
header = []
if not args.human :
    header += ['Last', 'First', 'Username']

if args.letter :
    header.append('Letter')

header += ['Grade', 'Course']
header += ['{:s}({:.3f})'.format(g, weight[g]) for g in groups]

# dump human-readable output and exit
if args.human :

    for x,y in zip(header, a) :
        print(x, y, sep = sep)

    sys.exit(0)

# print header and output
print(*header, sep = sep)
for lastuser in sorted(output) :
    print(*output[lastuser], sep = sep)
