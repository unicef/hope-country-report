# Generate a report on information related to a list of households


1\. Navigate to [https://reporting-hope-dev.unitst.org/admin/](https://reporting-hope-dev.unitst.org/admin/)


2\. Click "Add"

![Image](../_screenshots/ascreenshot25.jpeg)


3\. Type "Information in a list of Households" in the "Name" field.


4\. Click the "Target" field and select "Household".

![Image](../_screenshots/ascreenshot26.jpeg)


5\.
```python
hh_list= [
    "HH-23-0271.6128",
    "HH-23-0271.6129",
    ".......",
    "HH-24-2546.2547"
]
result=list(conn.filter(unicef_id__in=hh_list).values("unicef_id", "program__name", "registration_data_import__name"))
```
Paste the list into the `hh_list` variable and filter the query for households in that list.

![Image](../_screenshots/ascreenshot27.jpeg)


6\. Click "Save and continue editing".

![Image](../_screenshots/ascreenshot28.jpeg)


7\. Click "Queue".

![Image](../_screenshots/ascreenshot29.jpeg)


8\. Click "DATASETS".

![Image](../_screenshots/ascreenshot31.jpeg)


9\. Click "[ABSTRACT] Information in a list of Households".

![Image](../_screenshots/ascreenshot32.jpeg)


10\. Click "PREVIEW" to view the data.

![Image](../_screenshots/ascreenshot34.jpeg)
