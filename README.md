# Grading

Final grades were calculated by downloading the grades data from
iCollege in comma-separated values (CSV) format --- see `input.csv`
for an example of what the grades data should look like --- and
running the `calculate-grade.py` python script on it

## Calculate your own grade

[![Run on Repl.it](https://repl.it/badge/github/murraypatterson/grading)](https://repl.it/github/murraypatterson/grading)

Running the `calculate-grade.py` python script on `input.csv` can be
done in "repl.it" by clicking on the above `run on repl.it` badge: it
will load a "repl" where you can click the "run" button to see the
result.  To calculate your own grade, you can first replace
`input.csv` with the contents of your grades from iCollege.  After
this is done, you can click the "run" button again: the output should
match that of your "Final Adjusted Grade" on iCollege

## Advanced usage

The precise command that is run when the "run" button is clicked is:

    python3 calculate-grade.py -g groups_4330.txt input.csv 

where `groups_4330.txt` is the grading scheme of your particular
course.  The behavior of the "run" button is dictated by what is in
the `.replit` file.
