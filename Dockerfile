FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home redgum && mkdir -p /data && chown -R redgum:redgum /app /data
USER redgum
ENV APP_ENV=production APP_DATABASE=/data/redgum.sqlite3
EXPOSE 8080
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "--call", "app:create_app"]

