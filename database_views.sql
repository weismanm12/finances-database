-- No update needed
CREATE VIEW account_balances AS
SELECT
	tf.account_id,
    account_type,
    account_description,
    SUM(transaction_amount) AS balance
FROM transaction_facts AS tf
JOIN account USING (account_id)
GROUP BY account_id, account_type;

-- Updated to match 'category' changes
CREATE VIEW running_amount_spent AS
SELECT 
	tf.short_date,
    t.transaction_type_description,
    c.category_description,
    tf.transaction_description,
    d.year,
    ABS(tf.transaction_amount) AS transaction_total,
	SUM(ABS(tf.transaction_amount)) OVER(PARTITION BY d.year ORDER BY short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_yearly_spend
FROM transaction_facts AS tf
JOIN transaction_type AS t USING (transaction_type_id)
JOIN category AS c USING (category_id)
JOIN date AS d USING (short_date)
WHERE year != '2022'
ORDER BY short_date;

-- Updated to reflect 'category' changes
CREATE VIEW monthly_spend_summary AS
SELECT
	d.month_number,
	d.month_name AS month,
    d.year,
	SUM(ABS(tf.transaction_amount)) AS month_amount_spend,
    ROUND((SUM(ABS(tf.transaction_amount)) - LAG(SUM(ABS(tf.transaction_amount))) OVER(ORDER BY d.year, d.month_number))
		/ NULLIF(LAG(SUM(ABS(tf.transaction_amount))) OVER(ORDER BY d.year, d.month_number), 0), 2) AS prior_month_increase,
    SUM(SUM(ABS(tf.transaction_amount))) OVER(PARTITION BY year ORDER BY d.year, d.month_number ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS yearly_running_total
FROM transaction_facts AS tf
JOIN transaction_type AS t USING (transaction_type_id)
JOIN category AS c USING (category_id)
JOIN date AS d USING (short_date)
WHERE d.year != '2022'
GROUP BY month, d.month_number, d.year
ORDER BY d.year, d.month_number;

-- Updated to match 'category' changes
CREATE VIEW month_spend_category AS
SELECT
    d.year,
    d.month_number,
    d.month_name,
    c.category_description,
    SUM(ABS(tf.transaction_amount)) AS monthly_spend,
    RANK() OVER(PARTITION BY month_number, month_name, year ORDER BY ABS(SUM(tf.transaction_amount)) DESC) AS month_ranking
FROM transaction_facts AS tf
JOIN category AS c USING (category_id)
JOIN account AS a USING (account_id)
JOIN transaction_type AS t USING (transaction_type_id)
JOIN date AS d USING (short_date)
WHERE d.year != '2022'
GROUP BY month_number, month_name, year, category_description
ORDER BY year, month_number, month_ranking;

-- Updated to match changes in 'category' table
ALTER VIEW daily_spend_sum AS
SELECT d.short_date, SUM(COALESCE(SUM(ABS(tf.transaction_amount)), 0)) OVER(ORDER BY d.short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum
FROM date AS d
LEFT JOIN transaction_facts AS tf
	ON d.short_date = tf.short_date
LEFT JOIN transaction_type AS t
	ON tf.transaction_type_id = t.transaction_type_id
WHERE EXTRACT(year FROM d.short_date) != '2022'
	AND d.short_date <= CURDATE()
	AND (t.transaction_type_id IN (1, 2) OR t.transaction_type_id IS NULL)
GROUP BY d.short_date
ORDER BY short_date;

-- Updated to match changes in 'category' table
CREATE VIEW daily_spend_sum_w_transactions AS
SELECT 
	d.short_date,
    t.transaction_type_description,
    c.category_description,
    tf.transaction_description,
    COALESCE(ABS(tf.transaction_amount), 0) AS transaction_total,
    d.year,
	SUM(ABS(tf.transaction_amount)) OVER(PARTITION BY d.year ORDER BY short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_yearly_spend
FROM date AS d
LEFT JOIN transaction_facts AS tf
	ON d.short_date = tf.short_date
LEFT JOIN transaction_type AS t USING (transaction_type_id)
LEFT JOIN category AS c USING (category_id)
WHERE d.short_date <= CURDATE()
	AND (t.transaction_type_id IN (1, 2) OR t.transaction_type_id IS NULL)
	AND year != '2022'
ORDER BY short_date;

-- Updated to match changes in 'category' table
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
WHERE EXTRACT(year FROM d.short_date) != '2022'
	AND d.short_date <= CURDATE()
ORDER BY short_date, category_id
)

SELECT 
	dc.short_date,
    dc.category_id,
    SUM(COALESCE(SUM(ABS(tf.transaction_amount)), 0)) OVER(PARTITION BY dc.category_id ORDER BY dc.short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum
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
ORDER BY dc.short_date, dc.category_id
