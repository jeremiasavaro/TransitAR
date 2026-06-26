# Recommendations — TransitAR MVP

*This document contains opinions and recommendations from the consulting/technical lead perspective.*

---

## Recommended Technology Stack

| Layer | Recommendation | Rationale |
|-------|---------------|-----------|
| **LLM Provider** | OpenAI GPT-4o or Anthropic Claude 3.5 Sonnet | Best-in-class tool-calling performance; mature APIs; extensive SDK ecosystem. Start with one, maintain provider abstraction. |
| **Backend Runtime** | TypeScript / Node.js or Python | TypeScript offers end-to-end types if frontend is web-based. Python has stronger geospatial libraries (GeoPandas, Shapely) and GTFS tooling (gtfs-lib, partridge). Recommendation: Python for data-heavy services, Node.js for lightweight API layer — or consolidate in one language for MVP simplicity. |
| **Geospatial Database** | PostgreSQL with PostGIS | Mature, well-documented, handles GTFS relational model and geospatial queries in a single system. Extensive ecosystem (pgRouting for advanced routing). Open source with excellent operational tooling. |
| **Geocoding** | Nominatim (OSM) + Google Geocoding as fallback | Nominatim is free and suitable for MVP volumes. Google fallback for low-confidence results. Both have good Argentina coverage for major landmarks. |
| **Conversational Interface** | Responsive Web App (PWA) | Maximizes reach without app store friction. Can be wrapped in native shells later. Supports geolocation API natively. |
| **Infrastructure** | Containerized (Docker) on PaaS (e.g., Railway, Fly.io) | Minimal operational overhead for MVP. Easy to migrate to AWS/GCP later. |

**Why not alternatives:**
- Go/Rust: Premature optimization for MVP scale; smaller GTFS ecosystem
- MongoDB: Weaker geospatial querying and relational integrity compared to PostGIS
- Serverless: Cold start and timeout constraints conflict with LLM call latency
- No-code/LLM-only platforms: No control over business logic; vendor lock-in; cannot meet GTFS integration requirements

---

## Recommended Deployment Strategy

**Phase 1 (MVP): Containerized monolith on a PaaS**

- Single Docker image containing all services (web, API, tool layer)
- PostgreSQL (managed via PaaS add-on or separate managed DB)
- Weekly GTFS data refresh via scheduled job
- No orchestration beyond Docker Compose or simple PaaS deploy

**Rationale:**
- Fastest path to production
- Single deployable reduces DevOps burden
- Easy to split services later when warranted
- PaaS handles SSL, scaling, logging basics

**Phase 2 (Post-MVP): Service decomposition**

- Split tool layer, geocoding, and trip planning into separate services
- Add message queue for async ingestion
- Container orchestration (K8s or Nomad) for multi-service management

---

## Mobile vs Web Recommendations

**Build a Progressive Web App (PWA) for the MVP.**

**Rationale:**
- Zero app store friction — users access via URL
- Geolocation API works on mobile browsers
- Service workers enable basic offline support (though not an MVP requirement)
- Can be wrapped with Capacitor or similar for app store distribution later
- Single codebase for desktop and mobile

**Chat platforms (WhatsApp, Telegram) are recommended as the second channel** immediately after MVP validation, as they represent the primary communication tool for the target audience.

**Do not build native iOS/Android apps in the MVP phase.** The development and maintenance cost per platform does not justify the incremental reach.

---

## MVP Scope Recommendations

### Build

| Feature | Priority | Why |
|---------|----------|-----|
| GTFS data ingestion pipeline | P0 | Foundation for all transportation data |
| Nearby stop discovery | P0 | Core MVP capability |
| Route discovery (which lines serve a stop) | P0 | Core MVP capability |
| Basic trip planning (A→B with transfers) | P0 | Core MVP capability |
| Schedule lookup (stop times, route times) | P0 | Core MVP capability |
| Geocoding (place name → coordinates) | P0 | Required for location-aware queries |
| Conversational web interface | P0 | User-facing entry point |
| LLM tool calling integration | P0 | Core architectural decision |
| Fallback handling for ambiguous queries | P1 | UX polish |
| Conversation session management | P1 | Contextual follow-ups |

### Do Not Build (MVP)

| Feature | Reason |
|---------|--------|
| Real-time vehicle tracking | Explicitly out of scope per MVP definition |
| Predictive arrivals | Requires real-time data + ML model |
| Multi-city support | Single-city validation first |
| Offline mode | Out of scope |
| Ticket purchasing / payment | Out of scope |
| User accounts / authentication | Not required for MVP; add rate limiting instead |
| Native mobile apps | Web-first; mobile via PWA |
| Multi-language support | Spanish-first; internationalize later |
| Voice assistant | Requires platform-specific integrations |
| Analytics dashboard | Build internal logging first; public dashboard later |