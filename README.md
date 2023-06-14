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

### "account" Dimension Table

  Dimensional table storing data related to the account that the transaction corresponds. Fields:
  
  - **account_id** (int) - Unique identifier and primary key.
  - **account_type** (str) - Specifies the type of account. Either checking, savings, or credit card.
  - **account_description** (str) - Provides details about the account.
 
 ### "transaction_type" Dimension Table
   Dimensional table storing data related to the transaction_type (such as credit card purchase, credit card payment, paycheck, account transfer, etc.). Fields:

   - **transaction_type_id** (int) - Unique identifier and primary key.
   - **account_type** (str) - Specifies the details related to each type of transaction stored.
   
   
  ### "category" Dimension Table

   Dimensional table storing the different categories that a purchase can correspond to. Fields:

   - **category_id** (int) - Unique identifier and primary key.
   - **category_description** (str) - Description of what the category is (such as "food & drink", "groceries", etc.).
   - **category_essential** (bool) - Boolean value specifying whether the purchases corresponding to this category are essiential goods or not.
    
    
   ### "date" Dimension Table
   
   Dimensional table storing data related to every calendar day. Fields:
    
   - **short_date** (date) - Date in the form of "yyyy-mm-dd". Also serves as the table's unique identifier and primary key.
   - **weekday_name** (str) - The day of the week ("Monay", "Tuesday", etc.)
   - **day_month** (int) - The day of the month ("1", "2"..., "30", "31")
   - **month_name** (str) - The name of the month ("January", "February", etc.)
   - **quarter** (int) - Quarter of the year as an integer ("1", "2", "3", "4")
   - **year** (int) - Year in the form of "yyyy"
   - **weekday_number** - An integer the corresponds to the index position of the week ("1" for Sunday, "2" for Monday, etc.)
   - **month_number** - Month of the year as an integer ("1" for January, "2" for February, etc.)
    
   ### "transaction_facts" Fact Table
    
   Fact table which stores one row for each transaction occurring within each account. Some transactions may have 2 rows associated with it, one for each account (such as a credit card bill payment having a  transaction correspond to the credit card and another corresponding to the bank account the payment is made from). Also a description of the payment and the amount of the transaction. Fields:
      
   - **transaction_id** (int) - Unique identifier and primary key
   - **account_id** (int) - Foreign key referencing "account_id" in the "account" dimension table used to establish _mandatory_ one-to-many relationship between "transaction_facts" and "account". 
   - **transaction_type_id** (int) - Foreign key referencing "transaction_type_id" in the "transaction_type" dimension table used to establish _mandatory_ one-to-many relationship between "transaction_facts" and "transaction_type".
   - **category_id** (int) - Foreign key referencing "category_id" in the "category" dimension table used to establish _optional_ one-to-many relationship between "transaction_facts" and "category". This relationship is optional because only _purchases_ have a category, other non-purchase related transaction will be _null_. This functionality is enforced via a check constraint, mentioned in the "database constraints" section.
   - **short_date** (date) - Date of the transaction in form of "yyyy-mm-dd". Also foreign key referencing "short_date" in the date dimension table used to establish _mandatory_ one-to-many relationship between "date" and "account".
   - **transaction_description** (str) - Description of the transaction. Typically autogenerated at the time of the transaction.
   - **transaction_amount** (decimal) - Amount of the transaction. If the transaction is a purchase or is lowering an account balance (such as a bank transfer to another account), the amount is negative. If the transaction results in the increase of a balance (such as receiving a transfer from another account) or is a credit card payment, the transaction is positive.

## Database Creation

The creation of the database creation was performed via the "forward engineer" feature of MySQL workbench. To view full creation script view [final_database_creation_script.sql](final_database_creation_script.sql).

## Loading Data into Dimensional Tables

## Transactions Data Cleaning

## Loading Data into Transactions_Facts Table

## Database Views Creation

## Power BI Dashboard

## Future Improvements
