"""
Advanced alerting system for Customer Solution Snapshot Generator.

This module provides comprehensive alerting capabilities including multiple notification
channels, alert aggregation, escalation policies, and integration with external systems.
"""

import os
import sys
import json
import time
import logging
import smtplib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import queue

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..utils.config import Config
from .system_monitor import Alert

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"


@dataclass
class NotificationConfig:
    """Configuration for a notification channel."""
    channel: NotificationChannel
    enabled: bool
    config: Dict[str, Any]
    severity_filter: List[AlertSeverity]


@dataclass
class EscalationRule:
    """Alert escalation rule."""
    name: str
    condition: str  # time_based, retry_count, severity
    threshold: Any  # time in minutes, retry count, or severity level
    action: str  # escalate, notify_different_channel, suppress
    target: Optional[str] = None  # target for escalation


@dataclass
class AlertNotification:
    """Alert notification record."""
    alert_id: str
    channel: NotificationChannel
    recipient: str
    status: str  # sent, failed, pending
    timestamp: str
    response: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class EmailNotifier:
    """Email notification handler."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email', 'alerts@example.com')
        self.use_tls = config.get('use_tls', True)
    
    def send_notification(self, alert: Alert, recipients: List[str]) -> List[AlertNotification]:
        """Send email notification for alert."""
        notifications = []
        
        for recipient in recipients:
            try:
                # Create email message
                msg = MIMEMultipart()
                msg['From'] = self.from_email
                msg['To'] = recipient
                msg['Subject'] = f"[{alert.level}] Customer Snapshot Alert: {alert.name}"
                
                # Create email body
                body = self._create_email_body(alert)
                msg.attach(MIMEText(body, 'html'))
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    
                    server.send_message(msg)
                
                notifications.append(AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.EMAIL,
                    recipient=recipient,
                    status="sent",
                    timestamp=datetime.now().isoformat()
                ))
                
                logger.info(f"Email alert sent to {recipient}")
                
            except Exception as e:
                logger.error(f"Failed to send email to {recipient}: {e}")
                notifications.append(AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.EMAIL,
                    recipient=recipient,
                    status="failed",
                    timestamp=datetime.now().isoformat(),
                    error=str(e)
                ))
        
        return notifications
    
    def _create_email_body(self, alert: Alert) -> str:
        """Create HTML email body for alert."""
        severity_colors = {
            "INFO": "#17a2b8",
            "WARNING": "#ffc107", 
            "CRITICAL": "#dc3545",
            "EMERGENCY": "#6f42c1"
        }
        
        color = severity_colors.get(alert.level, "#6c757d")
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .alert-box {{ border-left: 4px solid {color}; padding: 15px; background-color: #f8f9fa; }}
                .alert-header {{ font-size: 18px; font-weight: bold; color: {color}; margin-bottom: 10px; }}
                .alert-details {{ margin: 10px 0; }}
                .alert-timestamp {{ font-size: 12px; color: #6c757d; }}
                .details-table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
                .details-table th, .details-table td {{ border: 1px solid #dee2e6; padding: 8px; text-align: left; }}
                .details-table th {{ background-color: #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="alert-header">[{alert.level}] {alert.name}</div>
                <div class="alert-details">
                    <strong>Message:</strong> {alert.message}<br>
                    <strong>Timestamp:</strong> {alert.timestamp}<br>
                    <strong>Status:</strong> {'Resolved' if alert.resolved else 'Active'}
                </div>
                
                {self._format_alert_details_table(alert.details)}
                
                <div class="alert-timestamp">
                    Generated by Customer Solution Snapshot Generator Monitoring System
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_alert_details_table(self, details: Dict[str, Any]) -> str:
        """Format alert details as HTML table."""
        if not details:
            return ""
        
        rows = []
        for key, value in details.items():
            if isinstance(value, dict):
                value = json.dumps(value, indent=2)
            elif isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            
            rows.append(f"<tr><th>{key}</th><td>{value}</td></tr>")
        
        return f"""
        <table class="details-table">
            <thead>
                <tr><th>Property</th><th>Value</th></tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """


class SlackNotifier:
    """Slack notification handler."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#alerts')
        self.username = config.get('username', 'Customer Snapshot Monitor')
        self.icon_emoji = config.get('icon_emoji', ':warning:')
    
    def send_notification(self, alert: Alert, recipients: List[str] = None) -> List[AlertNotification]:
        """Send Slack notification for alert."""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available for Slack notifications")
            return []
        
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return []
        
        try:
            # Create Slack message
            message = self._create_slack_message(alert)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
                return [AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.SLACK,
                    recipient=self.channel,
                    status="sent",
                    timestamp=datetime.now().isoformat(),
                    response=str(response.status_code)
                )]
            else:
                error_msg = f"Slack API returned status {response.status_code}"
                logger.error(error_msg)
                return [AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.SLACK,
                    recipient=self.channel,
                    status="failed",
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )]
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return [AlertNotification(
                alert_id=alert.name,
                channel=NotificationChannel.SLACK,
                recipient=self.channel,
                status="failed",
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )]
    
    def _create_slack_message(self, alert: Alert) -> Dict[str, Any]:
        """Create Slack message payload for alert."""
        severity_colors = {
            "INFO": "#17a2b8",
            "WARNING": "#ffc107",
            "CRITICAL": "#dc3545", 
            "EMERGENCY": "#6f42c1"
        }
        
        color = severity_colors.get(alert.level, "#6c757d")
        
        # Create attachment with alert details
        attachment = {
            "color": color,
            "title": f"[{alert.level}] {alert.name}",
            "text": alert.message,
            "fields": [
                {
                    "title": "Timestamp",
                    "value": alert.timestamp,
                    "short": True
                },
                {
                    "title": "Status", 
                    "value": "Resolved" if alert.resolved else "Active",
                    "short": True
                }
            ],
            "footer": "Customer Snapshot Monitor",
            "ts": int(datetime.now().timestamp())
        }
        
        # Add alert details as fields
        if alert.details:
            for key, value in alert.details.items():
                if len(attachment["fields"]) < 10:  # Slack limit
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    
                    attachment["fields"].append({
                        "title": key.replace("_", " ").title(),
                        "value": str(value),
                        "short": True
                    })
        
        return {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [attachment]
        }


