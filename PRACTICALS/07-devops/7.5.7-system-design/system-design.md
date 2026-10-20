# System Design Basics — Notes

## Scaling directions

### Vertical scaling (scale up)
- Bigger machine (more CPU, RAM, disk)
- Simple but expensive
- Has a limit
- Single point of failure

### Horizontal scaling (scale out)
- More machines
- Cheap, no limit
- Fault tolerant
- Harder to coordinate

**Big systems use horizontal.**

## The building blocks

### Load balancer
- Routes traffic across many servers
- Removes single point of failure
- Adds/removes servers without downtime
- Examples: Nginx, HAProxy, AWS ALB, Cloudflare

### Cache
- Stores answers to frequent questions
- Fast (RAM instead of disk/compute)
- Risk: stale data
- Examples: Redis, Memcached, CDN

### Database
- Where truth lives, but can be a bottleneck
- Solutions: replication, sharding, read/write split

### Queue
- Async processing
- Instant response to user
- Retry on failure
- Examples: RabbitMQ, Kafka, AWS SQS

### CDN
- Serves static files from servers near user
- Fast, offloads main servers
- Examples: Cloudflare, Akamai, AWS CloudFront

## The architecture (typical)
User → DNS → CDN → Load Balancer → Server cluster
  → Cache → Database

## pos-lab vs real systems
- pos-lab: 1 server, 1 SQLite file, no scale
- Real: hundreds of servers, load-balanced, cached, replicated
- pos-lab works for 1 user. Would fail at 100.
- Big systems build for scale from day one.

## Key insight
- Don't build one big thing. Build many small things that work together.
- Supercomputer = wrong answer for web scale.
- Hundreds of thousands of commodity servers = correct answer.
- WhatsApp: 450M users, ~50 engineers, built for horizontal scale.
