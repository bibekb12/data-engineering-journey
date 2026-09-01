-- Phase 02 SQL Analysis
-- Dataset: Chinook / PostgreSQL

-- #10 Top 10 customers by spending
-- Grain: one row per customer

WITH customer_spending AS (
SELECT
customer_id,
SUM(total) AS total_spending
FROM invoice
GROUP BY customer_id
)
SELECT
c.customer_id,
c.first_name,
c.last_name,
cs.total_spending
FROM customer_spending cs
JOIN customer c
ON c.customer_id = cs.customer_id
ORDER BY
cs.total_spending DESC,
c.first_name ASC,
c.last_name ASC,
c.customer_id ASC
LIMIT 10;

-- #11 Top 5 genres by revenue
-- Grain: one row per genre

WITH genre_revenue AS (
SELECT
g.genre_id,
g.name AS genre,
SUM(il.quantity * il.unit_price) AS revenue
FROM genre g
JOIN track t
ON t.genre_id = g.genre_id
JOIN invoice_line il
ON il.track_id = t.track_id
GROUP BY
g.genre_id,
g.name
)
SELECT
genre_id,
genre,
revenue
FROM genre_revenue
ORDER BY
revenue DESC,
genre ASC,
genre_id ASC
LIMIT 5;

-- #12 Top 10 artists by revenue
-- Grain: one row per artist

WITH artist_revenue AS (
SELECT
a.artist_id,
a.name AS artist,
SUM(il.quantity * il.unit_price) AS revenue
FROM artist a
JOIN album al
ON al.artist_id = a.artist_id
JOIN track t
ON t.album_id = al.album_id
JOIN invoice_line il
ON il.track_id = t.track_id
GROUP BY
a.artist_id,
a.name
)
SELECT
artist_id,
artist,
revenue
FROM artist_revenue
ORDER BY
revenue DESC,
artist ASC,
artist_id ASC
LIMIT 10;

-- #14 Customers spending above average
-- Average is calculated across customer totals,
-- not across individual invoices.
-- Grain: one row per customer

WITH customer_spending AS (
SELECT
customer_id,
SUM(total) AS total_spending
FROM invoice
GROUP BY customer_id
),
average_customer_spending AS (
SELECT
AVG(total_spending) AS average_spending
FROM customer_spending
)
SELECT
c.customer_id,
c.first_name,
c.last_name,
cs.total_spending
FROM customer_spending cs
JOIN customer c
ON c.customer_id = cs.customer_id
CROSS JOIN average_customer_spending acs
WHERE cs.total_spending > acs.average_spending
ORDER BY
cs.total_spending DESC,
c.customer_id ASC;

-- #15 Customers who never bought Jazz
-- NOT EXISTS expresses the anti-join requirement directly.

SELECT
c.customer_id,
c.first_name,
c.last_name
FROM customer c
WHERE NOT EXISTS (
SELECT 1
FROM invoice i
JOIN invoice_line il
ON il.invoice_id = i.invoice_id
JOIN track t
ON t.track_id = il.track_id
JOIN genre g
ON g.genre_id = t.genre_id
WHERE g.name = 'Jazz'
AND i.customer_id = c.customer_id
)
ORDER BY
c.customer_id ASC;

-- Advanced Analysis
-- Customer top genre and genre concentration

-- Business question:
-- For each customer, what is their highest-revenue genre,
-- what percentage of their spending does it represent,
-- and how concentrated is that customer compared with others?

WITH customer_genre_revenue AS (
-- Grain: one row per customer + genre
SELECT
c.customer_id,
c.first_name,
c.last_name,
g.genre_id,
g.name AS genre,
SUM(il.quantity * il.unit_price) AS genre_revenue
FROM customer c
JOIN invoice i
ON i.customer_id = c.customer_id
JOIN invoice_line il
ON il.invoice_id = i.invoice_id
JOIN track t
ON t.track_id = il.track_id
JOIN genre g
ON g.genre_id = t.genre_id
GROUP BY
c.customer_id,
c.first_name,
c.last_name,
g.genre_id,
g.name
),
customer_genre_ranked AS (
-- Rank genres within each customer.
-- Genre name provides a deterministic tie-breaker.
SELECT
customer_id,
first_name,
last_name,
genre_id,
genre,
genre_revenue,
ROW_NUMBER() OVER (
PARTITION BY customer_id
ORDER BY
genre_revenue DESC,
genre ASC,
genre_id ASC
) AS genre_rank
FROM customer_genre_revenue
),
customer_total AS (
-- Grain: one row per customer
SELECT
customer_id,
SUM(total) AS total_spending
FROM invoice
GROUP BY customer_id
),
top_customer_genre AS (
-- Reduce to one row per customer.
SELECT
cgr.customer_id,
cgr.first_name,
cgr.last_name,
cgr.genre,
cgr.genre_revenue,
ct.total_spending,
100.0 * cgr.genre_revenue
/ NULLIF(ct.total_spending, 0) AS top_genre_percentage
FROM customer_genre_ranked cgr
JOIN customer_total ct
ON ct.customer_id = cgr.customer_id
WHERE cgr.genre_rank = 1
),
customer_concentration AS (
-- Calculate metrics across all customers before filtering.
SELECT
customer_id,
first_name,
last_name,
genre,
genre_revenue,
total_spending,
top_genre_percentage,
AVG(top_genre_percentage) OVER ()
AS avg_genre_concentration,
top_genre_percentage
- AVG(top_genre_percentage) OVER ()
AS above_average_concentration,
RANK() OVER (
ORDER BY top_genre_percentage DESC
) AS concentration_rank
FROM top_customer_genre
)
SELECT
customer_id,
first_name,
last_name,
genre,
genre_revenue,
total_spending,
top_genre_percentage,
avg_genre_concentration,
above_average_concentration,
concentration_rank
FROM customer_concentration
WHERE top_genre_percentage > 50
ORDER BY
above_average_concentration DESC,
customer_id ASC;