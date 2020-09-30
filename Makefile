# Makefile targets simplify daily operatons:

.DEFAULT_GOAL := all
.PHONY: all
test:	clean lint run

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.yaml" | xargs yamllint --strict
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 80 --check
	@echo "Completed lint"

.PHONY: run
run:
	@echo "Starting  test runs"
	python manage_probes.py -r
	python manage_probes.py
	python get_probes.py
	python collect_stats.py
	test -f outputs/result.json
	test -f outputs/result.csv
	@echo "Completed test runs"

.PHONY: clean
clean:
	@echo "Starting  clean"
	rm -rf outputs/
	rm -rf *.pyc
	rm -f nornir.log
	@echo "Completed clean"
