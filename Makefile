################################################################################
#                                                                              #
#  Convenience Makefile for old fogies who can't imagine its lack.             #
#                                                                              #
################################################################################

VERSION := $(shell grep 'VERSION =' src/wp_enlighten/common.py | awk '{print $$3}' | tr -d '"')

help:
	@echo "To build and run Enlighten:"
	@echo
	@echo "  python -m venv venv"
	@echo "  . venv/*/activate"
	@echo "  pip install ."
	@echo "  python src/wp_enlighten/app.py"
	@echo
	@echo "Supported targets:"
	@echo
	@echo "  publish-test    - upload to pypi test repo"
	@echo "  publish         - upload to pypi prod repo"
	@echo
	@echo "  cloc            - count SLOC in Python, JSON and .ini files"
	@echo "  pylint          - code static analysis"
	@echo "  flake8          - code static analysis"
	@echo 
	@echo "VERSION = $(VERSION)"

cloc:
	@cloc --include-lang=Python,JSON,INI --exclude-dir=uic_qrc .

clean:
	@rm -rfv pyinstaller-build \
             innosetup-build \
             ENLIGHTEN-*.exe \
             docs/doxygen \
             enlighten.{err,out} \
             build.{err,out} \
             doxygen.{err,out}
	@find . -name __pycache__ -exec rm -rfv {} \;
	@find . -name \*.pyc -exec rm -fv {} \;

# run after "python -m build"
publish-test:
	python -m twine upload --repository testpypi dist/wp_enlighten*

# run after "python -m build"
publish:
	python -m twine upload dist/wp_enlighten*

pylint:
	@pylint src/wp_enlighten 

flake8:
	@find src/wp_enlighten -name \*.py | sort | grep -v uic_qrc | xargs flake8 | tee flake8.out 
	@echo && echo Counts:
	@awk -F": " '{print $$2}' < flake8.out | sort | uniq -c | sort -n
	@rm -f flake8.out
