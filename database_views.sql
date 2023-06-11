CREATE VIEW account_balances AS
SELECT
	tf.account_id,
    account_type,
    account_description,
    SUM(transaction_amount) AS balance
FROM transaction_facts AS tf
JOIN account USING (account_id)
GROUP BY account_id, account_type;

CREATE VIEW running_amount_spent AS 
SELECT 
	tf.short_date,
    t.transaction_type_description,
    c.category_description,
    tf.transaction_description,
    ABS(tf.transaction_amount) AS transaction_total,
    d.year,
	SUM(ABS(tf.transaction_amount)) OVER(PARTITION BY d.year ORDER BY short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_yearly_spend
FROM transaction_facts AS tf
JOIN transaction_type AS t USING (transaction_type_id)
JOIN category AS c USING (category_id)
JOIN date AS d USING (short_date)
WHERE t.transaction_type_description IN ('credit card purchase', 'debit card purchase', 'withdraw')
	AND year != '2022'
ORDER BY short_date;

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
WHERE t.transaction_type_description IN ('credit card purchase', 'debit card purchase', 'withdraw')
	AND d.year != '2022'
GROUP BY month, d.month_number, d.year
ORDER BY d.year, d.month_number;

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
WHERE t.transaction_type_description IN ('credit card purchase', 'debit card purchase', 'withdraw')
	AND d.year != '2022'
GROUP BY month_number, month_name, year, category_description
ORDER BY year, month_number, month_ranking;

CREATE VIEW daily_spend_sum AS
SELECT d.short_date, SUM(COALESCE(SUM(ABS(tf.transaction_amount)), 0)) OVER(ORDER BY d.short_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum
FROM date AS d
LEFT JOIN transaction_facts AS tf
	ON d.short_date = tf.short_date
LEFT JOIN transaction_type AS t
	ON tf.transaction_type_id = t.transaction_type_id
WHERE EXTRACT(year FROM d.short_date) != '2022'
	AND d.short_date <= CURDATE()
	AND (t.transaction_type_description IN ('credit card purchase', 'debit card purchase', 'withdraw') OR t.transaction_type_description IS NULL)
GROUP BY d.short_date
ORDER BY short_date;

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
	AND (t.transaction_type_description IN ('credit card purchase', 'debit card purchase', 'withdraw') OR t.transaction_type_description IS NULL)
	AND year != '2022'
ORDER BY short_date;