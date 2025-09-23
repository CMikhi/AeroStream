# Docker Deployment Guide

This guide explains how to deploy the IgniteDemoRepo backend using Docker for long-term hosting.

## Quick Start

### Development Deployment
```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment (with Nginx)
```bash
# Run with nginx reverse proxy
docker-compose --profile production up -d

# Stop services
docker-compose --profile production down
```

## Manual Docker Commands

### Build the Image
```bash
docker build -t ignite-backend .
```

### Run Container
```bash
docker run -d \
  --name ignite-backend \
  -p 8000:8000 \
  -v ignite_data:/app/data \
  ignite-backend
```

## Configuration

### Environment Variables
- `PORT`: Application port (default: 8000)
- `DATABASE_PATH`: Path to SQLite database (default: /app/data/database.db)
- `PYTHONPATH`: Python path (default: /app)

### Docker Compose Override
Create a `docker-compose.override.yml` file to customize settings:

```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=1
      - LOG_LEVEL=debug
    ports:
      - "8080:8000"  # Change port mapping
```

## Persistent Data

The database is stored in a Docker volume (`database_data`) to persist data between container restarts. The database is automatically initialized on first run.

### Backup Database
```bash
# Copy database from container
docker cp $(docker-compose ps -q backend):/app/data/database.db ./backup.db
```

### Restore Database
```bash
# Copy database to container
docker cp ./backup.db $(docker-compose ps -q backend):/app/data/database.db
docker-compose restart backend
```

## Production Considerations

### Security
1. **Change JWT Secret**: Update `SECRET_KEY` in `backend.py`
2. **Use HTTPS**: Configure SSL certificates in nginx
3. **Firewall**: Restrict access to necessary ports only
4. **Regular Updates**: Keep base images updated

### Performance
1. **Resource Limits**: Add memory and CPU limits in docker-compose
2. **Scaling**: Use multiple backend instances with load balancer
3. **Database**: Consider migrating to PostgreSQL for production

### Monitoring
1. **Health Checks**: Built-in health check endpoint at `/`
2. **Logs**: Centralize logs using Docker logging drivers
3. **Metrics**: Add Prometheus metrics for monitoring

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Debug container
docker-compose exec backend /bin/bash
```

### Database Issues
```bash
# Check database permissions
docker-compose exec backend ls -la /app/data/

# Reset database (WARNING: deletes all data)
docker-compose down
docker volume rm ignitedemo_database_data
docker-compose up -d
```

### Network Issues
```bash
# Check if port is accessible
curl http://localhost:8000/

# Check container networking
docker-compose exec backend netstat -tlnp
```

## API Access

Once running, the API will be available at:
- **Development**: http://localhost:8000
- **Production**: http://your-domain.com (with nginx)

### Key Endpoints
- `GET /`: Health check
- `POST /register`: User registration
- `POST /login`: User authentication
- `GET /test`: WebSocket test page
- `WS /ws/{room_name}`: WebSocket connection

## SSL Configuration (Production)

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `./ssl/` directory
3. Update `nginx.conf` with your domain name
4. Uncomment HTTPS server block in nginx.conf
5. Run with production profile: `docker-compose --profile production up -d`

## Scaling

For high-traffic deployments:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Migration
If database schema changes are needed, create migration scripts and run them before starting the application.