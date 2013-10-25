#!/bin/bash

# verify user provided a name for the virtualenv
if [ -z "$1" ]; then
    echo "usage: $0 virtual_env_name"
    exit
fi
VIRTUALENV_NAME=$1

virtualenv $VIRTUALENV_NAME
. $VIRTUALENV_NAME/bin/activate

find . -name "*.pyc" -delete

rm -rf jenkins_reports
mkdir jenkins_reports

pip install -r requirements/ci.txt

python manage.py test --with-xunit --with-xcover --cover-package=djcopybook
TEST_EXIT=$?

flake8 djcopybook --max-line-length=120 --max-complexity=5 | awk -F\: '{printf "%s:%s: [E]%s%s\n", $1, $2, $3, $4}' > jenkins_reports/flake8.txt
FLAKE8_EXIT=`cat jenkins_reports/flake8.txt | wc -l`

let JENKINS_EXIT="$TEST_EXIT +  $FLAKE8_EXIT"
if [ $JENKINS_EXIT -gt 0 ]; then
    echo "Test exit status:" $TEST_EXIT
    echo "FLAKE8 exit status:" $FLAKE8_EXIT
    echo "Exiting Build with status:" $JENKINS_EXIT
    exit $JENKINS_EXIT
fi
