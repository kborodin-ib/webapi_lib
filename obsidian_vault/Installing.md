Most of python packages reside in /site-packages directory.

In order for the package to be initialized by interpreter it is required to add `__init__.py` files to the root of the directory.

Running `pip show ibapi` or any other know library will reveal the full path to `site-packages` dir 

Than soft link needs to be created. If located in the root of the project can be done like so:

`sudo ln -s (pwd) /home/thdmn/.local/site-package`

Now package can be imported systemwide

TODO:

Automate this process