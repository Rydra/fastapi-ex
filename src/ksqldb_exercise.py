from ksql import KSQLAPI

# KSQL_SERVER_URL = 'http://ksql-server:8088'
from ksql.errors import KSQLError

KSQL_SERVER_URL = 'http://localhost:8088'

client = KSQLAPI(KSQL_SERVER_URL)

query = client.query("""
SELECT * FROM riderLocations
  WHERE GEO_DISTANCE(latitude, longitude, 37.4133, -122.1162) <= 5
""", use_http2=True)

for item in query: print(item)
