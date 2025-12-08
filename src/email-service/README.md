# Email Service

A production-ready, Kafka-based email service for sending transactional emails in the PicASpot application.

## Features

- ✅ **Kafka Integration**: Consumes email events from Kafka topics
- ✅ **Retry Logic**: Automatic retry with exponential backoff
- ✅ **Health Monitoring**: Built-in health checks and metrics tracking
- ✅ **Graceful Shutdown**: Proper cleanup on service termination
- ✅ **Template Support**: HTML email templates with Jinja2
- ✅ **Production Ready**: Comprehensive logging and error handling
- ✅ **Scalable**: Can run multiple instances for high availability
- ✅ **Industry Standards**: Following best practices and design patterns

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Backend   │ ──────> │    Kafka    │ ──────> │   Email     │
│   Service   │ Events  │   Cluster   │ Topics  │   Service   │
└─────────────┘         └─────────────┘         └─────────────┘
                                                       │
                                                       ▼
                                                 ┌─────────────┐
                                                 │ SMTP Server │
                                                 └─────────────┘
```

## Email Types Supported

1. **Verification Email**: Sent when users register
2. **Password Reset Email**: Sent when users request password reset

## Configuration

The service is configured via environment variables:

### Required Variables

```env
# SMTP Configuration
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_HOST=smtp.example.com
SMTP_PORT=587
EMAIL_FROM_NAME=PicASpot
PROJECT_NAME=PicASpot

# Kafka Configuration (with defaults)
KAFKA_BOOTSTRAP_SERVERS=kafka-0:9092,kafka-1:9092,kafka-2:9092
KAFKA_EMAIL_TOPIC=email-events
KAFKA_CONSUMER_GROUP=email-service-group
```

### Optional Variables

```env
# Service Configuration
SERVICE_NAME=email-service
VERSION=1.0.0
DEBUG=false

# Email Retry Settings
EMAIL_MAX_RETRIES=3
EMAIL_RETRY_DELAY_SECONDS=5

# Kafka Advanced Settings
KAFKA_MAX_POLL_RECORDS=100
KAFKA_SESSION_TIMEOUT_MS=30000
KAFKA_HEARTBEAT_INTERVAL_MS=10000
KAFKA_MAX_POLL_INTERVAL_MS=300000
KAFKA_AUTO_OFFSET_RESET=earliest
```

## Running the Service

### With Docker Compose

The service is automatically started with the main application:

```bash
docker-compose up email-service
```

### Development Mode

```bash
cd src/email-service
uv sync
uv run python -m app.main
```

Or directly:

```bash
uv run python -m app.consumer
```

## Email Templates

Templates are located in `app/templates/` and use Jinja2 syntax:

- `base_email.html` - Base template with common styles
- `verify.html` - Email verification template
- `password_reset.html` - Password reset template

### Adding New Templates

1. Create a new HTML file in `app/templates/`
2. Extend `base_email.html` if needed
3. Add corresponding handler in `email_manager.py`
4. Update `EmailType` enum in `schemas.py`

## Monitoring

### Health Checks

The service logs health statistics every 60 seconds:

```
Health check - Uptime: 3600s | Processed: 150 | Failed: 2 | Emails sent: 148
```

### Metrics Tracked

- Messages processed
- Messages failed
- Emails sent successfully
- Emails failed
- Emails retried
- Service uptime

### Logs

Logs are written to:
- Console (stdout)
- `logs/email-service.log` - All logs
- `logs/email-service-error.log` - Error logs only

## Error Handling

The service implements robust error handling:

1. **Validation Errors**: Invalid messages are logged and skipped
2. **SMTP Errors**: Automatic retry with configurable attempts
3. **Kafka Errors**: Connection retry with backoff
4. **Network Errors**: Handled gracefully with retries

## Scaling

To scale the service:

1. **Horizontal Scaling**: Run multiple instances (Docker replicas)
2. **Consumer Groups**: All instances share the same consumer group
3. **Partition Distribution**: Kafka distributes partitions among instances

```yaml
email-service:
  deploy:
    replicas: 3
```

## Message Format

Email events sent to Kafka must follow this format:

```json
{
  "email_type": "verification",
  "recipient": "user@example.com",
  "username": "john_doe",
  "link": "https://example.com/verify/token",
  "timestamp": "2025-12-08T10:30:00",
  "metadata": {}
}
```

## Development

### Project Structure

```
email-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── consumer.py          # Kafka consumer
│   ├── email_manager.py     # Email sending logic
│   ├── schemas.py           # Data models
│   ├── settings.py          # Configuration
│   ├── logging_config.py    # Logging setup
│   └── templates/           # Email templates
├── logs/                    # Log files
├── Dockerfile
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
uv run pytest tests/
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy app/
```

## Troubleshooting

### Consumer Not Connecting to Kafka

1. Check Kafka is running: `docker-compose ps kafka-0`
2. Verify `KAFKA_BOOTSTRAP_SERVERS` is correct
3. Check network connectivity: `docker-compose logs email-service`

### Emails Not Being Sent

1. Verify SMTP credentials are correct
2. Check SMTP server is reachable
3. Review logs in `logs/email-service-error.log`
4. Test SMTP connection manually

### High Memory Usage

1. Reduce `KAFKA_MAX_POLL_RECORDS`
2. Increase `KAFKA_MAX_POLL_INTERVAL_MS`
3. Check for memory leaks in logs

## Best Practices

✅ **Use environment variables** for all configuration  
✅ **Monitor logs** regularly for errors  
✅ **Set up alerts** for failed emails  
✅ **Test email templates** before deployment  
✅ **Use staging environment** for testing  
✅ **Keep templates up to date** with branding  
✅ **Monitor Kafka lag** to ensure timely delivery  
✅ **Set appropriate retry limits** to avoid spam  

## Security Considerations

- Store SMTP credentials securely (use secrets management)
- Use TLS/SSL for SMTP connections (configure in production)
- Validate all input data
- Sanitize user data in templates
- Rate limit email sending if needed
- Monitor for suspicious activity

## Performance

- Processes up to 100 messages per poll
- Configurable batch sizes
- Automatic retry with backoff
- Multiple instances for high throughput
- Efficient template caching

## License

This service is part of the PicASpot project.

## Support

For issues or questions:
1. Check the logs first
2. Review this documentation
3. Contact the development team
4. Create an issue in the project repository

