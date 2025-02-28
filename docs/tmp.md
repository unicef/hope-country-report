# HCR Components



## Features


## Repository

<https://github.com/unicef/hope-country-report>


### Glossary

<report:Parametrizer/Argument>

Dataset : Dictionary used to create reports

System flagged are special arguments with related sync

Power Query
It's a read only query to be executed on database, it generate a dataset.

target: is the model from which the query starts from

parametrizer

active

daily refreshed

code:
result variable contains the result
extra variable contains extra context

Formatter
template to display or export reports

content type

code

Dataset
Dataset

has reference to query used

Report
Report connecting Query, Dataset, and Formatter

Document Report
is an instance obtained enumerating a Report for each Argument combination.

access is granted based on:

Business Area as per User Group -> PowerQuery Viewer

limited_access to field
