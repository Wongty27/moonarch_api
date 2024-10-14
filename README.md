# Backend stacks used for Moonarch website
- FastAPI for building REST API
- PostgreSQL as SQL database
- sqlalchemy as SQL ORM
 - pytest / pytest-asyncio / unittest for testing [Optional]

## Instruction
- schemas: pydantic model
- models: sqlalchemy table
- routers: api functions
- dependencies: reusable functions
- data: for testing and production
- core: config and security stuff (to be discussed)
- test: test script if necessary
- services/utils: business logic if applicable
- main.py: launch app
- app/main.py: fastapi app to include middleware, routers
- requirements.txt: List of packages / libraries required for this project