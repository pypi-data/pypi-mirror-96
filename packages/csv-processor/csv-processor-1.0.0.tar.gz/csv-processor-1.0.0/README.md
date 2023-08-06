# Python csv processor

The **csv-processor** is a python package that turns a csv into various formats.

It supports the following conversions:

- CSV - SQLite
- CSV - Json



# Installation
If not already [install pip](https://pip.pypa.io/en/stable/installing/)

Install the package with `pip` or `pip3`:

```bash
pip install csv-processor
```

# Usage
### Example:
```Python
from csvprocessor.csvtodb import Converter
csvfile = "path/to/your/file"
converter = Converter(csvfile)
converter.output() -> "db.db"
```