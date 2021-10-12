from Uptime import uptime_monitor
import config

if __name__ == '__main__':
    monitor = uptime_monitor.UptimeMonitor(config.SITES, config.WEBHOOK_ENDPOINT)
    