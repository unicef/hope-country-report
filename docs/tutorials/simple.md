# Creating reports



1\. Navigate to [https://reporting-hope-dev.unitst.org/admin/](https://reporting-hope-dev.unitst.org/admin/)


2\. Scroll down and click "Queries"

![Image](../_screenshots/ascreenshot9.jpeg)


3\. Click "ADD QUERY"

![Image](../_screenshots/ascreenshot1.jpeg)


4\. Click here.

![Image](../_screenshots/ascreenshot.jpeg)


5\. Right-click "Afghanistan"

![Image](../_screenshots/ascreenshot2.jpeg)


6\. Click the "Name:" field.

![Image](../_screenshots/ascreenshot3.jpeg)


7\. Type the name of the query e.g "Afghan query for all households"


8\. Click the "**Target**" drop-down menu. It designate which table you are going to be using to query the database. For our case we will use the **Household** table.

![Image](../_screenshots/ascreenshot4.jpeg)


Alert: The list of tables available in the Hope project can be viewed on this [link](https://github.com/unicef/hope-country-report/blob/develop/src/hope_country_report/apps/hope/models/%5C_inspect.py). The link between different tables and how to retrieve information from one table to another is part of the [Django documentation](https://www.djangoproject.com/).

![Image](../_screenshots/Pasted_image1.png)


9\. Start typing the code for the query. Remember, here **conn** represent ***conn=Household.objects***. Please refer to [Django](https://www.djangoproject.com/).

![Image](../_screenshots/ascreenshot5.jpeg)


10\. 
```python
result = list(conn.filter(withdrawn=False, first_registration_date__year__gte=2024).values("unicef_id", "admin1__name"))
```

Here we will query the list of households which are not withdrawn and were registered in 2024 or above. We will only retrieve their **unicef_id** and **Admin1** area name. The query must return data that we must assign to the **result** environment variable.


11\. We then save and continue editing

![Image](../_screenshots/ascreenshot6.jpeg)


12\. Click "Queue" to launch the retrieval of the data.

![Image](../_screenshots/ascreenshot7.jpeg)


13\. If you want to preview the result, click "DATASETS" button.

![Image](../_screenshots/ascreenshot8.jpeg)


14\. Click  on the query "\[ABSTRACT\] Afghan query for all households"

![Image](../_screenshots/ascreenshot10.jpeg)


15\. And preview "PREVIEW". You should see that your report is OK.

![Image](../_screenshots/ascreenshot11.jpeg)


16\. Click  on the navigation link "Power Query" so that we can produce the actual report in its format.

![Image](../_screenshots/ascreenshot12.jpeg)


17\. Click "Add" on the Report Configuration

![Image](../_screenshots/ascreenshot13.jpeg)


18\. Click this drop-down and chose which country office the report will bellong to.

![Image](../_screenshots/ascreenshot14.jpeg)


19\. Fill in the "Report Title:" field. "Repport on Afghan households in 2024"

![Image](../_screenshots/ascreenshot15.jpeg)


20\. Click here.

![Image](../_screenshots/ascreenshot16.jpeg)


21\. Search for the query you previously created by typing "afgh".


22\. Click "[ABSTRACT] Afghan query for all households"

![Image](../_screenshots/ascreenshot17.jpeg)


23\. Add "Queryset To HTML" if you want to see the report as an html page and file.

![Image](../_screenshots/ascreenshot18.jpeg)


24\. Add "Dataset to XLSX" if you want to see the report as an Excel file.

![Image](../_screenshots/ascreenshot19.jpeg)


25\. Click "Choose" and move them on the other side.

![Image](../_screenshots/ascreenshot10.jpeg)


26\. Save and continue editing.

![Image](../_screenshots/ascreenshot21.jpeg)


27\. Click "Queue" to generate the actual reports.

![Image](../_screenshots/ascreenshot22.jpeg)


28\. Click "VIEW ON SITE" in order to view the resulting reports.

![Image](../_screenshots/ascreenshot23.jpeg)


29\. Click "view"

![Image](../_screenshots/ascreenshot24.jpeg)
