# Metrics

Metrics are sent to statsd by the [statsd] library.
To send metrics, you need to execute [service configuration](./Config.ms#metrics).

## List of metrics

All metrics are prefixed with `services.auth.auth.${env}.${id}`,
where `${env}` is the name of the environment (`production`, `development`),
and `${id}` is the application instance ID (positive integer).
