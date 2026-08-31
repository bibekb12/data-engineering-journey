-- 01. list all the customers from a specific country
select
  country,
  last_name,
  first_name
from
  customer
where
  country = 'USA';


-- 02. find the 10 logest records
select
  name,
  milliseconds
from
  track
ORDER BY
  milliseconds DESC
limit
  10;


-- 03. find all employee with their job titles
select
  title,
  last_name,
  first_name
from
  employee;


--   04. list customers with their invoices
select
  i.customer_id,
  i.invoice_id,
  i.invoice_date
from
  invoice i
  join customer c on c.customer_id = i.customer_id;


--   05. list customers names with their invoices
select
  i.customer_id,
  c.last_name,
  c.first_name,
  i.invoice_id,
  i.invoice_date
from
  invoice i
  join customer c on c.customer_id = i.customer_id;


--   06 find the total revenue
select
  sum(total)
from
  invoice;


-- 07 find the average invoice value
select
  avg(total)
from
  invoice;


-- 08 find revenue by country
select
  billing_country,
  sum(total) revenue
from
  invoice
group by
  billing_country
order by
  revenue desc;


-- 09 find the number if customer per country
select
  country,
  count(*) customer_count
from
  customer
GROUP BY
  country
order by
  customer_count DESC;


--   10 find the top 10 customers by total spending
select
  customer_id,
  sum(total) spending
from
  invoice
group by
  customer_id
order by
  spending DESC
limit
  10;


-- 11 find the top 5 genere by revenue
select
  g.name,
  sum(il.quantity * il.unit_price) as reveneu
from
  genre g
  join track t on t.genre_id = g.genre_id
  join invoice_line il on il.track_id = t.track_id
group by
  g.genre_id
order by
  reveneu desc
limit
  5;


--   12 tind the top 10 artists by revenue
select
  a.name,
  sum(il.quantity * il.unit_price) as revenue
from
  artist a
  join album al on al.artist_id = a.artist_id
  join track t on t.album_id = al.album_id
  join invoice_line il on il.track_id = t.track_id
group by
  a.artist_id
order by
  revenue desc
limit
  10;


-- 13 find the customer who have never made a purchase
select
  c.last_name,
  c.first_name
from
  customer c
  left join invoice i on i.customer_id = c.customer_id
where
  i.customer_id is null;


--  14 find the customer who spend more than average customer
select
  c.last_name,
  c.first_name,
  sum(i.total) revenue
from
  customer c
  join invoice i on i.customer_id = c.customer_id
group by
  c.customer_id
having
  sum(i.total) > (
    select
      avg(total_spend)
    from
      (
        select
          customer_id,
          sum(total) as total_spend
        from
          invoice
        group by
          customer_id
      )
  )
order by
  revenue DESC;


--   15. find the customer who never bought jazz
SELECT
    c.customer_id,
    c.first_name,
    c.last_name
FROM customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM invoice AS i
    JOIN invoice_line AS il
        ON il.invoice_id = i.invoice_id
    JOIN track AS t
        ON t.track_id = il.track_id
    JOIN genre AS g
        ON g.genre_id = t.genre_id
    WHERE i.customer_id = c.customer_id
      AND g.name = 'Jazz');
