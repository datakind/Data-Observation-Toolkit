#!/bin/bash
echo $'#/bin/sh\nblack .\nfor f in `git diff --name-only | grep ".py"`; do python lint.py -p $f; done; pytest dot/self_tests/unit; pytest dot/self_tests/integration'> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
