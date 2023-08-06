# somenergia-utils

This module includes different Python modules and scripts
ubiquiously used on scripts in SomEnergia cooperative
but with no entity by themselves to have their own repository.


- `venv`: run a command under a Python virtual enviroment
- `sql2csv.py`: script to run parametrized sql queries and get the result as (tab separated) csv.
- `dbutils.py`: module with db related functions
	- `fetchNs`: a generator that wraps db cursors to fetch objects with attributes instead of psycopg arrays
	- `nsList`: uses the former to build a list of such object (slower but maybe convinient)
	- `csvTable`: turns the results of a query into a tab separated table with proper header names
- `sheetfetcher.py`: convenience class to retrieve data from gdrive spreadshets
- `trace`: quickly enable and disable tracing function calling by decorating them with `@trace`
- `testutils`: module with common test utilities
	- `testutils.assertNsEqual`: structure equality assertion using sorted key yaml dumps
	- `testutils.destructiveTest`: decorator to avoid running destructive tests in production

## `venv` script

This script is useful to run Python scripts under a given virtual environment.
It is specially useful to run Python scripts from crontab lines.

```bash
usage: venv /PATH/TO/PYTHON/VIRTUALENV COMMAND [PARAM1 [PARAM2...]]
```

## `sql2csv.py` script

Runs an SQL file and outputs the result of the query as tabulator separated csv.a

You can provide query parameters either as yamlfile or as commandline options.

```bash
 sql2csv.py <sqlfile> [<yamlfile>] [--<var1> <value1> [--<var2> <value2> ..] ]
```

## `dbutils` Python module

Convenient cursor wrappers to make the database access code more readable.

Example:

```python
import psycopg2, dbutils
db = psycopg2.connect(**dbconfiguration)
with db.cursor() as cursor :
	cursor.execute("SELECT name, age FROM people")
	for person as dbutils.fetchNs(cursor):
		if person.age < 21: continue
		print("{name} is {age} years old".format(person))
```

## `sheetfetcher` Python module

Convenient wraper for gdrive.

```python
from sheetfetcher import SheetFetcher

fetcher = SheetFetcher(
	documentName='My Document',
	credentialFilename='drive-certificate.json',
	)
table = fetcher.get_range("My Sheet", "A2:F12")
fulltable = fetcher.get_fullsheet("My Sheet")
```

- Document selectors can be either an uri or the title
- Sheet selectors can be either an index, a name or an id.
- Range selectors can be either a named range, index tuple or a "A2:F5" coordinates.
- You should [Create a certificate and grant it access to the document](http://gspread.readthedocs.org/en/latest/oauth2.html)

## trace

This decorator is a fast helper to trace calls to functions and methods.
It will show the name of the functions the values of the parameters and the returned values.

```python
from trace import trace

@trace
def factorial(n):
    if n<1: return 1
    return n*factorial(n-1)

factorial(6)

('> factorial', (6,))
('> factorial', (5,))
('> factorial', (4,))
('> factorial', (3,))
('> factorial', (2,))
('> factorial', (1,))
('> factorial', (0,))
('< factorial', (0,), '->', 1)
('< factorial', (1,), '->', 1)
('< factorial', (2,), '->', 2)
('< factorial', (3,), '->', 6)
('< factorial', (4,), '->', 24)
('< factorial', (5,), '->', 120)
('< factorial', (6,), '->', 720)

```

## `testutils.assertNsEqual`

Allows to assert equality on json/yaml like structures combining
dicts, lists, numbers, strings, dates...
The comparision is done on the YAML output so that differences are
spoted as text diffs.
Also keys in dicts are alphabetically sorted.


## `testutils.destructiveTest`

An utility to avoid running destrutive tests in production.
It is a decorator that checks wheter the erp configured in `dbconfig`
has the testing flag and skips the test if it doesn't.

The script `enable_destructive_test.py` is also provided to set/unset
that testing flag which is not defined by default.

## `isodates`

Module for simplified isodate parsing and timezone handling.


## `sequence`

Interprets strings like the ones the standard Print Dialog
uses to specify pages to be printed.
ie. "2,4,6-9,13" means "2, 4, from 6 to 9 and 13"





