-- row number() - rank by customers by spending
select
  c.last_name,
  c.first_name,
  sum(i.total) as total_spending,
  ROW_NUMBER() over (
    order by
      sum(i.total) DESC
  ) as spending_rank
from
  customer c
  join invoice i on i.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.last_name,
  c.first_name
ORDER BY
  spending_rank;


-- rank the customer with ties
select
  c.last_name,
  c.first_name,
  sum(i.total) as total_spent,
  rank() over (
    order by
      sum(i.total) desc
  ) as spending_rank
from
  customer c
  join invoice i on i.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.last_name,
  c.first_name
order by
  spending_rank;


--   revenue by country + country rank
select
  billing_country,
  sum(total) as total_spend,
  rank() over (
    order by
      sum(total) desc
  ) as country_rank
from
  invoice
group by
  billing_country
order by
  country_rank;


--   LAG()
select
  invoice_id,
  customer_id,
  invoice_date,
  total,
  LAG(total) OVER (
    order by
      invoice_date
  ) as previous_inv_total
from
  invoice
order by
  invoice_date;


-- calculate diff using lag()
select
  invoice_id,
  customer_id,
  invoice_date,
  total,
  lag(total) over (
    ORDER BY
      invoice_date
  ) as previous_inv_total,
  total - lag(total) over (
    order by
      invoice_date
  ) as difference
from
  invoice
ORDER BY
  invoice_date;


-- LAG() per customer
select
  customer_id,
  invoice_date,
  total,
  lag(total) over (
    PARTITION BY customer_id
    ORDER BY
      invoice_date
  ) as previous_purchase
from
  invoice
order by
  customer_id,
  invoice_date;


-- first CTE
with
  customer_spending as (
    select
      customer_id,
      sum(total) as spending
    from
      invoice
    GROUP BY
      customer_id
  )
select
  c.customer_id,
  c.last_name,
  c.first_name,
  cs.spending
from
  customer c
  join customer_spending cs on cs.customer_id = c.customer_id
order by
  cs.spending DESC
LIMIT
  10;


--   customer spending above average
with
  customer_spending as (
    select
      customer_id,
      SUM(total) total_spending
    from
      invoice
    GROUP BY
      customer_id
  ),
  average_spending as (
    select
      avg(total_spending) as avg_spending
    from
      customer_spending
  )
select
  c.customer_id,
  c.last_name,
  c.first_name,
  cs.total_spending
from
  customer c
  join customer_spending cs on cs.customer_id = c.customer_id
  cross join average_spending a
where
  cs.total_spending > a.avg_spending
order by
  cs.total_spending desc;


--   top 3 customers per country
with
  customer_spend as (
    select
      c.country,
      c.customer_id,
      sum(i.total) as total_spending,
      ROW_NUMBER() over (
        PARTITION BY c.country
        order by
          sum(i.total) DESC
      ) as rank_spending
    from
      customer c
      join invoice i on i.customer_id = c.customer_id
    GROUP BY
      c.country,
      c.customer_id
  )
select
  *
from
  customer_spend
where
  rank_spending <= 3;


-- rank the artists by revenue
select
  a.name,
  sum(il.quantity * il.unit_price) as total_revenue,
  rank() over (
    order by
      sum(il.quantity * il.unit_price) DESC
  ) as artist_rank
from
  artist a
  join album al on al.artist_id = a.artist_id
  join track t on t.album_id = al.album_id
  join invoice_line il on il.track_id = t.track_id
GROUP BY
  a.artist_id;


--   find each customer's largest invoice
with
  customer_spend as (
    select
      i.customer_id,
      i.invoice_id,
      i.total,
      rank() over (
        PARTITION BY i.customer_id
        order by
          i.total desc
      ) as spending_rank
    from
      invoice i
  )
select
  customer_id,
  invoice_id,
  total
from
  customer_spend
where
  spending_rank = 1;


--   find each customer's second purchase
with
  customer_purchase as (
    select
      customer_id,
      invoice_id,
      ROW_NUMBER() over (
        PARTITION BY customer_id
        order by
          invoice_date
      ) as purchase_rank
    from
      invoice
  )
select
  customer_id,
  invoice_id
from
  customer_purchase cs
where
  cs.purchase_rank = 2;


--   monthly revenue
select
  date_trunc('month', invoice_date),
  sum(total)
from
  invoice
group by
  date_trunc('month', invoice_date);


-- month over month revenue
with
  month_revenue as (
    select
      date_trunc('month', invoice_date) as months,
      sum(total) revenue
    from
      invoice
    group by
      date_trunc('month', invoice_date)
  )
SELECT
months,
revenue,
  lag(revenue) over (
    order by
      months
  ) as previous_revenue,
  revenue - lag(revenue) over (
    order by
      months
  ) as difference_revenue
from
  month_revenue
ORDER BY months;


