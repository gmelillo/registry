all:

test:
	@echo "testing all (with python3 in test/*.py..."; \
	for i in test/*.py; do \
	  COVERAGE_FILE=.coverage_$${i##*/} python3 -m coverage run $${i}; \
	done; \
	python3 -m coverage combine .coverage_*; \
	python3 -m coverage report *.py lib/*.py

checkdeps:
	@PYTHON="$${PYTHON-python3}"; export PYTHONPATH=test/test:lib; \
	if ! $${PYTHON} -c "import coverage" &> /dev/null; then \
		echo 'Unable to find coverage module on your python.'; \
		exit 1; \
	fi \

clean:
	@find . -type f -name '*.py[co]' -print0 | xargs -0 rm
	@find . -type d -name '__pycache__' -print0 | xargs -0 rm -r
	@find . -type f -name '.coverage' -print0 | xargs -0 rm 

.PHONY: test clean

