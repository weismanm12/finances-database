
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
    
    # Reset the index of the DataFrame and unecessary columns
    #savings_df = savings_df.reset_index(drop=True)
    # savings_df = savings_df.drop(['details', 'type', 'balance', 'Check or Slip #'], axis=1)
    
    # Convert all string values to lowercase in the DataFrame
    savings_df = savings_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    savings_df.columns = [column.lower() for column in savings_df.columns]
    
    # Insert needed columns. 
    # Add account_id # "3" to reference "savings account" as the account and initialize other columns with "0" value to be updated later
    savings_df.insert(1, 'account_id', 3)
    savings_df.insert(2, 'transaction_type_id', 0)
    savings_df.insert(3, 'category_id', 0)
    
    # Rename columns in the DataFrame to match database
    savings_df = savings_df.rename(columns={'posting date': 'short_date', 'description': 'transaction_description', 
                                            'amount': 'transaction_amount'})
    
    # Convert short_date to datetime format
    savings_df['short_date'] = pd.to_datetime(savings_df['short_date'])
    
    # Next step is to set transaction_type_id and category_id (or null category) based on transaction description and amount (positive/negative)
    # Only PURCHASES are to be given a category, the rest are set to NaN
    
    # Identify interest revenue and set transaction_type_id (no category assigned since this is not a purchase)
    savings_df.loc[savings_df['transaction_description'].str.contains('interest'), 
                   ['transaction_type_id', 'category_id']] = [9, np.nan]
    
    # Identify transfers FROM savings and set transaction_type_id (no category)
    savings_df.loc[(savings_df['transaction_description'].str.contains('transfer')) & (savings_df['transaction_amount'] < 0), 
               ['transaction_type_id', 'category_id']] = [5, np.nan]
    
    # Identify transfers TO savings and set transaction_type_id (no category)
    savings_df.loc[(savings_df['transaction_description'].str.contains('transfer')) & (savings_df['transaction_amount'] > 0), 
               ['transaction_type_id', 'category_id']] = [6, np.nan]
    
    # Identify deposits and set transaction_type_id (no category)
    savings_df.loc[(savings_df['transaction_description'].str.contains('deposit')) & (savings_df['transaction_amount'] > 0), 
               ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Identify withdraws and set transaction_type_id (no category)
    savings_df.loc[(savings_df['transaction_description'].str.contains('withdraw')) & (savings_df['transaction_amount'] < 0), 
               ['transaction_type_id', 'category_id']] = [4, np.nan]
    
    # Set any remaining non-assigned POSITIVE value transaction_type_ids as deposit (no category)
    savings_df.loc[(savings_df['transaction_type_id'] == 0) & (savings_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Set any non-assigned NEGATIVE value transaction_type_ids as withdraw (no category)
    savings_df.loc[(savings_df['transaction_type_id'] == 0) & (savings_df['transaction_amount'] < 0), 
                   ['transaction_type_id', 'category_id']] = [4, np.nan]
    
    # Truncate transaction_description to match database constraints
    savings_df['transaction_description'] = savings_df['transaction_description'].str.slice(0,100)
    
    # Select transactions that have not been assigned a transaction_type_id and category_id for manual review 
    # Add these transactions to review_df and drop from savings_df
    mask = ((savings_df['transaction_type_id'] == 0) & (savings_df['category_id'] == 0))
    review_df = savings_df[mask].reset_index(drop=True)
    savings_df = savings_df[~mask].reset_index(drop=True)

    # Print transactions that need to be manually processed
    print("Transactions successfully transformed."
          "The following transactions need to be reviewed."
          "Once values have been assigned to transaction_type_id and category_id (or a null category_id), use to_spend_save() to update database.")
    print(review_df)
    
    # Return cleaned data and data to be manually processed as two DataFrames
    return savings_df, review_df
    
    
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
    
    # Read the csv file into a DataFrame
    checking_df = pd.read_csv(csv_file, index_col=None)
    
    # Convert all string values to lowercase in the DataFrame
    checking_df = checking_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    # Convert all column titles to lowercase and drop unnecessary columns
    checking_df.columns = [column.lower() for column in checking_df.columns]
    checking_df = checking_df.drop(['details', 'type', 'balance', 'check or slip #'], axis=1)
    
    # Update column titles to match MySQL database.
    checking_df = checking_df.rename(columns={'posting date': 'short_date', 'description': 'transaction_description', 
                                              'amount': 'transaction_amount'})
    
    # Convert short_date to a datetime format
    checking_df['short_date'] = pd.to_datetime(checking_df['short_date'])

    # Insert columns needed to be loaded into MySQL database
    # Add account_id "2" for "checking account" value and initialize other columns with "0" value to be updated later.
    checking_df.insert(1, 'account_id', 2)
    checking_df.insert(2, 'transaction_type_id', 0)
    checking_df.insert(3, 'category_id', 0)

    # Next step is to set transaction_type_id and category_id (or null category) based on transaction description and amount (positive/negative)
    # Only PURCHASES are to be given a category, the rest are set to NaN
    
    # Identify transfers to savings and set transaction_type_id (no category assigned since this is not a purchase)
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] > 0),
                    ['transaction_type_id', 'category_id']] = [6, np.nan]
    
    # Identify transfers from savings and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('deposit')) & (checking_df['transaction_amount'] > 0),
                    ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Identify interest received and set transaction_type_id (no category)
    checking_df.loc[checking_df['transaction_description'].str.contains('interest'),
                    ['transaction_type_id', 'category_id']] = [9, np.nan]
    
    # Identify paychecks from employers and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('gusto|exel')) & (checking_df['transaction_amount'] > 0), 
                    ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Identify credit card bill payments and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('pay')) &
                    (checking_df['transaction_description'].str.contains('chase')) &
                    (checking_df['transaction_amount'] < 0),
                    ['transaction_type_id', 'category_id']] = [8, np.nan]
    
    # Identify transfers from checking to savings and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] < 0), 
                   ['transaction_type_id', 'category_id']] = [5, np.nan]
    
    # Identify transfers from savings to checking and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('transfer')) & (checking_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [6, np.nan]
    
    # Identify miscellaneous withdraws from checking account and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('atm')) & (checking_df['transaction_description'].str.contains('chase'))
                    & (checking_df['transaction_amount'] < 0), ['transaction_type_id', 'category_id']] = [4, np.nan]
    
    # Identify miscellaneous deposits to checking account and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('atm')) &
                    (checking_df['transaction_description'].str.contains('chase')) &
                    (checking_df['transaction_amount'] > 0),
                    ['transaction_type_id', 'category_id']] = [3, np.nan]

    # Identify reimbursements through employer certify reimbursement system and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('certify')) & (checking_df['transaction_amount'] > 0), 
                   ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Identify insurance payments and set transaction_type_id/category_id
    checking_df.loc[(checking_df['transaction_description'].str.contains('allstate')) & (checking_df['transaction_amount'] < 0), 
                   ['transaction_type_id', 'category_id']] = [2, 1]
    
    #Identifies Venmo "cashout"/deposit and set transaction_type_id (no category)
    checking_df.loc[(checking_df['transaction_description'].str.contains('venmo')) & (checking_df['transaction_amount'] > 0), 
                    ['transaction_type_id', 'category_id']] = [3, np.nan]
    
    # Identify Venmo payments. These need to be reviewed to determine category of transaction
    # Add these transactions to review_df and drop from checking_df
    mask = ((checking_df['transaction_description'].str.contains('venmo')) & (checking_df['transaction_amount'] < 0))
    venmo_review_df = checking_df[mask].reset_index(drop=True)
    checking_df = checking_df[~mask].reset_index(drop=True)

    # Select transactions that have not been assigned a transaction_type_id and category_id for manual review
    # Add these transactions to review_df and drop from checking_df
    mask = ((checking_df['transaction_type_id'] == 0) & (checking_df['category_id'] == 0))
    review_df = checking_df[mask].reset_index(drop=True)
    checking_df = checking_df[~mask].reset_index(drop=True)
    
    # Append venmo_review_df to review_df
    review_df = pd.concat([review_df, venmo_review])
    review_df = review_df.reset_index(drop=True)
    
    # Truncate transaction_description at 100 characters to meet requirements of spend_save database
    checking_df["transaction_description"] = checking_df["transaction_description"].str.slice(0, 100)
    review_df_df["transaction_description"] = review_df["transaction_description"].str.slice(0, 100)
    
    # Print transactions that need to be manually processed
    print("Transactions successfully transformed."
          "The following transactions need to be reviewed."
          "Once values have been assigned to transaction_type_id and category_id (or a null category_id), use to_spend_save() to update database.")
    print(review_df)
    
    # Return cleaned data and data to be manually processed as two DataFrames
    return checking_df, review_df


