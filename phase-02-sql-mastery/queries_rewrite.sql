# 10 top 10 customers by spending

with
  customer_spending as (
    select
      customer_id,
      sum(total) total_revenue
    from
      invoice
    GROUP BY
      customer_id
  )
select
  c.customer_id,
  c.last_name,
  c.first_name,
  cs.total_revenue
from
  customer_spending cs
  join customer c on c.customer_id = cs.customer_id
ORDER BY
  total_revenue desc, first_name desc ,last_name desc, customer_id desc
limit
  10;

-- 11 top 5 genere by revenue

with
  genere_revenue as (
    select
      g.name,
      sum(il.quantity * il.unit_price) as revenue
    from
      genre g
      join track t on t.genre_id = g.genre_id
      join invoice_line il on il.track_id = t.track_id
    group by
      g.genre_id,
      g.name
  )
select
  name,
  revenue
from
  genere_revenue
order by
  revenue desc, name asc
limit
  5;


-- 12 top 10 artist by revenue

with
  artist_revenue as (
    select
      a.artist_id,
      a.name,
      sum(il.unit_price * il.quantity) as revenue
    from
      artist a
      join album al on al.artist_id = a.artist_id
      join track t on t.album_id = al.album_id
      join invoice_line il on il.track_id = t.track_id
    GROUP BY
      a.artist_id,
      a.name
  )
select
  artist_id,
  name,
  revenue
from
  artist_revenue
order by
  revenue desc, name desc, artist_id desc
limit
  10;

-- 14 customer spending above average

with
  customer_spending as (
    select
      customer_id,
      sum(total) total_spend
    from
      invoice
    GROUP BY
      customer_id
  ),
  average_spending as (
    select
      avg(total_spend) avg_spend
    from
      customer_spending
  )
select
  c.customer_id,
  c.last_name,
  c.first_name,
  total_spend
from
  customer_spending
  cross join average_spending
  join customer c on c.customer_id = customer_spending.customer_id
where
  total_spend > avg_spend
order by
  customer_spending.total_spend desc;


--   15 customer never bought jazz

-- solution 1 

select
  c.customer_id,
  c.last_name,
  c.first_name
from
  customer c
where
  not exists (
    select
      1
    from
      invoice i
      join invoice_line il on il.invoice_id = i.invoice_id
      join track t on t.track_id = il.track_id
      join genre g on g.genre_id = t.genre_id
    where
      g.name = 'Jazz'
      and i.customer_id = c.customer_id
  );

--   solution 2

select
  c.customer_id,
  c.last_name,
  c.first_name
from
  customer c
EXCEPT
select
  c.customer_id,
  c.last_name,
  c.first_name
from
  customer c
  join invoice i on c.customer_id = i.customer_id
  join invoice_line il on il.invoice_id = i.invoice_id
  join track t on t.track_id = il.track_id
  join genre g on g.genre_id = t.genre_id
where
  g.name = 'Jazz';


--   solution 3
with
  jazz_buy as (
    select
      DISTINCT c.customer_id
    from
      customer c
      join invoice i on c.customer_id = i.customer_id
      join invoice_line il on il.invoice_id = i.invoice_id
      join track t on t.track_id = il.track_id
      join genre g on g.genre_id = t.genre_id
    where
      g.name = 'Jazz'
  )
select
  c.customer_id,
  c.last_name,
  c.first_name
from
  customer c
where
  c.customer_id not in (
    select
      customer_id
    from
      jazz_buy
  );


--   solution 4 
select
  customer_id,
  last_name,
  first_name
from
  customer
where
  customer_id not in (
    select
      DISTINCT c.customer_id
    from
      customer c
      join invoice i on c.customer_id = i.customer_id
      join invoice_line il on il.invoice_id = i.invoice_id
      join track t on t.track_id = il.track_id
      join genre g on g.genre_id = t.genre_id
    where
      g.name = 'Jazz'
  );

--   solution 5

select
  c.customer_id,
  c.last_name,
  c.first_name
from
  customer c
  join invoice i on i.customer_id = c.customer_id
  join invoice_line il on il.invoice_id = i.invoice_id
  join track t on t.track_id = il.track_id
  join genre g on g.genre_id = t.genre_id
GROUP BY
  c.customer_id,
  c.last_name,
  c.first_name
HAVING
  COALESCE(
    sum(
      case
        when g.name = 'Jazz' then 1
        else 0
      end
    ),
    0
  ) = 0