#!/bin/bash
py.test2 -r fsxX --ignore=tmp --cov httoop --cov-report=html "$@"
