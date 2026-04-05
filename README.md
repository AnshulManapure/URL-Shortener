# Scalable URL Shortener

A production-ready URL shortening service built with FastAPI, PostgreSQL, and Redis, designed for low-latency redirects and high read throughput.

# Live Demo
* Live API: https://url-shortener-aotx.onrender.com/docs
* GitHub: https://github.com/AnshulManapure/URL-Shortener

# Features
* Shorten long URLs into compact, shareable links
* Low-latency redirects using Redis caching
* Rate limiting to prevent abuse (Redis-based)
* Click tracking & analytics pipeline
* Cache-first architecture for read-heavy workloads
* Optimized PostgreSQL queries with indexing
* RESTful API design with FastAPI
* CI/CD pipeline using GitHub Actions
* Deployed on Render

# System Design Overview
This system is designed for read-heavy traffic, where redirects are far more frequent than writes.

Flow:
1. User requests short URL
2. System checks Redis cache
3. If cache hit → instant redirect
4. If cache miss → fetch from DB → update cache → redirect

Key Design Decisions:
* Redis caching reduces database load and improves latency
* Rate limiting prevents spam and ensures reliability
* Stateless backend enables horizontal scaling
* Click tracking stored for future analytics/dashboard

# Tech Stack
* Backend: FastAPI
* Database: PostgreSQL
* Cache & Rate Limiting: Redis
* ORM: SQLAlchemy
* CI/CD: GitHub Actions
* Deployment: Render
* Containerization: Docker

# API Endpoints
### Create Short URL
* POST /shorten

### Redirect
* GET /{short_code}

### Register new user
* POST /register

### Login
* POST /login

### Analytics
* GET /analytics/{short_code}

# Performance Considerations
* Cache-first lookup reduces DB hits significantly
* Indexed queries ensure fast lookups
* Redis enables O(1) access for hot URLs
* Designed to scale horizontally with stateless services

# Rate Limiting
Implemented using Redis to:
* Prevent abuse/spam
* Protect backend resources
* Ensure fair usage

# Analytics
* Tracks click events per short URL
* Stores metadata for future dashboard integration
* Enables insights like:
  * Total clicks
  * Access frequency
  
# Future Improvements
* Custom aliases (/my-link)
* Expiring links
* Full analytics dashboard (frontend)
* Background jobs for analytics processing
* Distributed caching / sharding

# Author
### Anshul Manapure
* GitHub: https://github.com/AnshulManapure
* LinkedIn: https://www.linkedin.com/in/anshul-manapure-6a51a7179/
