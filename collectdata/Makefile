
.PHONY:  clean-pyc clean-buildi run

TEST_PATH=./


help:
	@echo "	clean-pyc"
	@echo "		Remove python artifacts"
	@echo "	clean-build"
	@echo "		Remove build artifacts"
	@echo "	test"
	@echo "		Testing with"
	@echo "	run"
	@echo "		Run htm_cpu.py" 
clean-pyc: 
	find . -name '*.pyc' -exec rm --force {} + 


clean-build: 
	find ../data/procfs/ -name '*.csv' -exec rm --force {} +


test: 

run: 
	python htm_univariate.py 
