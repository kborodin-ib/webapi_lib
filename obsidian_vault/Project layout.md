
/root
	/source
	/tests
	/samples

<h2> Module vs Package </h2>
	A module is a single .py file
	A package is a directory that contains multiple .py files

<h2> How __init__ and __main__ work </h2>
	- When you import a package it runs the `__init__.py` file inside directory
	- When you execute the package it executes the `__main__.py`

<h2> Managing import paths </h2>
- import sys; sys.path - list of all directories that will be searched for imports
- PYTHONPATH environmental var - contains directories that will be searched for modules.
**Package needs to be either in sys.path or PYTHONPATH**