class WebhookNotifier:
    """Generic webhook notification handler."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get('url')
        self.method = config.get('method', 'POST')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.timeout = config.get('timeout', 10)
    
    def send_notification(self, alert: Alert, recipients: List[str] = None) -> List[AlertNotification]:
        """Send webhook notification for alert."""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available for webhook notifications")
            return []
        
        if not self.url:
            logger.error("Webhook URL not configured")
            return []
        
        try:
            # Create webhook payload
            payload = {
                "alert": asdict(alert),
                "timestamp": datetime.now().isoformat(),
                "source": "customer_snapshot_generator"
            }
            
            # Send webhook
            response = requests.request(
                method=self.method,
                url=self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if 200 <= response.status_code < 300:
                logger.info(f"Webhook alert sent successfully to {self.url}")
                return [AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.WEBHOOK,
                    recipient=self.url,
                    status="sent",
                    timestamp=datetime.now().isoformat(),
                    response=str(response.status_code)
                )]
            else:
                error_msg = f"Webhook returned status {response.status_code}"
                logger.error(error_msg)
                return [AlertNotification(
                    alert_id=alert.name,
                    channel=NotificationChannel.WEBHOOK,
                    recipient=self.url,
                    status="failed",
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )]
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return [AlertNotification(
                alert_id=alert.name,
                channel=NotificationChannel.WEBHOOK,
                recipient=self.url,
                status="failed",
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )]


class AlertAggregator:
    """Aggregates and deduplicates alerts."""
    
    def __init__(self):
        self.alert_cache = {}
        self.aggregation_window = 300  # 5 minutes
        self.max_cache_size = 1000
    
    def should_send_alert(self, alert: Alert) -> bool:
        """Determine if alert should be sent based on aggregation rules."""
        cache_key = f"{alert.name}:{alert.level}"
        current_time = datetime.now()
        
        # Check if we've seen this alert recently
        if cache_key in self.alert_cache:
            last_sent = datetime.fromisoformat(self.alert_cache[cache_key]['last_sent'])
            time_diff = (current_time - last_sent).total_seconds()
            
            # If within aggregation window, increment count but don't send
            if time_diff < self.aggregation_window:
                self.alert_cache[cache_key]['count'] += 1
                self.alert_cache[cache_key]['last_seen'] = current_time.isoformat()
                return False
        
        # Send alert and update cache
        self.alert_cache[cache_key] = {
            'count': 1,
            'last_sent': current_time.isoformat(),
            'last_seen': current_time.isoformat(),
            'first_seen': current_time.isoformat()
        }
        
        # Cleanup old cache entries
        self._cleanup_cache()
        
        return True
    
    def _cleanup_cache(self):
        """Remove old entries from cache."""
        if len(self.alert_cache) <= self.max_cache_size:
            return
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.aggregation_window * 2)
        
        keys_to_remove = []
        for key, data in self.alert_cache.items():
            last_seen = datetime.fromisoformat(data['last_seen'])
            if last_seen < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.alert_cache[key]


class AlertingService:
    """Main alerting service coordinator."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.notification_configs = self._load_notification_configs()
        self.escalation_rules = self._load_escalation_rules()
        self.aggregator = AlertAggregator()
        
        # Initialize notifiers
        self.notifiers = {}
        self._initialize_notifiers()
        
        # Alert processing
        self.alert_queue = queue.Queue()
        self.processing_enabled = False
        self.processor_thread = None
        
        # Notification history
        self.notifications = []
        self.max_notifications = 10000
    
    def _load_notification_configs(self) -> List[NotificationConfig]:
        """Load notification configurations."""
        configs = []
        
        # Email configuration
        if hasattr(self.config, 'email_alerts') and self.config.email_alerts:
            email_config = getattr(self.config, 'email_config', {})
            configs.append(NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=email_config.get('enabled', False),
                config=email_config,
                severity_filter=[AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            ))
        
        # Slack configuration
        if hasattr(self.config, 'slack_alerts') and self.config.slack_alerts:
            slack_config = getattr(self.config, 'slack_config', {})
            configs.append(NotificationConfig(
                channel=NotificationChannel.SLACK,
                enabled=slack_config.get('enabled', False),
                config=slack_config,
                severity_filter=[AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            ))
        
        # Webhook configuration
        if hasattr(self.config, 'webhook_alerts') and self.config.webhook_alerts:
            webhook_config = getattr(self.config, 'webhook_config', {})
            configs.append(NotificationConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=webhook_config.get('enabled', False),
                config=webhook_config,
                severity_filter=[AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            ))
        
        return configs
    
    def _load_escalation_rules(self) -> List[EscalationRule]:
        """Load escalation rules."""
        return [
            EscalationRule(
                name="critical_escalation",
                condition="time_based",
                threshold=15,  # 15 minutes
                action="escalate",
                target="emergency"
            ),
            EscalationRule(
                name="repeated_warnings",
                condition="retry_count",
                threshold=5,
                action="escalate",
                target="critical"
            )
        ]
    
    def _initialize_notifiers(self):
        """Initialize notification handlers."""
        for config in self.notification_configs:
            if not config.enabled:
                continue
            
            try:
                if config.channel == NotificationChannel.EMAIL:
                    self.notifiers[NotificationChannel.EMAIL] = EmailNotifier(config.config)
                elif config.channel == NotificationChannel.SLACK:
                    self.notifiers[NotificationChannel.SLACK] = SlackNotifier(config.config)
                elif config.channel == NotificationChannel.WEBHOOK:
                    self.notifiers[NotificationChannel.WEBHOOK] = WebhookNotifier(config.config)
                
                logger.info(f"Initialized {config.channel.value} notifier")
                
            except Exception as e:
                logger.error(f"Failed to initialize {config.channel.value} notifier: {e}")
    
    def start(self):
        """Start alert processing service."""
        self.processing_enabled = True
        self.processor_thread = threading.Thread(target=self._process_alerts)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        logger.info("Alerting service started")
    
    def stop(self):
        """Stop alert processing service."""
        self.processing_enabled = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        logger.info("Alerting service stopped")
    
    def send_alert(self, alert: Alert):
        """Queue alert for processing."""
        self.alert_queue.put(alert)
    
    def _process_alerts(self):
        """Main alert processing loop."""
        while self.processing_enabled:
            try:
                # Get alert from queue with timeout
                try:
                    alert = self.alert_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Check if alert should be sent (aggregation)
                if not self.aggregator.should_send_alert(alert):
                    logger.debug(f"Alert {alert.name} suppressed by aggregation")
                    continue
                
                # Process alert through notifiers
                self._send_notifications(alert)
                
                # Mark queue task as done
                self.alert_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for alert."""
        alert_severity = AlertSeverity(alert.level.lower())
        
        for config in self.notification_configs:
            if not config.enabled:
                continue
            
            # Check severity filter
            if alert_severity not in config.severity_filter:
                continue
            
            # Get notifier
            notifier = self.notifiers.get(config.channel)
            if not notifier:
                continue
            
            try:
                # Send notification
                recipients = config.config.get('recipients', [])
                notifications = notifier.send_notification(alert, recipients)
                
                # Store notification records
                self.notifications.extend(notifications)
                
                # Limit notification history
                if len(self.notifications) > self.max_notifications:
                    self.notifications = self.notifications[-self.max_notifications:]
                
            except Exception as e:
                logger.error(f"Failed to send {config.channel.value} notification: {e}")
    
    def get_notification_status(self) -> Dict[str, Any]:
        """Get notification service status."""
        recent_notifications = [
            n for n in self.notifications
            if datetime.fromisoformat(n.timestamp) > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "processing_enabled": self.processing_enabled,
            "queue_size": self.alert_queue.qsize(),
            "total_notifications": len(self.notifications),
            "recent_notifications": len(recent_notifications),
            "active_notifiers": list(self.notifiers.keys()),
            "notification_configs": len(self.notification_configs)
        }