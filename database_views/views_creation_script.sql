-- Shows total spent per month, increase from prior month, and the running total for the year the month is in
CREATE VIEW monthly_spend_summary AS
WITH cte AS (											-- CTE to perform initial aggregation
	SELECT
		d.month_number,
		d.month_name AS month,
		d.year,
		SUM(ABS(tf.transaction_amount)) AS month_amount_spent				-- Take absolute value since transaction_amount is negative for purchases
	FROM transaction_facts AS tf
	JOIN transaction_type AS t 
		USING (transaction_type_id)
	JOIN category AS c 
		USING (category_id)
	JOIN date AS d 
		USING (short_date)
	WHERE d.year != '2022'			-- Not interested in 2022
	GROUP BY month, d.month_number, d.year
	ORDER BY d.year, d.month_number
)
SELECT
	*,
    	ROUND((month_amount_spent - LAG(month_amount_spent) OVER (ORDER BY year, month_number))				-- Calculate dollar increase from prior month
		/ LAG(month_amount_spent) OVER (ORDER BY year, month_number), 2) AS prior_month_change,			-- Convert to decimal value of last month
	SUM(month_amount_spent)												-- Calculate yearly running total spent
		OVER (
			PARTITION BY year
			ORDER BY year, month_number
        ) AS yearly_running_total
FROM cte;
--------------------------------------------------------------------------------------------------------------------------------------------------------
-- Shows and ranks amount spent per category per month
CREATE VIEW monthly_spend_category AS
SELECT
	d.year,
    	d.month_number,
    	d.month_name,
    	c.category_description,
    	SUM(ABS(tf.transaction_amount)) AS monthly_spend,								-- Take absolute value since transaction_amount is negative for purchases
    	RANK() 
		OVER(
			PARTITION BY month_number, month_name, year 
            		ORDER BY ABS(SUM(tf.transaction_amount)) DESC
		) AS month_ranking
FROM transaction_facts AS tf
JOIN category AS c 
	USING (category_id)
JOIN account AS a 
	USING (account_id)
JOIN transaction_type AS t 
	USING (transaction_type_id)
JOIN date AS d 
	USING (short_date)
WHERE d.year != '2022'
GROUP BY month_number, month_name, year, category_description
ORDER BY year, month_number, month_ranking;
--------------------------------------------------------------------------------------------------------------------------------------------------------
-- Shows all transactions and the yearly running total spent
CREATE VIEW daily_spend AS
SELECT
	tf.transaction_id,
	d.short_date,
	t.transaction_type_description,
    	c.category_description,
    	tf.transaction_description,
    	COALESCE(ABS(tf.transaction_amount), 0) AS transaction_total,		-- Take absolute value since transaction_amount is negative for purchases. Assign 0 for days with no purchases.
    	d.year,
	SUM(ABS(tf.transaction_amount)) 					-- Sum total spent by year up to the current date
		OVER(
			PARTITION BY d.year 
			ORDER BY short_date, transaction_id
		) AS running_yearly_spend
FROM date AS d									-- Select from date column to keep all dates, not just ones with purchases
LEFT JOIN transaction_facts AS tf						-- Use left join to keep dates mentioned above
	ON d.short_date = tf.short_date
        AND tf.transaction_type_id IN (1, 2)
LEFT JOIN transaction_type AS t 
	USING (transaction_type_id)
LEFT JOIN category AS c 
	USING (category_id)
WHERE d.short_date <= CURDATE()
-- 	AND (t.transaction_type_id IN (1, 2) OR t.transaction_type_id IS NULL)						-- Since a left join was used, we must filter out transactions that
	AND year != '2022'				-- Not interested in 2022					-- are not purchases, while keeping days without purchases 
ORDER BY short_date;
--------------------------------------------------------------------------------------------------------------------------------------------------------
-- View created to run visual on Power BI dashboard. Calculates running total spent for each category (daily level of granularity) 
CREATE VIEW daily_category_balance AS
WITH date_category AS (
	SELECT 
		d.short_date,
		c.category_id
	FROM date AS d
	CROSS JOIN (
		SELECT category_id
		FROM category
	) AS c
	WHERE d.year != '2022'
		AND d.short_date <= CURDATE()
	ORDER BY short_date, category_id
)
SELECT 
	dc.short_date,
	dc.category_id,
	COALESCE(SUM(ABS(tf.transaction_amount)), 0) AS day_sum,		-- Categorical spending each day. Zero if none on a given day day
FROM date_category AS dc
LEFT JOIN transaction_facts AS tf
	ON dc.short_date = tf.short_date
    AND dc.category_id = tf.category_id
LEFT JOIN transaction_type AS t
	ON tf.transaction_type_id = t.transaction_type_id
WHERE EXTRACT(year FROM dc.short_date) != '2022'
	AND dc.short_date <= CURDATE()
	AND (t.transaction_type_id IN (1, 2) OR t.transaction_type_id IS NULL)
GROUP BY dc.short_date, dc.category_id
ORDER BY dc.short_date, dc.category_id;
--------------------------------------------------------------------------------------------------------------------------------------------------------
-- Calculates balances of all accounts at the end of each month
CREATE VIEW monthly_account_balances AS
SELECT
	CONCAT(year, '-' , LPAD(month_number, 2, '0')) AS end_date_period,					-- Combine month and year to get date period
	tf.account_id,
    account_type,
    SUM(SUM(transaction_amount)) 										-- Running total represents account balances
		OVER(
			PARTITION BY tf.account_id 
            ORDER BY CONCAT(year, '-' , LPAD(month_number, 2, '0'))
		) AS balance
FROM transaction_facts AS tf
JOIN account 
	USING (account_id)
JOIN date 
	USING (short_date)
GROUP BY end_date_period, account_id, account_type
ORDER BY end_date_period;
