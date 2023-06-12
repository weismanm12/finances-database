def savings_file_cleanup(csv_file):
    """
    Cleans and prepares a CSV file from savings account on Chase website for loading into transaction_facts table.

    Args:
        csv_file (str): The path to the CSV file containing the savings data.

    Returns:
        tuple: A tuple containing two DataFrames:
            - savings_df: The cleaned and transformed savings account transactions Dataframe.
            - review_df: The DataFrame containing transactions that need manual review for assignment of
              transaction_type_id and category_id.
    """
    
    import numpy as np
    import pandas as pd
    
    # Read the CSV file into a DataFrame
    savings_df = pd.read_csv(csv_file, index_col=None)
    
    # Reset the index of the DataFrame and remove the 'Check or Slip #' column from the DataFrame
    #savings_df = savings_df.reset_index(drop=True)
    # savings_df = savings_df.drop(['details', 'type', 'balance', 'Check or Slip #'], axis=1)
    
    # Convert all string values to lowercase in the DataFrame
    savings_df = savings_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    savings_df.columns = [column.lower() for column in savings_df.columns]
    
    # Insert needed columns. 
    # Add account_id # "3" for "savings account" value and initialize other columns with "0" value to be updated later.
    savings_df.insert(1, 'account_id', 3)
    savings_df.insert(2, 'transaction_type_id', 0)
    savings_df.insert(3, 'category_id', 0)
    
    # Remove unnecessary columns from the DataFrame
    savings_df = savings_df.drop(['details', 'type', 'balance', 'check or slip #'], axis=1)
    
    # Rename columns in the DataFrame
    savings_df = savings_df.rename(columns={'posting date': 'short_date', 'description': 'transaction_description', 
                                            'amount': 'transaction_amount'})
    
    # Convert "shore_date" to datetime format
    savings_df['short_date'] = pd.to_datetime(savings_df['short_date'])
    
    # Update transaction_type_id and category_id based on transaction description and amount (positive/negative)
    
    # Identify interest revenue
    savings_df.loc[savings_df['transaction_description'].str.contains('interest'), ['transaction_type_id', 'category_id']] = [9, 19]
    
    # Identify transfers FROM savings
    savings_df.loc[(savings_df['transaction_description'].str.contains('transfer')) & (savings_df['transaction_amount'] < 0), 
               ['transaction_type_id', 'category_id']] = [5, 18]
    
    # Identify transfers TO savings
    savings_df.loc[(savings_df['transaction_description'].str.contains('transfer')) & (savings_df['transaction_amount'] > 0), 
               ['transaction_type_id', 'category_id']] = [6, 18]
    
    # Identify deposits
    savings_df.loc[(savings_df['transaction_description'].str.contains('deposit')) & (savings_df['transaction_amount'] > 0), 
               'transaction_type_id'] = 3
    
    # Identify withdraws
    savings_df.loc[(savings_df['transaction_description'].str.contains('withdraw')) & (savings_df['transaction_amount'] < 0), 
               'transaction_type_id'] = 4
    
    # Set any non-assigned POSITIVE value transaction_type_id's as deposit
    savings_df.loc[(savings_df['transaction_type_id'] == 0) & (savings_df['transaction_amount'] > 0), 'transaction_type_id'] = 3
    
    # Set any non-assigned NEGATIVE value transaction_type_id's as deposit
    savings_df.loc[(savings_df['transaction_type_id'] == 0) & (savings_df['transaction_amount'] < 0), 'transaction_type_id'] = 4
    
    # Set any non-assigned POSITIVE value category_id's as "miscellaneous deposit"
    savings_df.loc[(savings_df['category_id'] == 0) & (savings_df['transaction_amount'] > 0), 'category_id'] = 25
    
     # Set any non-assigned POSITIVE value category_id's as "miscellaneous withdraw"
    savings_df.loc[(savings_df['category_id'] == 0) & (savings_df['transaction_amount'] < 0), 'category_id'] = 24
    
    # Truncate transaction_description to match database constraints
    savings_df['transaction_description'] = savings_df['transaction_description'].str.slice(0,100)
    
     # Select transactions that have not been assigned a transaction_type_id and category_id for manual review. 
    # Add these transactions to review_df and drop from checking_df
    mask = ((savings_df['transaction_type_id'] == 0) & (savings['category_id'] == 0))
    review_df = savings_df[mask].reset_index(drop=True)
    savings_df = savings_df[~mask].reset_index(drop=True)

    # Manually update these transactions
    print("Transactions successfully transformed."
          "The following transactions need to be reviewed."
          "Once values have been assigned to transaction_type_id and category_id, use to_spend_save() to update database.")
    print(review_df)
    
    # Return cleaned data as a DataFrame
    return savings_df, review_df


