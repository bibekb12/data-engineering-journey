explain
select
  *
from
  invoice;


  explain ANALYSE
select
  *
from
  invoice
where
  customer_id = 5;


EXPLAIN ANALYZE
SELECT
  *
FROM
  invoice
WHERE
  customer_id = 1;


EXPLAIN ANALYZE
SELECT
  *
FROM
  invoice
WHERE
  customer_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);



EXPLAIN ANALYZE
SELECT *
FROM invoice
WHERE invoice_id = 100;

EXPLAIN ANALYZE
SELECT *
FROM invoice
WHERE billing_country = 'USA';

CREATE INDEX invoice_billing_country_idx ON invoice (billing_country);

EXPLAIN ANALYZE
SELECT *
FROM invoice
WHERE invoice_id = 100;

EXPLAIN ANALYZE
SELECT *
FROM customer
WHERE email = 'leonie.kohler@google.com';


CREATE INDEX customer_email_idx ON customer(email);

SET enable_seqscan = on;



EXPLAIN ANALYZE
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    i.invoice_id,
    i.total
FROM customer c
JOIN invoice i
    ON i.customer_id = c.customer_id;


EXPLAIN ANALYZE
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    i.invoice_id,
    i.total
FROM customer c
JOIN invoice i
    ON i.customer_id = c.customer_id
WHERE c.customer_id = 5;


EXPLAIN ANALYZE
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(il.quantity * il.unit_price) AS total_spent
FROM customer c
JOIN invoice i
    ON i.customer_id = c.customer_id
JOIN invoice_line il
    ON il.invoice_id = i.invoice_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name;


EXPLAIN analyze
WITH invoice_totals AS (
SELECT
	c.customer_id ,
	c.last_name ,
	c.first_name ,
	sum(total) AS total_spent
FROM
	customer c
JOIN invoice i ON
	i.customer_id = c.customer_id 
GROUP BY c.customer_id , c.last_name , c.first_name 
)SELECT customer_id , last_name , first_name , total_spent  FROM invoice_totals
;


EXPLAIN ANALYZE 
WITH invoice_totals AS (
SELECT
	il.invoice_id ,
	sum(il.quantity * il.unit_price ) invoice_total
FROM
	invoice_line il
GROUP BY
	il.invoice_id 
)
SELECT
	it.invoice_id ,
	c.customer_id ,
	c.first_name ,
	c.last_name, 
	it.invoice_total
FROM
	invoice_totals it
JOIN invoice i ON
	i.invoice_id = it.invoice_id
JOIN customer c ON
	c.customer_id = i.customer_id ;



EXPLAIN ANALYZE 
WITH invoice_totals AS (
SELECT
	il.invoice_id ,
	sum(il.quantity * il.unit_price ) invoice_total
FROM
	invoice_line il
GROUP BY
	il.invoice_id 
)
SELECT
--	it.invoice_id ,
	c.customer_id ,
	c.first_name ,
	c.last_name, 
	SUM(it.invoice_total)
FROM
	invoice_totals it
JOIN invoice i ON
	i.invoice_id = it.invoice_id
JOIN customer c ON
	c.customer_id = i.customer_id 
GROUP BY c.customer_id, c.first_name, c.last_name ;


-- for each customer genere generated the most revenue

WITH customer_genere_revenue AS (
SELECT
	c.customer_id ,
	c.first_name ,
	c.last_name ,
	g.name,
	SUM(il.quantity * il.unit_price ) AS genre_revenue
FROM
	customer c
JOIN invoice i ON
	i.customer_id = c.customer_id
JOIN invoice_line il ON
	il.invoice_id = i.invoice_id
JOIN track t ON
	t.track_id = il.track_id
JOIN genre g ON
	g.genre_id = t.genre_id
GROUP BY
	c.customer_id,
	c.last_name ,
	c.first_name ,
	g.genre_id ,
	g.name
),
customer_genre_ranked AS (
SELECT
	customer_id ,
	first_name ,
	last_name ,
	name AS genre,
	genre_revenue ,
	ROW_NUMBER() OVER (PARTITION BY customer_id
ORDER BY
	genre_revenue DESC,
	name ASC) AS genre_rank
FROM
	customer_genere_revenue
),
customer_total AS (
SELECT
	i.customer_id ,
	sum(i.total) AS total_spending
FROM
	invoice i
GROUP BY
	i.customer_id
),
top_genre_precent AS (
SELECT
	customer_genre_ranked.customer_id ,
	first_name ,
	last_name ,
	genre ,
	genre_revenue ,
	total_spending ,
	(genre_revenue/total_spending ) AS top_genre_concentation,
	(100 *(genre_revenue / NULLIF(total_spending, 0))) AS top_genre_percentage
FROM
	customer_genre_ranked
JOIN customer_total ON
	customer_total.customer_id = customer_genre_ranked.customer_id
WHERE
	customer_genre_ranked.genre_rank = 1
ORDER BY
	top_genre_percentage DESC
)
SELECT
	first_name ,
	last_name ,
	genre ,
	top_genre_percentage ,
	AVG(top_genre_percentage) OVER () AS avg_genere_concentation,
	top_genre_percentage - AVG(top_genre_percentage) OVER () AS difference,
	RANK() OVER (
	ORDER BY top_genre_percentage DESC ) AS concentration_rank
FROM
	top_genre_precent 
	ORDER BY concentration_rank ASC , customer_id ASC 


