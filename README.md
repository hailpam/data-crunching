# Overview
Collection of scripts to play with data.

## ```orders-exporter.py```
Exports orders from the JSON format to CSV.

It requires an API key in input:

```
$> python orders-exporter.py
usage: orders-exporter.py [-h] -k KEY
orders-exporter.py: error: the following arguments are required: -k/--key
```

To access the documentation:
```
$> python orders-exporter.py -h
usage: orders-exporter.py [-h] -k KEY

Exports JSON orders data into CSV format.

optional arguments:
  -h, --help         show this help message and exit
  -k KEY, --key KEY  API key to be used to perform the REST request to the backend
```

To run it succssfully:
```
$> python orders-exporter.py -k <specific_api_key>
info: loaded orders...
[...]
info: export successul
```