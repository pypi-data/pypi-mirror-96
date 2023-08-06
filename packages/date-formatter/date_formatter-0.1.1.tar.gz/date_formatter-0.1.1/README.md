# date_time_format

a Python package that formats a ten character string to a date

# Installation

```bash
pip install date_formatter
```

# Usage

## Minimal example

```python
from date_formatter import *

date_time_string_US = "12-18-2014"
date_time_string_AUS = "18-12-2014"

myDates_US = DateFormatter.dateFormat(date_time_string_US, False, True, "US")
myDates_AUS = DateFormatter.dateFormat(date_time_string_AUS, True, False)

print(myDates_US)
print(myDates_AUS)

```

## returns:

- 18-Dec-14
- 18 December 2014

## Parameters

- **date_time_string: str**
  The date string you want to format
- **USE_FULL_MONTH_NAME : bool**
  Whether to display the full name of the month. If this is set to `True`, shows "January"; if this is set to `False`, shows "Jan".
- **USE_HYPHEN_AS_SPACER : bool**
  Whether to show interval between characters as single space, or hyphen. If this is set to `True`, shows "18-Jan-14"; if this set to `False`, shows "18 Jan 14"
- **REGION_FORMAT : str, optional**
  Which region's date format to use. If set to "US" assumes string is "MM-DD-YYYY"; if this is set to something or is missing, assumes string is "DD-MM-YYYY"
