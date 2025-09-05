``` 
Caching Strategy for Customer Query Data

1. **Identify Repetitive Query Patterns**
   - The main query focused on retrieving customer details can lead to repetitive patterns, especially in applications displaying customer information frequently, like in e-commerce applications. 
   - Example query: `SELECT id, name, email, created_at FROM customers;`

2. **Proposed Cache Layers and TTL Rules**
   - **Cache Layer**: Implement a multi-layer caching strategy:
     - **In-Memory Cache (First Layer)**: Utilize Redis or Memcached to store frequently accessed customer data.
       - **TTL (Time to Live)**: Set to 5 minutes for general customer data, allowing for fast access while maintaining some level of freshness.
     - **Persistent Cache (Second Layer)**: Use a database or disk-based caching for less frequently accessed data.
       - **TTL**: Set to 1 hour, serving as a backup if the in-memory cache misses.
   
3. **Track Hit/Miss Rates**
   - Implement logging within the caching layer to record when a cache hit or miss occurs. 
   - Use these metrics to analyze the effectiveness of the cache:
     - **Hit Rate** = Successful cache retrievals / Total cache retrieval attempts.
     - Aim for a target hit rate of 80% to ensure that the cache is indeed improving access speeds.

4. **Design Cache Refresh Policies**
   - **On-Demand Refresh**: If customer data is expected to change (e.g., new sign-ups, updates), establish a mechanism for invalidating cache entries after a change.
   - **Scheduled Refresh**: If certain times of day see increased traffic (e.g., sales events), refresh the cache proactively every X minutes before peak times.
   - **Versioning**: Introduce a version control mechanism for the cache keys, so when significant database updates occur, it can seamlessly switch to a new version of the cache.

In conclusion, this caching strategy emphasizes speed and flexibility while ensuring that users are given up-to-date information. Through layered caching, strategic TTL, and effective monitoring, the system will efficiently handle customer queries while optimizing for performance.
```