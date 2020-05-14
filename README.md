# Grading

Final grades were calculated by downloading the grades data from Blackboard in comma-separated values (CSV) format, and running the `calculate-grade.py` python script on it --- not unlike the course project of CS 131 (but in python).  The "Feedback to Learner" along with your Final Grade on Blackboard are the lines of this CSV file pertaining to your grades: see `input.csv` for an example of what this should look like

## Calculate your own grade

[![Run on Repl.it](https://repl.it/badge/github/murraypatterson/grading)](https://repl.it/github/murraypatterson/grading)

Running the `calculate-grade.py` python script on `input.csv` can be done in "repl.it" by clicking on the above `run on repl.it` badge: it will load a "repl" where you can click the "run" button to see the result.  To calculate your own grade, you can first replace `input.csv` with the contents of your "Feedback to Learner" from Blackboard: a simple copy of the text of your "Feedback to Learner" and paste within the `input.csv` file inside the repl (replacing the original contents of `input.csv`) is easiest.  After this is done, you can click the "run" button again: the output should match that of your "Grading Notes" along with your Final Grade on Blackboard

## Advanced usage

The precise command that is run when the "run" button is clicked is:

    python3 calculate-grade.py -g groups_131.txt -l fairfield_scheme.txt input.csv 

where `groups_131.txt` is the grading scheme of your particular course, and `fairfield_scheme.txt` is the correspondence between numerical and letter grades for your particular university (Fairfield U. in this case).  The behavior of the "run" button is dictated by what is in the `.replit` file.  This can be customized by changing the grading scheme, _e.g._, to `groups_354.txt`, _etc._
