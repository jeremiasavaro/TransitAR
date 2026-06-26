# Technical Decisions — TransitAR MVP

## Accepted Decisions

These decisions are considered settled for the MVP unless strong evidence emerges during implementation.

### 1. Tool Calling / MCP over Pure RAG

- **Decision**: Use function-calling / MCP-style tool invocation instead of pure Retrieval-Augmented Generation for transportation data
- **Rationale**: Transportation information is structured (routes, schedules, stops). Semantic retrieval over unstructured documents introduces ambiguity, latency, and hallucination risk. Tool-based invocation allows deterministic, verifiable data access.
- **Consequence**: The LLM never queries a vector store for transportation facts. It calls typed functions that return structured results.

### 2. Structured Transportation Data

- **Decision**: Treat all transportation information as structured data (tables, spatial indexes, time-series) rather than documents
- **Rationale**: Routes, schedules, and stops are naturally relational/geospatial. Storing them as structured data enables efficient querying, validation, and consistency enforcement.
- **Consequence**: The ingestion pipeline transforms raw data (e.g., GTFS) into normalized, indexed data stores. No document stores are used for primary transportation data.

### 3. GTFS-First Data Approach

- **Decision**: GTFS (General Transit Feed Specification) is the primary data format for importing transportation data
- **Rationale**: GTFS is the global standard for public transit data. It is well-documented, widely adopted by municipalities, and includes all MVP-required data (stops, routes, trips, schedules). Using GTFS ensures interoperability and future scalability.
- **Consequence**: Data onboarding for new cities depends on GTFS availability. Custom data transformation may be required for cities without official GTFS feeds.

### 4. Geospatial Search Approach

- **Decision**: Use spatial indexing and geospatial queries (radius search, point-in-polygon) as the primary mechanism for proximity-based discovery
- **Rationale**: "Nearby" and "closest to" are inherently spatial operations. Geospatial queries are efficient, deterministic, and well-understood.
- **Consequence**: The system requires geospatial indexing capabilities (e.g., R-tree, geohash, or equivalent). All stops and routes are geocoded with coordinates.

### 5. LLM Responsibility Boundaries

- **Decision**: The LLM is strictly limited to NLU, intent extraction, and response generation. It must never be the source of truth for transportation data.
- **Rationale**: LLMs are prone to hallucination and lack guarantees on factual accuracy for dynamic data. By constraining the LLM to a natural language interface role, the system ensures that all factual responses are grounded in verified data sources.
- **Consequence**: Every factual claim in a response must be traceable to a tool invocation result. No transportation data is included in the LLM's system prompt or context beyond that returned by tools.

### 6. Business Logic Outside the LLM

- **Decision**: All business logic (trip planning algorithms, schedule calculations, fare rules) lives in dedicated services, not in LLM prompts
- **Rationale**: Business logic requires deterministic behavior, testability, and auditability. Embedding logic in prompts makes the system fragile, untestable, and prompt-injection vulnerable.
- **Consequence**: The LLM is a thin orchestration layer. Complex computations are delegated to backend services.

### 7. Intent-Driven Tool Dispatch

- **Decision**: Tool invocation is driven by the LLM's intent classification, not by hard-coded rules or a separate intent classifier
- **Rationale**: LLMs are well-suited to understanding varied natural language expressions of the same intent. Using the LLM for both classification and response reduces architectural complexity and cascading failure points.
- **Consequence**: The system depends on the LLM correctly selecting tools. Tool definitions must be clear, with explicit parameter schemas and descriptions.

---

## Deferred Decisions

These decisions are deferred until after the MVP (or until validated through discovery). Each includes alternatives, tradeoffs, risks, and confidence level.

### 1. Programming Language

| Aspect | Detail |
|--------|--------|
| **Alternatives** | Python, TypeScript/Node.js, Go, Rust, Java/Kotlin |
| **Tradeoffs** | Python has the richest AI/ML ecosystem but weaker concurrency. TypeScript/Node.js offers good I/O performance and shared types with frontend. Go provides excellent performance and simple deployment. Rust offers maximum performance at development complexity cost. |
| **Risks** | Choosing too early may conflict with LLM provider SDK availability, GTFS parsing library quality, and team expertise |
| **Recommendation** | Defer to implementation phase based on team skills and ecosystem fit |
| **Confidence** | Medium — any mainstream choice works for MVP scale |

### 2. Database Technology

| Aspect | Detail |
|--------|--------|
| **Alternatives** | PostgreSQL (with PostGIS), SQLite with SpatiaLite, DuckDB, MongoDB with GeoJSON |
| **Tradeoffs** | PostgreSQL/PostGIS is mature, well-supported, and handles structured + geospatial data in one system. SQLite is simpler but less concurrent. DuckDB is excellent for analytics but not suited for transactional workloads. MongoDB offers flexibility but weaker geospatial and relational capabilities. |
| **Risks** | PostGIS learning curve; over-engineering if simple data structures suffice |
| **Recommendation** | Defer — but strong leaning toward PostgreSQL/PostGIS for MVP given GTFS's relational nature and geospatial requirements |
| **Confidence** | High — PostGIS is a proven choice for GTFS-based systems |

