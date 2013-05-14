#!/bin/sh

runtests() {
    if `which coverage > /dev/null 2> /dev/null`; then
        cd "$1"
        coverage run --source=djangoproject,../mongine djangoproject/manage.py test
        coverage report --omit 'djangoproject/*'
        coverage html --omit 'djangoproject/*'
    else
        cd "$1"
        python djangoproject/manage.py test
    fi
}

roottestdir="`pwd`/`dirname $0`"
(runtests "$roottestdir")