def cc_file_cleanup(spend_save_password, csv_file):
    
    """
    Cleans up a credit card CSV file, performs data transformations, and returns the cleaned dataframes.

    Args:
        spend_save_password (str): Password to spend_save server. Needed to retrieve current categories and category_ids.
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
    
    # Bank automatically marks credit card purchases with a category. These categories need to be assigned to the corresponding category_id to match database schema.
    # The spend_save database will be queried to extract all category_ids and category_descriptions from the category table.
    # This will be saved as a DataFrame and joined to the the DataFrame generated from the checking transactions csv.
    # This will allow us to get all the category_id's for each transaction.

    # Connect to database engine
    engine = create_engine('mysql+pymysql://root:' + password + '@localhost/spend_save')

    # SQL query to extract category_id and category_description from spend_save database
    query = ("""
        SELECT *
        FROM category
        ORDER BY category_id
    """)

    # Run query passed as an argument
    result = engine.execute(query)

    # Fetch all rows from the result of query
    rows = result.fetchall()

    # Get the column names from the result of query 
    column_names = result.keys()

    # Create a DataFrame from the result of the query to store category_id and category_description as "category_df"
    category_df = pd.DataFrame(rows, columns=column_names)

    # Close the result and the connection
    result.close()
    engine.dispose()
    
    # Load credit card transactions from csv AS "cc_df" and drop empty rows that may be present at bottom of csv
    cc_df = pd.read_csv(csv_file, header=0, index_col=None)
    cc_df.dropna(how='all', inplace=True)

    # Casefold all letters in dataset/column titles drop irrelevant columns, and convert date column to datetime
    cc_df = cc_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    cc_df.columns = [column.lower() for column in cc_df.columns]
    
    # Drop columns that are not needed
    cc_df = cc_df.drop(['post date', 'memo'], axis=1)
    
    # merge category_df and cc_df on category/category_description to get category_id for each transaction in cc_df
    cc_df = pd.merge(cc_df, category_df[['category_id', 'category_description']],
                     left_on='category', right_on='category_description',
                     how='left').drop('category_description', axis=1)
    
    # Fill null values with 0 to be processed again below and convert category_id to integer data type
    cc_df['category_id'] = cc_df['category_id'].fillna(0).astype('Int64')
    
     # Convert "transaction date" to datetime data type
    cc_df['transaction date'] = pd.to_datetime(cc_df['transaction date'])
    
    # Reorder columns and drop category column since we now have category_id
    column_names = cc_df.columns.tolist()
    column_names = [column_names[-1]] + column_names[:-1]
    cc_df = cc_df[column_names]
    cc_df = cc_df.drop('category', axis=1)

    # Insert account_id and transaction_type_id columns. Assign "1" to all account_id's since they are all credit card.
    # Assign "0" to all transaction_type_id's to be updated below.
    cc_df.insert(0, 'account_id', 1)
    cc_df.insert(1, 'transaction_type_id', 0)

    # Identify credit card purchases and set transaction_type_id (category_id was assigned when merging DataFrames avove)
    cc_df.loc[cc_df['type'] == 'sale', 'transaction_type_id'] = 1

    # Identify credit card bill payments (no category)
    cc_df.loc[cc_df['type'] == 'payment', ['transaction_type_id', 'category_id']] = [7, np.nan]

    # Identify fees and adjustments set transaction_type_id (no category)
    cc_df.loc[cc_df['type'].str.contains('fee|adjustment'),
                ['transaction_type_id', 'category_id']] = [11, np.nan]

    # Drop "type" column since it is no longer needed
    cc_df = cc_df.drop('type', axis=1)

    # Rename columns to match spend_save database
    column_titles = ['transaction_id', 'account_id', 'transaction_type_id', 'category_id', 'short_date', 'transaction_description', 'transaction_amount']
    cc_df.columns = column_titles
    
    # Truncate transaction_description at 100 characters
    cc_df["transaction_description"] = cc_df["transaction_description"].str.slice(0, 100)

    # Create cc_review_df to manually review any transactions that were not assigned a category_id (or is null) 
    # or transaction_type_id
    mask = (cc_df['category_id'].isin([0])) | (cc_df['transaction_type_id'].isin([0]))
    cc_review_df = cc_df[mask].reset_index(drop=True)
    cc_df = cc_df[~mask].reset_index(drop=True)
    
    # Print transactions that need to be manually processed
    print("Transactions successfully transformed."
      "The following transactions need to be reviewed."
      "Once values have been assigned to transaction_type_id and category_id, use to_spend_save() to update database.")
    print(cc_review_df)
    
    # Return cleaned data and data to be manually processed as two DataFrames
    return cc_df, cc_review_df
