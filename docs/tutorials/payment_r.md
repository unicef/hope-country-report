# Generate Payment Plans Report from a template

1\. Navigate to [https://reporting-hope-dev.unitst.org/admin/](https://reporting-hope-dev.unitst.org/admin/)


2\. Add a query

![Image](../_screenshots/ascreenshot55.jpeg)


3\. In the **Parent** field, you have to choose the report template that you want to use. It must use Parameters so that you can substitute new ones. The target and code fields _must be empty_, but the "Country" and "Parent" fields must be set.

![Image](../_screenshots/ascreenshot56.jpeg)


4\. Delete anything in the code field  `result=conn.all()`

![Image](../_screenshots/ascreenshot57.jpeg)


5\. Click the "Parametrizer" dropdown.

![Image](../_screenshots/ascreenshot58.jpeg)


6\. You can choose any parameter or create one by clicking on the "+" sign.

![Image](../_screenshots/ascreenshot59.jpeg)


7\. Choose a name and a country.

![Image](../_screenshots/ascreenshot60.jpeg)


8\. Fill the "Value" field with the correct JSON information:

```json
{"payment_plan": ["PP-4140-24-00000056", "PP-4140-24-00000055", "PP-4140-24-00000049", "PP-4140-24-00000046"], "business_area": ["syria"]}
```

![Image](../_screenshots/ascreenshot61.jpeg)


9\. Save the parameters

![Image](../_screenshots/ascreenshot62.jpeg)


10\. Click this button.

![Image](../_screenshots/ascreenshot63.jpeg)


11\. Click "Info on Payment plans (Payment plan list report)"

![Image](../_screenshots/ascreenshot64.jpeg)


12\. Click "Queue"

![Image](../_screenshots/ascreenshot65.jpeg)


13\. Go back and we create the report configurations

![Image](../_screenshots/ascreenshot66.jpeg)


14\. Select the country

![Image](../_screenshots/ascreenshot67.jpeg)


15\. Click "Info on Payment plans (Payment plan list report)" as the query

![Image](../_screenshots/ascreenshot68.jpeg)


16\. Choose for the report to be available as an Excel and HTML file.

![Image](../_screenshots/ascreenshot69.jpeg)


17\. You can choose to limit access to or notify "[dzzzdzzzz@unicef.org](mailto:dzzzzzzzz@unicef.org)".

![Image](../_screenshots/ascreenshot70.jpeg)


18\. Click the "Compress" field if you want the report to be available as a compressed file.

![Image](../_screenshots/ascreenshot71.jpeg)


19\. Save and continue editing, and  queue the report.

![Image](../_screenshots/ascreenshot72.jpeg)


20\. Click "VIEW ON SITE" to view the result

![Image](../_screenshots/ascreenshot73.jpeg)


21\. Click "view"

![Image](../_screenshots/ascreenshot74.jpeg)


22\. Click "Report For Payment Plans In Syriapp-4140-24-00000056_Syria"

![Image](../_screenshots/ascreenshot75.jpeg)
