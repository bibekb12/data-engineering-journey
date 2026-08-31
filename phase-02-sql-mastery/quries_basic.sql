-- Active: 1788163553050@@localhost@5432@chinook@public
-- listing all the cusmtomer with id, first_name, last_name and country located
select
  customer_id,
  first_name,
  last_name,
  country
from
  customer;


-- listing customer first name, last name and email from the brazil
select
  first_name,
  last_name,
  email
from
  customer
where
  country = 'Brazil';


-- listing track longer than 5 minutes
select
  name,
  milliseconds
from
  track
where
  milliseconds > 5 * 60 * 1000
order by
  milliseconds DESC;


-- inner join
-- customer and invoices
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  i.invoice_id,
  i.invoice_date,
  i.total
FROM
  customer c
  INNER JOIN invoice i on c.customer_id = i.customer_id
ORDER BY
  i.invoice_date;


-- invoice lines with track name
select
  invoice_line_id,
  invoice_id,
  name as track_name,
  quantity,
  invoice_line.unit_price
from
  invoice_line
  join track on invoice_line.track_id = track.track_id;


-- artists cutomer bought
select
  c.first_name,
  c.last_name,
  ar.name as artist,
  t.name as track
from
  customer c
  join invoice i on i.customer_id = c.customer_id
  join invoice_line il on il.invoice_id = i.invoice_id
  join track t on t.track_id = il.track_id
  join album a on a.album_id = t.album_id
  join artist ar on ar.artist_id = a.artist_id
order by
  c.last_name,
  ar.name;


-- total revenue
select
  sum(total) total_revenue
from
  invoice;


-- number of invoices
select
  count(*) total_invoices
from
  invoice;


-- average invoice value
select
  avg(total) as average_total
from
  invoice;


-- revenue by country
select
  billing_country,
  sum(total) as revenue
from
  invoice
group by
  billing_country
order by
  revenue DESC;


-- number of customer per country
select
  country,
  count(*) as no_of_customer
from
  customer
group by
  country
order by
  no_of_customer DESC;


-- country more than 5 customer
select
  country,
  count(*) customer_count
from
  customer
GROUP BY
  country
HAVING
  count(*) > 5
order by
  customer_count DESC;


-- top 5 genere by revenue
select
  g.name,
  SUM(il.quantity * il.unit_price) revenue
from
  genre g
  join track t on t.genre_id = g.genre_id
  join invoice_line il on il.track_id = t.track_id
group by
  g.genre_id
order by
  revenue DESC
limit
  5;


-- customer who have spent more than average customer
select
  avg(total_spend)
from
  (
    select
      customer_id,
      sum(total) total_spend
    from
      invoice
    GROUP BY
      customer_id
  );


select
  c.last_name,
  c.first_name,
  sum(i.total) spend 
from
  customer c
  join invoice i on i.customer_id = c.customer_id
group by c.last_name, c.first_name, c.customer_id
HAVING sum(i.total)> (select
  avg(total_spend)
from
  (
    select
      customer_id,
      sum(total) total_spend
    from
      invoice
    GROUP BY
      customer_id
  ))
  order by spend desc;