FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "\
  python -c \"\
import time, sys; \
from sqlalchemy import create_engine; \
url = '${DATABASE_URL_SYNC}' or '${DATABASE_URL}'; \
if 'postgresql' in url: \
  for i in range(30): \
    try: \
      e = create_engine(url.replace('+asyncpg','').replace('+psycopg2','')); \
      e.connect(); \
      print('DB ready after', i*2, 's'); \
      break; \
    except Exception as ex: \
      if i==29: print('DB timeout:', ex); \
      else: print(f'Waiting for DB... ({i+1}/30)'); time.sleep(2); \
\" 2>&1; \
  python seed_data.py 2>/dev/null || true; \
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000" ]
