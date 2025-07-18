from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph
from models import db  # Import your models here

# Create a temporary in-memory SQLite database
engine = create_engine('sqlite:///:memory:')

# Create all tables from models.py in the temporary DB
db.metadata.create_all(engine)

# Generate the schema graph
graph = create_schema_graph(
    engine=engine,
    metadata=db.metadata,
    show_datatypes=False,
    show_indexes=False,
    rankdir='LR',
    concentrate=False
)

# Save to file
graph.write_png('schema_diagram.png')
print("✅ Schema diagram saved as 'schema_diagram.png'")
