
.PHONY:  clean-pyc clean-build run

TEST_PATH=./


help:
	@echo "	clean-pyc"
	@echo "		Remove python artifacts"
	@echo "	clean-plots"
	@echo " 	Remove plots" 
	@echo "	clean-build"
	@echo "		Remove build artifacts"
	@echo "	run"
	@echo "		Run htm_univariate.py" 
clean-pyc: 
	find . -name '*.pyc' -exec rm --force {} + 

clean-plots:
	find ./plots -name '*.html' -exec rm --force {} +
	find ./plots -name '*.png' -exec rm --force {} + 

clean-build: 
	find ./config -name '*.py' -exec rm --force {} +
	find ../results/ -name '*.csv' -exec rm --force {} +

		
lint: 
	flake8 --exclude=.tox

test: 

run: 
	python htm_univariate.py 
