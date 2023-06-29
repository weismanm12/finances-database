# Data Model for Personal Finance Dashboard
See the data model created based on the spend_save database below:

![image](https://github.com/weismanm12/finances_database/assets/112783326/60713785-53f8-4eba-aef6-36b95cf74296)

## Tables
Five of the seven tables in this data model are tables directly imported from the database. To view descriptions of the data contained in these tables, see the [spend_save data dictionary](https://github.com/weismanm12/finances_database/blob/main/database_creation/data_dictionary.md).
The only tables in this model that are not tables in the spend_save database are `spend_save daily category_balance` and `measures_table`, of which descriptions can be seen below.

### spend_save daily category_balance
This table was created from the SQL view "daily_category_balance". This view calculates the total spending per category on every day up to the last refresh. See the SQL code for the view creation and a sample output in the [Views Overview Jupyter Notebook](https://github.com/weismanm12/finances_database/blob/main/database_views/views_overview.ipynb) and/or see a description of the table below:
| Field       | Data Type | Description                                                                                                                                                                                  |
|-------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| category_id | int       | Unique identifier for each category. Used in combination with short_date to produce a category_id for every day up to the latest dashboard refresh.                                          |
| day_sum     | float     | Amount spent on a given date in a given category                                                                                                                                             |
| short_date  | date      | Date in the form of yyyy-mm-dd. Also a unique identifier for any given day. Used in combination with category_id to generate a category_id for every day up to the latest dashboard refresh. |

### measures_table
Table containing all custom measures used for calculations in the dashboard. See descriptions of each measure below along with the DAX code to create it:
| Measure              | Description                                                               | DAX Code                         |
|----------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| sum_spent            | Used to calculate total spent over a given time period                    | sum_spent = CALCULATE(ABS(SUM('spend_save transaction_facts'[transaction_amount])), 'spend_save transaction_type'[transaction_type_description] = "credit card purchase"|| 'spend_save transaction_type'[transaction_type_description] = "debit card purchase")    |
| cumulative_sum       | Calculates the running total spent by category at the day level           | cumulative_sum = CALCULATE(SUMX('spend_save daily_category_balance', 'spend_save daily_category_balance'[day_sum]), FILTER(ALL('spend_save daily_category_balance'[short_date]), 'spend_save daily_category_balance'[short_date] <= MAX('spend_save daily_category_balance'[short_date])))
| rank                 | Ranks categories in descending orderby the most spent in period           | rank = RANKX(ALL('spend_save category'[category_description]), [sum_spent], , DESC) |

Note: The measures_table also has the column "Column" which is a default column needed in order to create the measures_table. This column contains no data and is not used.

