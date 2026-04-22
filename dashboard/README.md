# Dashboard Guide (Metabase)

This folder stores dashboard notes and future exported assets.

## Suggested Dashboard Tabs
1. Trends per day
- Source: `articles_stats`
- Chart: line
- X: `event_date`
- Y: sum(`article_count`)
- Filter: `category`, `source`

2. Articles per source
- Source: `articles_stats`
- Chart: bar
- Dimension: `source`
- Metric: sum(`article_count`)

3. Category distribution
- Source: `articles_stats`
- Chart: pie or stacked bar
- Dimension: `category`
- Metric: sum(`article_count`)

4. Latest clean articles
- Source: `articles_clean`
- Chart: table
- Columns: `published_at`, `source`, `category`, `title`, `language`

## Metabase Setup Quick Steps
1. Open Metabase at http://localhost:3000
2. Add PostgreSQL database:
- Host: postgres (or localhost from host machine)
- Port: 5432
- DB: sports_warehouse
- User: sports_user
- Password: sports_pass
3. Sync schema and create questions
4. Group questions into one dashboard named "Sports Media Monitoring"
