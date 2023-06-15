# Personal Finance Database and Dashboard
In this project, I developed a MySQL database tracking all of my financial transactions. This includes purchases, deposits, withdraws, credit card payments, and more. Any transaction that results in a change in a bank account or credit card balance is tracked in this database. These transactions are extracted from my banking website in the form of csv files, transformed using customized Python scripts, and loaded into the database via the sqlalchemy Python libray. I then created SQL views to understand my spending habits and developed a Power BI dashboard linked to the MySQL database to view these habits visually.

## Technologies/Skills
- SQL (MySQL), MySQL Workbench, Python (NumPy, Pandas, SQLAlchemy), Power BI, DAX
- Data modeling, database development, data wrangling, data cleaning, ETL, data visualization

## Inspiration
My inspiration for developing a financial database and dashboard stemmed from a desire to gain a deeper understanding of my spending habits. I was motivated by the idea of having a comprehensive tool that would allow me to track and analyze my expenses, giving me valuable insights into my financial patterns. I wanted to effortlessly visualize which categories I spent the most on and observe how my spending habits evolved over time. By creating this database and dashboard, I aimed to empower myself with knowledge and make informed decisions about my finances, ultimately working towards improving my financial well-being

---

## Identifying Requirements 
My primary objective was to create a system that could meticulously monitor every transaction flowing through my bank and credit card accounts. I aimed to capture crucial details such as transaction categories, transaction types (credit card purchases, paychecks, credit card bill payments, etc.), and transaction dates. It was imperative for me to have a comprehensive view of all my financial activities, enabling me to gain a profound understanding of my monetary flow and make informed decisions based on this valuable information.

## Data Modeling
To achieve the desired requirements above, I opted to create a dimensional model consisting of 4 dimension tables and one fact table as seen below:

![model](https://github.com/weismanm12/finances_database/assets/112783326/17b3b7b0-5991-43c4-b3b9-6b17a87325e7)

#### "account" Dimension Table

| Field                | Data Type | Description                               |
|----------------------|-----------|-------------------------------------------|
| account_id           | int       | Unique identifier and primary key         |
| account_type         | str       | Type of account - checking, savings, or credit card |
| account_description  | str       | Details about the account                 |

#### "transaction_type" Dimension Table

| Field                | Data Type | Description                               |
|----------------------|-----------|-------------------------------------------|
| transaction_type_id  | int       | Unique identifier and primary key        |
| account_type         | str       | Details related to each type of transaction |

#### "category" Dimension Table

| Field                | Data Type | Description                               |
|----------------------|-----------|-------------------------------------------|
| category_id          | int       | Unique identifier and primary key.        |
| category_description | str       | Description of the category (e.g., "food & drink", "groceries") |
| category_essential   | bool      | Boolean value indicating if the purchases in this category are essential goods |

#### "date" Dimension Table

| Field                | Data Type | Description                               |
|----------------------|-----------|-------------------------------------------|
| short_date           | date      | Date in the form of "yyyy-mm-dd"; serves as the table's unique identifier and primary key. |
| weekday_name         | str       | The name day of the week (e.g., "Monday") |
| day_month            | int       | The day of the month ("1", "15", etc.) |
| month_name           | str       | The name of the month (e.g., "January") |
| quarter              | int       | Quarter of the year as an integer (e.g. "1") |
| year                 | int       | Year in the form of "yyyy"                 |
| weekday_number       | int       | An integer that corresponds to the index position of day ofthe week ("1" for Sunday, "2" for Monday, etc.) |
| month_number         | int       | Month of the year as an integer (e.g., "1" for January) |

#### "transaction_facts" Fact Table

| Field                  | Data Type | Description                               |
|------------------------|-----------|-------------------------------------------|
| transaction_id         | int       | Unique identifier and primary key         |
| account_id             | int       | Foreign key referencing "account_id" in the "account" dimension table (mandatory one-to-many relationship) |
| transaction_type_id    | int       | Foreign key referencing "transaction_type_id" in the "transaction_type" dimension table (mandatory one-to-many relationship) |
| category_id            | int       | Foreign key referencing "category_id" in the "category" dimension table (optional one-to-many relationship; only purchases marked with a category; null for non-purchase transactions) |
| short_date             | date      | Date of the transaction in "yyyy-mm-dd" format; foreign key referencing "short_date" in the "date" dimension table (mandatory one-to-many relationship) |
| transaction_description| str       | Description of the transaction (autogenerated at the time of the transaction) |
| transaction_amount     | str       | Amount of the transaction (negative for purchases and bank account balance reduction, positive for bank balance increase and credit card bill payments) |

_Note: The "transaction_facts" Fact Table includes a check constraint to enforce the relationship between transactions and categories. This constraint ensures that only purchase transactions have a category, while other non-purchase transactions have a null value for the category_id field._
## Database Creation

The creation of the database creation was performed via the "forward engineer" feature of MySQL Workbench. Additionally, the check constraint mentioned above was added. To view full creation script view [final_database_creation_script.sql](final_database_creation_script.sql).

## Loading Data into Dimensional Tables

## Transactions Data Cleaning

## Loading Data into Transactions_Facts Table

## Database Views Creation

## Power BI Dashboard

## Future Improvements
