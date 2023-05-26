[Up](../README.md)

# Configuration

## Metrics

To send metrics to statsd, you need to add the `statsd` block to the service configuration:

* `debug` - flag to enable statsd debugging, don't enable it in prod environment;
* `host` - hostname where the statsd service is deployed;
* `port` - port of the statsd service.

For example,

```json
"services": {
	"statsd": {
		"debug": false,
		"host": "statsd.example.com",
		"port": 8125
	}
}
```
