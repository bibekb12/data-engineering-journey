Phase 02 SQL Analysis
Dataset

Database: Chinook
Database engine: PostgreSQL

This phase focuses on analytical SQL, query reasoning, window functions, CTEs, and basic PostgreSQL query-plan analysis.

SQL Concepts Practiced
Common Table Expressions (CTEs)
Aggregation with GROUP BY
Multi-table joins
NOT EXISTS
Anti-join reasoning
ROW_NUMBER()
RANK()
LAG()
PARTITION BY
Deterministic ordering
EXPLAIN
EXPLAIN ANALYZE
Sequential scans
Index scans
Bitmap scans
Hash joins
Nested-loop joins
Planner estimates vs actual execution
Basic index and optimization reasoning
Query #10 — Top 10 Customers by Spending
Business question

Which customers have spent the most money?

Approach

First aggregate invoices at the customer level:

SUM(total)
GROUP BY customer_id


The resulting CTE has one row per customer.

The customer table is then joined to retrieve the customer's name.

The final result is ordered by total spending and limited to the top 10.

Grain

One row per customer.

Key reasoning

The aggregation must happen before the LIMIT.

The query ranks customers based on their total spending across all invoices rather than ranking individual invoices.

A deterministic secondary ordering is used so tied spending produces reproducible output.

Query #11 — Top 5 Genres by Revenue
Business question

Which genres generate the most revenue?

Approach

Revenue is calculated from invoice-line data:

SUM(il.quantity * il.unit_price)


The relationship is:

genre
  ↓
track
  ↓
invoice_line


Revenue is grouped by genre.

Grain

One row per genre.

Key reasoning

invoice_line is the appropriate level for revenue because it contains both quantity and unit price.

The aggregation therefore uses:

quantity * unit_price


rather than invoice totals.

Query #12 — Top 10 Artists by Revenue
Business question

Which artists generate the most revenue?

Approach

The revenue relationship is:

artist
  ↓
album
  ↓
track
  ↓
invoice_line


Revenue is calculated from invoice-line quantity and unit price and grouped by artist.

Grain

One row per artist.

Key reasoning

The artist must be connected to the purchased track through the album relationship.

Grouping by both artist_id and artist name preserves the stable identifier while displaying the human-readable name.

Query #14 — Customers Spending Above Average
Business question

Which customers spend more than the average customer?

Important distinction

The average must be calculated from customer totals, not directly from invoices.

The reasoning is:

Invoices
   ↓
total spending per customer
   ↓
average of customer totals
   ↓
customers above that average


If AVG(invoice.total) were used directly, customers with many invoices would contribute more observations to the average.

That would answer a different question.

Grain

The first CTE:

One row per customer.

The second CTE:

One row containing the average customer spending.

The final result:

One row per customer above the average.

Query #15 — Customers Who Never Bought Jazz
Business question

Which customers have never purchased a Jazz track?

Approach

NOT EXISTS is used to express the anti-existence condition.

For each customer, the subquery asks:

Does there exist a purchase by this customer where the track belongs to Jazz?

If such a row exists, the customer is excluded.

If no such row exists, the customer is returned.

Why NOT EXISTS?

NOT EXISTS directly expresses the business logic:

Return customer
WHERE
no Jazz purchase exists


It also avoids the NULL behavior that can make NOT IN dangerous when the subquery can contain nulls.

Alternative approaches

This problem can also be solved with:

EXCEPT
aggregation with conditional logic
an anti-join

However, NOT EXISTS is particularly readable for this requirement.

Advanced Analysis — Customer Genre Concentration
Business question

For each customer:

What genre generated the most revenue?
How much revenue did that genre generate?
What percentage of the customer's spending came from that genre?
How does that concentration compare with other customers?
Step 1 — Customer + Genre Revenue

The first CTE creates:

customer + genre → revenue


This is the most important grain in the first stage.

Revenue is calculated using:

SUM(il.quantity * il.unit_price)


The join path is:

customer
   ↓
invoice
   ↓
invoice_line
   ↓
track
   ↓
genre

Step 2 — Rank Genres Within Each Customer

ROW_NUMBER() is used:

ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY genre_revenue DESC, genre ASC, genre_id ASC
)


The PARTITION BY customer_id means that each customer gets an independent ranking.

The result is conceptually:

Customer A | Rock  | 50 | 1
Customer A | Jazz  | 40 | 2
Customer A | Metal | 20 | 3

Customer B | Jazz  | 60 | 1
Customer B | Rock  | 30 | 2

Why ROW_NUMBER() Instead of RANK()?

The requirement is to select exactly one top genre per customer.

ROW_NUMBER() guarantees one row receives rank 1.

RANK() can assign the same rank to multiple rows when values tie.

For example:

Rock | $50 | rank 1
Jazz | $50 | rank 1


Using ROW_NUMBER() with a deterministic secondary ordering allows us to select exactly one genre.

Deterministic Ordering

The ranking uses:

ORDER BY
    genre_revenue DESC,
    genre ASC,
    genre_id ASC


Revenue is the primary criterion.

If revenue ties, genre name breaks the tie.

If the name were also tied, genre_id provides another stable ordering key.

This makes the result reproducible.

