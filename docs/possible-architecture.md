# Architecture — TransitAR MVP

## System Context

TransitAR is an intelligent conversational assistant that answers public transportation questions across Argentina. Users interact via natural language, and the system resolves their intent through a tool-based architecture that delegates transportation queries to specialized services rather than relying on LLM knowledge or semantic retrieval.

The MVP validates the architecture for a single city before expanding nationwide.

## High-Level Architecture

```
User
  └─> Conversational Interface
        └─> LLM (NLU + Intent Extraction + Response Generation)
              └─> Tool Layer / MCP Layer
                    ├─> Transportation Services
                    │     ├─> Stop Discovery
                    │     ├─> Route Discovery
                    │     ├─> Trip Planning
                    │     └─> Schedule Lookup
                    └─> Geospatial Services
                          ├─> Geocoding
                          └─> Proximity Search
                                └─> Transportation Data Sources (GTFS, OpenStreetMap, etc.)
```

## Components & Responsibilities

### 1. Conversational Interface
- Receives user input (text, geolocation if available)
- Renders responses to the user
- Provides session management (conversation history)
- Handles input validation and basic sanitization

### 2. LLM Layer
- **Natural Language Understanding**: Parses user input to extract intent and entities (locations, route numbers, time references)
- **Intent Classification**: Maps user queries to tool invocations
- **Parameter Extraction**: Extracts structured parameters from free-text input
- **Response Generation**: Composes human-readable answers from tool results
- **Fallback Handling**: Gracefully manages ambiguous or unrecognizable queries
- The LLM does **not** contain transportation domain knowledge; it only interprets and responds

### 3. Tool Layer / MCP Layer
- Exposes a set of capabilities as callable tools
- Translates LLM intent into structured service calls
- Aggregates and formats results for response generation
- Handles tool execution errors and timeouts
- Tools are stateless and idempotent where possible

### 4. Transportation Services
- **Stop Discovery**: Finds stops near a given location
- **Route Discovery**: Returns routes/lines serving a given stop or area
- **Trip Planning**: Computes optimal paths between origin and destination using transit schedules
- **Schedule Lookup**: Returns timetable information for a stop, route, or trip
- **Destination Resolution**: Matches fuzzy location names to known points of interest or transit hubs
- Each service encapsulates its own domain logic; none depends on the LLM

### 5. Geospatial Services
- **Geocoding**: Converts place names (e.g., "Patio Olmos") to coordinates
- **Reverse Geocoding**: Converts coordinates to place names or addresses
- **Proximity Search**: Finds transportation stops within a radius of a given coordinate
- **Spatial Indexing**: Maintains efficient spatial lookups for stops and routes

### 6. Transportation Data Sources
- **GTFS Feeds**: Primary structured data format for routes, stops, schedules, and trips
- **Geospatial Datasets**: OpenStreetMap or equivalent for map data
- The ingestion pipeline validates, normalizes, and indexes data from these sources

## Information Flow

### Query Flow
1. User submits a natural language query (e.g., "How do I get to Patio Olmos from the Córdoba Bus Terminal?")
2. Conversational Interface passes the query plus conversation context to the LLM
3. LLM classifies intent and extracts structured parameters (origin, destination, time constraint)
4. LLM calls the appropriate tool(s) via the Tool Layer
5. Tool Layer invokes the relevant Transportation or Geospatial Service
6. Service queries the structured data sources
7. Results flow back through the Tool Layer to the LLM
8. LLM composes a natural language response
9. Response is rendered to the user via the Conversational Interface

### Data Flow
- GTFS feeds are ingested, validated, and stored into structured data stores
- A scheduled update mechanism refreshes data at appropriate intervals
- Geospatial indexes are rebuilt on data updates
- All service queries operate on the indexed, structured data — not on raw GTFS files at query time

## Service Boundaries

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                     │
├─────────────────────────────────────────────────────┤
│                    LLM Layer                         │
├─────────────────────────────────────────────────────┤
│                  Tool / MCP Layer                    │
├──────────┬──────────┬──────────┬────────────────────┤
│  Stop     │  Route   │  Trip    │  Schedule          │
│ Discovery │ Discovery│ Planning │  Lookup            │
├──────────┴──────────┴──────────┴────────────────────┤
│              Geospatial Services                     │
├─────────────────────────────────────────────────────┤
│              Data Ingestion Pipeline                 │
├─────────────────────────────────────────────────────┤
│          GTFS / Structured Data Sources              │
└─────────────────────────────────────────────────────┘
```

- **UI ↔ LLM**: Natural language in, natural language out. No structured data crosses this boundary.
- **LLM ↔ Tool Layer**: The LLM only sees tool definitions and results. It should never directly access data stores.
- **Tool Layer ↔ Services**: Structured request/response contracts. Services are agnostic to the conversational context.
- **Services ↔ Data Sources**: Query-only access. All writes happen through the ingestion pipeline.

## External Dependencies

- **LLM Provider**: External API for NLU and response generation
- **Geocoding Service**: For place name to coordinate resolution
- **GTFS Data Providers**: Municipal or provincial transportation agencies
- **Geospatial Data Provider**: OpenStreetMap or commercial alternative
- **Infrastructure Hosting**: Cloud provider for service deployment

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| GTFS data quality or availability is poor for target city | High | Research phase first; establish data quality thresholds; consider manual data curation |
| LLM hallucinates transportation information | High | Strict tool-based architecture; LLM never answers from knowledge; response validation layer |
| Geocoding accuracy insufficient for colloquial place names | Medium | Support multiple geocoding backends; maintain point-of-interest database for common landmarks |
| Latency from multi-hop LLM tool calls degrades UX | Medium | Optimize tool design for minimal round trips; consider streaming responses |
| GTFS data becomes stale | Medium | Scheduled refresh pipeline with alerting on failures |
| API cost of LLM calls at scale | Low (MVP) | Caching strategy; input/output token optimization; model selection |

## Assumptions

- GTFS data is available for the target MVP city (either officially or via community curation)
- Users have internet connectivity during usage
- Geolocation permission is available from users who want proximity-based features
- The target city's transportation network is representable via GTFS semantics
- The LLM provider API is available and meets latency requirements
- A single LLM call per user query is sufficient for intent extraction and response generation (with tool callbacks counted separately)

## Scalability Considerations (MVP)

- Tool services are designed as stateless to enable horizontal scaling
- GTFS data is read-heavy; write throughput is limited to ingestion pipeline
- Geospatial queries should use indexed data structures for sub-second lookups
- LLM costs scale linearly with usage; cost monitoring should be implemented from day one
- The architecture supports adding new cities by onboarding their GTFS feeds and geospatial data — no architectural changes required
- For MVP, a monolithic service deployment is acceptable; services can be split as needed