def to_spend_save(df, data_source, password, database_name="spend_save", table="transaction_facts"):
    """
    Loads a DataFrame into a MySQL database and saves it as a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to be loaded.
        data_source (str): The source of the data.
        password (str): The password to the MySQL database server.
        database_name (str, optional): The name of the MySQL database. Defaults to "spend_save".
        table (str, optional): The name of the table in the MySQL database. Defaults to "transaction_facts".
        
    Returns:
        None
    """

    import numpy as np
    import pandas as pd
    from sqlalchemy import create_engine
    from datetime import date
    
    # Create the connection string for the MySQL database
    database = 'mysql+pymysql://root:' + password' @localhost/' + database_name
    
    # Create engine
    engine = create_engine(database)

    # Connect to MySQL database using engine
    conn = engine.connect()

    # Import data from Pandas DataFrame to MySQL database
    df.to_sql(table, con=conn, if_exists='append', index=False)

    # Commit the transaction
    conn.execute('commit')

    # Close connection
    conn.close()
    
    # Generate the file name to save as CSV using data_source and current_date()
    current_date = date.today()
    file_name = f"{data_source}_{current_date}.csv"
    
    # Save the DataFrame as a CSV file
    df.to_csv(file_name)
    print("savings data successfully loaded into spend_save MySQL database")
    print(f"csv file saved as {data_source}_{current_date}.csv")
    
    
