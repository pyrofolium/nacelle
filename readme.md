## Some things I would do to optimize and scale:

- Transition from SQLite to a more robust data warehouse like **Snowflake** or **BigQuery** or **Redshift** for handling high volumes of data and supporting complex queries. These platforms are optimized for concurrent access and large datasets.
- Add indexes to frequently accessed columns, such as `product_id` in `customer_feedback` and `marketing_campaigns` tables, to speed up joins and lookups.
- Implement an async job that loads products and customer into the database.
- Use **Redis** to cache frequently accessed data, such as `products` or recent `recommendations`. For instance, `get_product_data()` can cache product details for a set duration, reducing database calls and response times.
- Employ a cache invalidation strategy for customer IDs based on their interactions. For example, update Redis when a customer interacts with new products or when new recommendations are generated.
- Offload recommendation generation to a task queue using **Celery** or **Dramatiq** with **RabbitMQ** or something imilar  as the broker. This setup allows FastAPI to quickly respond to `/recommendations/<customer_id>` by either serving cached data or queuing a new task if needed.
- Instead of generating recommendations one customer at a time, periodically request bulk recommendations for multiple active customers. This can be done by aggregating product and customer data and sending it to OpenAI in a single batch.
- Use local models. We can use a more targetted model rather then an LLM. The input would be past purchases and the output would be recommended purchases. Initially we can use the LLM to give the initial data when no purchase data is available. 
- Store historical data, such as older customer feedback and previous marketing campaigns, in distributed storage solutions (e.g., **AWS S3** or **Google Cloud Storage**). This keeps the active database lightweight and focused on current, relevant data.

answer these questions related to the project:
As part of the coding challenge, please provide a high-level system design for scaling the
personalization engine you&#39;ve built to handle millions of users and products. Consider the
following:
1. How would you design the data pipeline to handle real-time updates to product
information, customer feedback, and marketing campaigns?

Assuming product updates, customer feedback and marketing campaigns are coming in at high volume I would use some 
queue like kafka to queue these operations up during high traffic periods and batch insert them. If they are seldomely
updated then directly inserting or updating a SQL database should be sufficient. 

2. What database choices would you make for storing different types of data (product
catalog, user interactions, recommendations)?

Assuming user interactions are high volume and recommendations and product catalogue are low volume writes then
User interactions would go into a database designed for analytics like big query. recommendations and product catalogue
would go into a typical SQL database. 

3. How would you ensure low latency for product recommendations, even during high
traffic periods?

Recommendations happen through the openai api which is very slow and expensive. I would have an async job that runs
periodically that queries current products, customer profiles and updates the recommendations for each customer. Of 
course this job runs during low traffic periods.

Additionally I can put caching up so customers who access recommendations frequently don't hit the database but they
hit the cache instead. 

If the web app gets overloaded you can put load balancing and auto-scaling on top of it. 

4. How would you implement A/B testing for different recommendation algorithms?

The user interaction database should have all the events related to interaction. From here you can construct aggregate
queries that give you information about user interaction allowing you to look into the past and see outcomes based
on changes you conducted. For example count all click events after 3pm assuming you made a change at 3pm. 

Also deploy features as config flags so you can easily turn something on or off without a code deployment. 

Additionally you can use something to split the traffic so not all users are part of the test. 

5. What monitoring and alerting systems would you put in place to ensure the reliability of
the personalization engine?

Health check links and using some health check to track if each server is online. Also log monitoring and making sure
if a 500 is triggered or if a cluster of unxpected log lines are activated it triggers some sort of alert that goes
to someones phone/email/etc. 



Please provide a diagram (you can use ASCII art or describe it in text) and a brief explanation of
your design choices.
--------
Basically you have a web app with a SQL database and a pipeline for processing and counting user events.
When the user makes a request or does something on the website it throws an event down the data pipeline that gets
processed by something else later or it gets placed into an analytics database. 

The request also triggers an action in the main database that usually involves a read of the database as well. 

Async jobs can be done by something like celery with a rabbitMQ broker. These workers will mostly operating during low traffic
to update the recommendation engine with new results from updated product/customer data and openai results. 