Step 3 — Calculate Customer Total Spending

A separate CTE calculates:

customer → total spending


This is deliberately kept at a different grain.

customer_total
--------------------------
customer_id | total_spending


This avoids mixing customer-level totals with customer+genre-level aggregation.

Step 4 — Calculate Top-Genre Concentration

After selecting the top genre for each customer:

100.0 * genre_revenue / NULLIF(total_spending, 0)


calculates the percentage of customer spending represented by the top genre.

For example:

Top genre revenue = $60
Total spending    = $100

Concentration = 60%


NULLIF(total_spending, 0) prevents division-by-zero errors.

100.0 also ensures the calculation is performed as a decimal rather than relying on integer division.

Step 5 — Compare Customers Using Window Functions

The query calculates the overall average:

AVG(top_genre_percentage) OVER ()


Because there is no PARTITION BY, the window contains all customers.

Therefore every row receives the same average concentration.

The query also calculates:

RANK() OVER (
    ORDER BY top_genre_percentage DESC
)


This ranks customers against one another.

Why RANK() here?

Unlike selecting the top genre, this analysis should preserve ties.

If two customers both have 80% concentration:

Customer A → rank 1
Customer B → rank 1
Customer C → rank 3


That is different from the earlier use of ROW_NUMBER().

Step 6 — Filter After Window Calculations

The concentration ranking is calculated in a separate CTE before applying:

WHERE top_genre_percentage > 50


This is intentional.

If the filter were applied before calculating RANK(), customers below 50% would disappear from the window-function input.

The resulting rank would then describe only customers above 50%.

The current structure allows the rank to represent each customer's position among all customers.

This is a common analytical SQL pattern:

calculate dataset
      ↓
window calculation
      ↓
filter in outer query

PostgreSQL EXPLAIN ANALYZE Notes
Sequential Scan

A sequential scan reads the table from beginning to end.

Example:

Seq Scan on invoice


For a small table such as Chinook's invoice, this can be completely reasonable.

An index is not automatically faster.

If a query needs a large percentage of a small table, PostgreSQL may prefer a sequential scan because scanning the table directly is cheaper than using an index and repeatedly accessing table pages.

Index Scan

An index scan is useful when a query needs a relatively small subset of rows.

For example:

WHERE invoice_id = 100


can efficiently use the primary-key index.

The index helps PostgreSQL locate the relevant row without scanning every invoice.

Bitmap Scan

A bitmap scan can be useful when multiple rows match an indexed condition.

The process can be thought of as:

Index
  ↓
identify matching row locations
  ↓
build bitmap of relevant pages
  ↓
read table pages


This can be more efficient than performing many individual index lookups.

In the Chinook examples, filtering invoices by customer_id produced a bitmap index scan followed by a bitmap heap scan.

Join Strategies
Hash Join

A hash join is useful when PostgreSQL can build a hash table for one input and match rows from the other input.

A typical plan looked like:

Hash Join
├── Seq Scan on invoice
└── Hash
    └── Seq Scan on customer


For the small Chinook tables, sequential scans plus hash joins are often inexpensive.

Nested Loop

A nested loop can be effective when the outer relation produces only a small number of rows and the inner relation can be accessed efficiently.

For example:

one customer
    ↓
find that customer's invoices


An index on invoice.customer_id can make the inner lookup efficient.

Nested loops are not inherently bad.

Their usefulness depends heavily on the number of outer rows and the cost of the inner operation.

Planner Cost vs Actual Time

EXPLAIN shows PostgreSQL's estimated plan.

EXPLAIN ANALYZE actually executes the query and reports runtime information.

Important fields include:

cost — planner estimate used for choosing between plans
rows — estimated number of rows
actual time — observed execution timing
actual rows — observed number of rows
loops — number of times the operation executed

The estimates do not represent milliseconds.

They are internal planner cost units.

Statistics

PostgreSQL uses table statistics to estimate things such as:

how many rows will match a condition
how selective a predicate is
which join strategy is likely to be cheaper
whether an index is worthwhile

ANALYZE updates these statistics.

EXPLAIN ANALYZE executes the query and reports actual results, but the important conceptual distinction is:

ANALYZE → collects/updates planner statistics
EXPLAIN ANALYZE → executes the query and compares the plan estimates with actual execution

Key Lessons From Phase 02

The biggest lesson from this phase is that SQL is not just about writing syntactically correct queries.

A strong analytical query starts by identifying:

What is the business question?
What is the grain of the result?
What tables contain the required information?
What joins connect those tables?
Where should aggregation occur?
Do we need a window function?
Should we use ROW_NUMBER() or RANK()?
Does ordering need a deterministic tie-breaker?
Does a later filter need to happen after a window calculation?
What does PostgreSQL actually do according to EXPLAIN ANALYZE?

The goal is to reason through these questions before writing the SQL.

Phase 02 Summary

Phase 02 progressed from standard aggregation and joins into multi-stage analytical SQL.

The advanced customer-genre analysis combined:

CTEs
  +
aggregation
  +
multiple grains
  +
ROW_NUMBER()
  +
PARTITION BY
  +
RANK()
  +
AVG() OVER ()
  +
deterministic ordering
  +
post-window filtering

