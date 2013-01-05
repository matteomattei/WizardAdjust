from distutils.core import setup
import py2exe

setup(
    windows = [
		{
		"script": 'wizardadjust.py',
		}
	],
    options = {
        "py2exe" : {
			"optimize": 2,
        }
    },
)