### 3. Deployment Strategy

| Aspect | Detail |
|--------|--------|
| **Alternatives** | Serverless (AWS Lambda + API Gateway), Container-based (Docker + ECS/K8s), PaaS (Railway, Fly.io, Heroku), VM-based |
| **Tradeoffs** | Serverless offers auto-scaling and low cost at low traffic but suffers from cold starts and may struggle with long-running LLM calls. Containers offer flexibility and environment consistency. PaaS trades control for simplicity. |
| **Risks** | Choosing a platform that doesn't support long-lived LLM connections |
| **Recommendation** | Defer — but containerized deployment on a PaaS offers the best MVP tradeoff |
| **Confidence** | Medium — depends on team familiarity and LLM provider integration requirements |

### 4. Mobile vs Web

| Aspect | Detail |
|--------|--------|
| **Alternatives** | Progressive Web App, Native Mobile (iOS/Android), Chat interface (WhatsApp/Telegram), Standalone Website |
| **Tradeoffs** | PWA offers cross-platform reach with minimal development cost. Native mobile gives best UX and device sensor access. Chat interfaces bypass app distribution but constrain UI/UX. |
| **Risks** | Choosing a platform that limits reach or requires app store approval delays |
| **Recommendation** | Defer — but a web-first approach (PWA or responsive web app) maximizes reach for MVP |
| **Confidence** | Medium — MVP validation can happen on any platform |

### 5. Hosting Provider

| Aspect | Detail |
|--------|--------|
| **Alternatives** | AWS, Google Cloud, Azure, DigitalOcean, Railway, Fly.io |
| **Tradeoffs** | Major clouds offer full service breadth but operational complexity. Smaller PaaS offerings reduce overhead at the cost of flexibility and vendor lock-in. |
| **Risks** | Selection should not precede deployment strategy or programming language |
| **Recommendation** | Defer — decision flows from deployment strategy and team expertise |
| **Confidence** | Low — too many variables to recommend confidently pre-architecture |

### 6. Authentication Approach

| Aspect | Detail |
|--------|--------|
| **Alternatives** | No auth (public access), API key, OAuth2 (Google/GitHub), Magic link, Phone number |
| **Tradeoffs** | No auth maximizes adoption but lacks personalization and rate limiting per user. OAuth2 adds development complexity but enables future personalization (favorites, history). |
| **Risks** | MVP may not need auth at all; adding it prematurely creates friction for early users |
| **Recommendation** | Defer — start without auth for MVP, add rate limiting at infrastructure level |
| **Confidence** | High — auth is not an MVP requirement per the project scope |

### 7. LLM Provider

| Aspect | Detail |
|--------|--------|
| **Alternatives** | OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini), Open-source self-hosted (Llama, Mistral) |
| **Tradeoffs** | Commercial providers offer best-in-class NLU and tool calling but incur per-token costs and external dependency. Open-source models offer lower operational cost and data privacy but require significant infrastructure investment and may have weaker tool-calling performance. |
| **Risks** | Provider API changes, deprecation, pricing changes, or downtime |
| **Recommendation** | Defer — but start with a commercial provider for rapid prototyping and tool-calling maturity |
| **Confidence** | Medium — provider landscape evolves rapidly |

### 8. Geocoding Provider

| Aspect | Detail |
|--------|--------|
| **Alternatives** | Nominatim (OpenStreetMap), Google Maps Geocoding API, Mapbox, Pelias |
| **Tradeoffs** | Nominatim is free but rate-limited and slower. Google/Mapbox offer high accuracy and speed but charge per request. Pelias is self-hostable from OSM data. |
| **Risks** | Accuracy for Argentine place names varies significantly across providers |
| **Recommendation** | Defer — requires evaluation against target city location data (covered by Discovery & Research backlog) |
| **Confidence** | Medium — depends on data quality findings |

### 9. Observability

| Aspect | Detail |
|--------|--------|
| **Alternatives** | Self-hosted (Grafana + Prometheus + Loki), Managed (Datadog, New Relic, Sentry), Cloud-native (CloudWatch, GCP Monitoring) |
| **Tradeoffs** | Managed solutions reduce setup cost but incur monthly fees. Self-hosted is cheaper at scale but requires operational expertise. |
| **Risks** | Insufficient observability in MVP makes debugging LLM behavior difficult |
| **Recommendation** | Defer — but lightweight logging and LLM call tracing should be implemented from day one regardless of the chosen system |
| **Confidence** | High — observability approach can be evolved incrementally |
