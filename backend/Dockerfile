FROM python:3.11

WORKDIR /src

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"

COPY requirements.txt ./

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY ./alembic ./alembic
COPY alembic.ini .
COPY ./db ./db
COPY ./app ./app



EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]