def checking_file_cleanup(csv_file):
    """
    Performs data cleaning and transformation on a checking account DataFrame loaded from a CSV file.
    
    Args:
        csv_file (str): Path to the CSV file containing the checking account data.
        
    Returns:
        tuple: A tuple containing two DataFrames:
            - checking_df: The cleaned and transformed checking account transactions Dataframe.
            - review_df: The DataFrame containing transactions that need manual review for assignment of
              transaction_type_id and category_id.
    """
    
    import numpy as np
    import pandas as pd
    
    # Load dataset
    checking_df = pd.read_csv(csv_file, index_col=None)
    
    # Convert all string values to lowercase in the DataFrame
    checking_df = checking_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    # Convert all column titles to lowercase
    checking_df.columns = [column.lower() for column in checking_df.columns]
    checking_df = checking_df.drop(['details', 'type', 'balance', 'check or slip #'], axis=1)
    
    # Update column titles to match MySQL database.
    checking_df = checking_df.rename(columns={'posting date': 'short_date', 'description': 'transaction_description', 
                                              'amount': 'transaction_amount'})
    
    # Convert "short_date" to a datetime format
    checking_df['short_date'] = pd.to_datetime(checking_df['short_date'])

    # Insert needed columns. 
    # Add account_id # "2" for "checking account" value and initialize other columns with "0" value to be updated later.
    checking_df.insert(1, 'account_id', 2)
    checking_df.insert(2, 'transaction_type_id', 0)
    checking_df.insert(3, 'category_id', 0)

    # Identifies transfers to savings and updates transation_type_id and category_id as such
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [6, 18]
    
    # Identifies transfers from savings and updates transation_type_id and category_id as such
    checking_df.loc[(checking_df['transaction_description'].str.contains('deposit')) & (checking_df['transaction_amount'] > 0), 
                   'transaction_type_id'] = 3
    
    # Identifies interest received
    checking_df.loc[checking_df['transaction_description'].str.contains('interest'), ['transaction_type_id', 'category_id']] = [9, 19]
    
    # Identifies paychecks from employers
    checking_df.loc[(checking_df['transaction_description'].str.contains('gusto|exel')) & (checking_df['transaction_amount'] > 0), 
                    ['transaction_type_id', 'category_id']] = [3, 21]
    
    # Identifies credit card payments
    checking_df.loc[(checking_df['transaction_description'].str.contains('pay')) & 
                    (checking_df['transaction_description'].str.contains('chase'))
                    & (checking_df['transaction_amount'] < 0), ['transaction_type_id', 'category_id']] = [8, 23]
    
    # Identifies transfers from checking to savings
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] < 0), 
                   ['transaction_type_id', 'category_id']] = [5, 18]
    
    # Identifies transfers from savings to checking
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [6, 18]
    
    # Identifies miscellaneous withdraws from checking account
    checking_df.loc[(checking_df['transaction_description'].str.contains('atm')) & (checking_df['transaction_description'].str.contains('chase'))
                    & (checking_df['transaction_amount'] < 0), ['transaction_type_id', 'category_id']] = [4, 24]
    
    # Identifies miscellaneous deposits to checking account
    checking_df.loc[(checking_df['transaction_description'].str.contains('atm')) &
                    (checking_df['transaction_description'].str.contains('chase')) &
                    (checking_df['transaction_amount'] > 0),
                    ['transaction_type_id', 'category_id']] = [3, 25]

    # Identifies reimbursements through certify
    checking_df.loc[(checking_df['transaction_description'].str.contains('certify')) & (checking_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [3, 25]
    
    # Identifies insurance payments
    checking_df.loc[(checking_df['transaction_description'].str.contains('allstate')) & (checking_df['transaction_amount'] < 0), 
                   ['transaction_type_id', 'category_id']] = [2, 1]
    
    #Identifies venmo "cashout"
    checking_df.loc[(checking_df['transaction_description'].str.contains('venmo')) & (checking_df['transaction_amount'] > 0), 
                    ['transaction_type_id', 'category_id']] = [3, 22]
    
    # Identifies venmo payments. These need to be reviewed.
    mask = ((checking_df['transaction_description'].str.contains('venmo')) & (checking_df['transaction_amount'] < 0))
    venmo_review = checking_df[mask].reset_index(drop=True)
    checking_df = checking_df[~mask].reset_index(drop=True)

    # Select transactions that have not been assigned a transaction_type_id and category_id for manual review. 
    # Add these transactions to review_df and drop from checking_df
    mask = ((checking_df['transaction_type_id'] == 0) & (checking_df['category_id'] == 0))
    review_df = checking_df[mask].reset_index(drop=True)
    checking_df = checking_df[~mask].reset_index(drop=True)
    
    # Append venmo_review
    review_df = pd.concat([review_df, venmo_review])
    review_df = review_df.reset_index(drop=True)
    
    # Truncate transaction_description at 100 characters
    checking_df["transaction_description"] = checking_df["transaction_description"].str.slice(0, 100)
    review_df["transaction_description"] = review_df["transaction_description"].str.slice(0, 100)
    
    # Manually update these transactions
    review_df = review_df.reset_index(drop=True)
    print("Transactions successfully transformed."
          "The following transactions need to be reviewed."
          "Once values have been assigned to transaction_type_id and category_id, use to_spend_save() to update database.")
    print(review_df)
    
    return checking_df, review_df


def query_spend_save(query, password, database_name='spend_save'):

    """
    Executes a SQL query on the spend_save database and returns the result as a pandas DataFrame.
    
    Args:
        query (str): The SQL query to be executed.
        password (str): The password to the MySQL database server.
        database_name (str): The name of the database. Default is 'spend_save'.

    Returns:
        pandas.DataFrame: A DataFrame containing the result of the query.
    """
    
    import numpy as np
    import pandas as pd
    from sqlalchemy import create_engine
    
    # Connect to database engine
    engine = create_engine('mysql+pymysql://root:' + password + '@localhost/' + database_name)
    
    # Run query
    result = engine.execute(query)
    
    # Fetch all rows from the result
    rows = result.fetchall()

    # Get the column names from the result set
    column_names = result.keys()

    # Create a DataFrame from the rows and column names
    df = pd.DataFrame(rows, columns=column_names)

    # Close the result and the connection
    result.close()
    engine.dispose()
    
    return df


def cc_file_cleanup(csv_file):
    
    """
    Cleans up a credit card CSV file, performs data transformations, and returns the cleaned dataframes.

    Args:
        csv_file (str): The path to the credit card CSV file.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - cc_df: The cleaned and transformed credit card transactions DataFrame.
            - cc_review_df: The DataFrame containing transactions that need manual review for assignment of
              transaction_type_id and category_id.
    """
    
    import numpy as np
    import pandas as pd
    from sqlalchemy import create_engine
    from financial_database_functions import query_spend_save
    
    
    # Generate dataframe from categories table in SQL database to determine category_id of cc transactions
    query = ("""
        SELECT *
        FROM category
        ORDER BY category_id
        """)

    category_df = query_spend_save(query)
    
    # Load dataset
    cc_df = pd.read_csv(csv_file, header=0, index_col=None)
    cc_df.dropna(how='all', inplace=True)

    # Casefold all letters in dataset/column titles, drop irrelevant columns, and convert date column to datetime
    cc_df = cc_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    cc_df.columns = [column.lower() for column in cc_df.columns]
    cc_df = cc_df.drop(['post date', 'memo'], axis=1)
    cc_df['transaction date'] = pd.to_datetime(cc_df['transaction date'])
    
    # merge category_df and cc_df to match get category_id for each transaction in cc_df
    cc_df = pd.merge(cc_df, category_df[['category_id', 'category_description']],
                     left_on='category', right_on='category_description',
                     how='left').drop('category_description', axis=1)
    cc_df['category_id'] = cc_df['category_id'].fillna(0)
    cc_df['category_id'] = cc_df['category_id'].astype(int)

    # Reorder columns and drop category column since we now have category_id
    column_names = cc_df.columns.tolist()
    column_names = [column_names[-1]] + column_names[:-1]
    cc_df = cc_df[column_names]
    cc_df = cc_df.drop('category', axis=1)

    # Insert account_id and transaction_type_id columns. Assign "1" to all account_id's since they are all credit card.
    # Assign "0" to all transaction_type_id's to be updated below.
    cc_df.insert(0, 'account_id', 1)
    cc_df.insert(1, 'transaction_type_id', 0)

    # Identify credit card purchases
    cc_df.loc[cc_df['type'] == 'sale', 'transaction_type_id'] = 1

    # Identify credit card payments
    cc_df.loc[cc_df['type'] == 'payment', ['transaction_type_id', 'category_id']] = [7, 23]

    # Identify fees and adjustments
    cc_df.loc[cc_df['type'].str.contains('fee|adjustment'), ['transaction_type_id', 'category_id']] = [11, 5]

    # Drop "type" column since it is no longer needed
    cc_df = cc_df.drop('type', axis=1)

    # Extract the proper columns from MySQL database and rename dataframe columns
    table_facts = query_spend_save("""
        SHOW columns
        FROM transaction_facts
        """)
    column_titles = table_facts['Field'].tolist()[1:]
    cc_df.columns = column_titles
    
    # Truncate transaction_description at 100 characters
    cc_df["transaction_description"] = cc_df["transaction_description"].str.slice(0, 100)

    # Create cc_review_df to manually review any transactions that were not assigned an id or contains NaN values
    mask = (cc_df['category_id'].isin([0])) | (cc_df['transaction_type_id'].isin([0])) | (cc_df.isna().any(axis=1))
    cc_review_df = cc_df[mask].reset_index(drop=True)
    cc_df = cc_df[~mask].reset_index(drop=True)
    
    # Return cc_df and cc_review_df to be inserted into MySQL database
    print("Transactions successfully transformed."
      "The following transactions need to be reviewed."
      "Once values have been assigned to transaction_type_id and category_id, use to_spend_save() to update database.")
    print(cc_review_df)
    
    return cc_df, cc_review_df
