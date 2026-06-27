app/
├── endpoints/      # FastAPI
├── services/       # Toda la lógica del negocio
│   ├── transport/
│   ├── mcp/
│   ├── llm/
│   ├── gtfs/
│   ├── routing/
│   └── geocoding/
├── repositories/   # Acceso a datos
├── models/         # ORM, aca viven las entidades de SQLAlchemy
├── schemas/        # Pydantic
├── jobs/           # Procesos asíncronos
├── config/         # Configuración
├── utils/          # Utilidades compartidas
└── app.py