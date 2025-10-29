"""
VELOX-N8N Audit Model
Database model for audit logging and compliance tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class AuditEventType(str, enum.Enum):
    """Audit event type enumeration"""
    # User events
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_REGISTER = "USER_REGISTER"
    USER_PASSWORD_CHANGE = "USER_PASSWORD_CHANGE"
    USER_PROFILE_UPDATE = "USER_PROFILE_UPDATE"
    USER_API_KEY_GENERATE = "USER_API_KEY_GENERATE"
    USER_API_KEY_REVOKE = "USER_API_KEY_REVOKE"
    
    # Trading events
    ORDER_PLACED = "ORDER_PLACED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_MODIFIED = "ORDER_MODIFIED"
    ORDER_FILLED = "ORDER_FILLED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    POSITION_MODIFIED = "POSITION_MODIFIED"
    
    # Strategy events
    STRATEGY_CREATED = "STRATEGY_CREATED"
    STRATEGY_UPDATED = "STRATEGY_UPDATED"
    STRATEGY_DELETED = "STRATEGY_DELETED"
    STRATEGY_STARTED = "STRATEGY_STARTED"
    STRATEGY_STOPPED = "STRATEGY_STOPPED"
    STRATEGY_BACKTESTED = "STRATEGY_BACKTESTED"
    
    # System events
    SYSTEM_LOGIN = "SYSTEM_LOGIN"
    SYSTEM_LOGOUT = "SYSTEM_LOGOUT"
    SYSTEM_CONFIG_CHANGE = "SYSTEM_CONFIG_CHANGE"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    SYSTEM_WARNING = "SYSTEM_WARNING"
    
    # Security events
    SECURITY_BREACH = "SECURITY_BREACH"
    SECURITY_ALERT = "SECURITY_ALERT"
    FAILED_LOGIN = "FAILED_LOGIN"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    
    # Data events
    DATA_ACCESS = "DATA_ACCESS"
    DATA_EXPORT = "DATA_EXPORT"
    DATA_IMPORT = "DATA_IMPORT"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    DATA_DELETION = "DATA_DELETION"
    
    # API events
    API_ACCESS = "API_ACCESS"
    API_ERROR = "API_ERROR"
    API_RATE_LIMIT = "API_RATE_LIMIT"
    API_UNAUTHORIZED = "API_UNAUTHORIZED"


class AuditSeverity(str, enum.Enum):
    """Audit severity enumeration"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AuditLog(Base):
    """
    Audit log model for tracking all system events
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Event information
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(30), nullable=False, index=True)  # USER, TRADING, STRATEGY, SYSTEM, SECURITY, DATA, API
    severity = Column(String(20), nullable=False, index=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(50), nullable=True, index=True)
    user_role = Column(String(20), nullable=True)
    
    # Session information
    session_id = Column(String(100), nullable=True)
    session_token = Column(String(255), nullable=True)
    
    # Request information
    request_id = Column(String(100), nullable=True, index=True)
    request_method = Column(String(10), nullable=True)
    request_endpoint = Column(String(255), nullable=True)
    request_ip = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    
    # Event details
    event_description = Column(Text, nullable=False)
    event_details = Column(JSON, nullable=True)  # Detailed event data
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values for updates
    
    # Resource information
    resource_type = Column(String(50), nullable=True, index=True)  # USER, STRATEGY, ORDER, etc.
    resource_id = Column(String(100), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)
    
    # Status and outcome
    status = Column(String(20), nullable=False, index=True)  # SUCCESS, FAILURE, PENDING
    outcome = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Performance metrics
    duration_ms = Column(Integer, nullable=True)  # Event duration in milliseconds
    response_size = Column(Integer, nullable=True)  # Response size in bytes
    
    # Risk and compliance
    risk_score = Column(Float, nullable=True)  # Risk score (0-100)
    compliance_flags = Column(JSON, nullable=True)  # Compliance flags
    regulatory_impact = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # Event tags
    metadata = Column(JSON, nullable=True)  # Additional metadata
    source = Column(String(50), nullable=True)  # Event source (WEB, API, SYSTEM, etc.)
    
    # Timestamps
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for performance
    __table_args__ = (
        {'schema': 'public'}  # Explicit schema
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id}, timestamp={self.timestamp})>"
    
    @property
    def is_critical(self) -> bool:
        """Check if event is critical"""
        return self.severity == AuditSeverity.CRITICAL.value
    
    @property
    def is_high_severity(self) -> bool:
        """Check if event is high severity"""
        return self.severity in [AuditSeverity.CRITICAL.value, AuditSeverity.HIGH.value]
    
    @property
    def is_security_event(self) -> bool:
        """Check if event is security related"""
        return self.event_category == 'SECURITY'
    
    @property
    def is_trading_event(self) -> bool:
        """Check if event is trading related"""
        return self.event_category == 'TRADING'
    
    @property
    def is_user_event(self) -> bool:
        """Check if event is user related"""
        return self.event_category == 'USER'
    
    @property
    def is_failure(self) -> bool:
        """Check if event resulted in failure"""
        return self.status == 'FAILURE'
    
    @property
    def is_success(self) -> bool:
        """Check if event resulted in success"""
        return self.status == 'SUCCESS'
    
    @property
    def display_severity(self) -> str:
        """Get display severity name"""
        severity_map = {
            'CRITICAL': 'Critical',
            'HIGH': 'High',
            'MEDIUM': 'Medium',
            'LOW': 'Low',
            'INFO': 'Info'
        }
        return severity_map.get(self.severity, self.severity)
    
    @property
    def display_category(self) -> str:
        """Get display category name"""
        category_map = {
            'USER': 'User',
            'TRADING': 'Trading',
            'STRATEGY': 'Strategy',
            'SYSTEM': 'System',
            'SECURITY': 'Security',
            'DATA': 'Data',
            'API': 'API'
        }
        return category_map.get(self.event_category, self.event_category)
    
    @property
    def display_status(self) -> str:
        """Get display status name"""
        status_map = {
            'SUCCESS': 'Success',
            'FAILURE': 'Failure',
            'PENDING': 'Pending'
        }
        return status_map.get(self.status, self.status)
    
    def calculate_risk_score(self) -> float:
        """Calculate risk score based on event properties"""
        base_score = 0
        
        # Base score by severity
        severity_scores = {
            'CRITICAL': 80,
            'HIGH': 60,
            'MEDIUM': 40,
            'LOW': 20,
            'INFO': 10
        }
        base_score = severity_scores.get(self.severity, 10)
        
        # Adjust by event type
        high_risk_events = [
            'SECURITY_BREACH', 'ACCOUNT_LOCKED', 'SUSPICIOUS_ACTIVITY',
            'ORDER_CANCELLED', 'POSITION_CLOSED', 'SYSTEM_ERROR'
        ]
        if self.event_type in high_risk_events:
            base_score += 20
        
        # Adjust by failure status
        if self.is_failure:
            base_score += 15
        
        # Adjust by regulatory impact
        if self.regulatory_impact:
            base_score += 25
        
        # Cap at 100
        return min(100, base_score)
    
    def to_dict(self, include_details: bool = True) -> dict:
        """Convert audit log to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'event_type': self.event_type,
            'event_category': self.event_category,
            'display_category': self.display_category,
            'severity': self.severity,
            'display_severity': self.display_severity,
            'user_id': self.user_id,
            'username': self.username,
            'user_role': self.user_role,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'request_method': self.request_method,
            'request_endpoint': self.request_endpoint,
            'request_ip': self.request_ip,
            'user_agent': self.user_agent,
            'event_description': self.event_description,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'status': self.status,
            'display_status': self.display_status,
            'outcome': self.outcome,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'duration_ms': self.duration_ms,
            'response_size': self.response_size,
            'risk_score': self.risk_score or self.calculate_risk_score(),
            'compliance_flags': self.compliance_flags,
            'regulatory_impact': self.regulatory_impact,
            'tags': self.tags,
            'metadata': self.metadata,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_critical': self.is_critical,
            'is_high_severity': self.is_high_severity,
            'is_security_event': self.is_security_event,
            'is_trading_event': self.is_trading_event,
            'is_user_event': self.is_user_event,
            'is_failure': self.is_failure,
            'is_success': self.is_success
        }
        
        if include_details:
            data.update({
                'event_details': self.event_details,
                'old_values': self.old_values,
                'new_values': self.new_values
            })
        
        return data


class SystemLog(Base):
    """
    System log model for application and system events
    """
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Log information
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger_name = Column(String(100), nullable=False, index=True)
    module = Column(String(100), nullable=True, index=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # Message and details
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Exception information
    exception_type = Column(String(100), nullable=True)
    exception_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Context information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    correlation_id = Column(String(100), nullable=True)
    
    # System information
    hostname = Column(String(100), nullable=True)
    process_id = Column(Integer, nullable=True)
    thread_id = Column(String(50), nullable=True)
    
    # Performance information
    duration_ms = Column(Integer, nullable=True)
    memory_usage = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', logger='{self.logger_name}', timestamp={self.timestamp})>"
    
    @property
    def is_error(self) -> bool:
        """Check if log is error level"""
        return self.level in ['ERROR', 'CRITICAL']
    
    @property
    def is_warning(self) -> bool:
        """Check if log is warning level"""
        return self.level == 'WARNING'
    
    @property
    def is_info(self) -> bool:
        """Check if log is info level"""
        return self.level == 'INFO'
    
    @property
    def is_debug(self) -> bool:
        """Check if log is debug level"""
        return self.level == 'DEBUG'
    
    @property
    def has_exception(self) -> bool:
        """Check if log has exception information"""
        return self.exception_type is not None
    
    def to_dict(self, include_stack_trace: bool = False) -> dict:
        """Convert system log to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'level': self.level,
            'logger_name': self.logger_name,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'message': self.message,
            'details': self.details,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'correlation_id': self.correlation_id,
            'hostname': self.hostname,
            'process_id': self.process_id,
            'thread_id': self.thread_id,
            'duration_ms': self.duration_ms,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'tags': self.tags,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_error': self.is_error,
            'is_warning': self.is_warning,
            'is_info': self.is_info,
            'is_debug': self.is_debug,
            'has_exception': self.has_exception
        }
        
        if include_stack_trace:
            data['stack_trace'] = self.stack_trace
        
        return data


class ComplianceReport(Base):
    """
    Compliance report model for regulatory reporting
    """
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Report information
    report_type = Column(String(50), nullable=False, index=True)
    report_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Report period
    period_start = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    period_end = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # Report status
    status = Column(String(20), nullable=False, index=True)  # PENDING, GENERATING, COMPLETED, FAILED
    generated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Report content
    report_data = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Compliance metrics
    total_events = Column(Integer, nullable=False, default=0)
    critical_events = Column(Integer, nullable=False, default=0)
    high_risk_events = Column(Integer, nullable=False, default=0)
    compliance_score = Column(Float, nullable=True)
    
    # Review information
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    approved = Column(Boolean, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship("User")
    
    def __repr__(self):
        return f"<ComplianceReport(id={self.id}, type='{self.report_type}', period='{self.period_start}' to '{self.period_end}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if report is completed"""
        return self.status == 'COMPLETED'
    
    @property
    def is_pending(self) -> bool:
        """Check if report is pending"""
        return self.status in ['PENDING', 'GENERATING']
    
    @property
    def is_failed(self) -> bool:
        """Check if report generation failed"""
        return self.status == 'FAILED'
    
    @property
    def is_approved(self) -> bool:
        """Check if report is approved"""
        return self.approved is True
    
    @property
    def is_rejected(self) -> bool:
        """Check if report is rejected"""
        return self.approved is False
    
    @property
    def period_days(self) -> int:
        """Calculate period duration in days"""
        return (self.period_end - self.period_start).days
    
    def calculate_compliance_score(self) -> float:
        """Calculate compliance score"""
        if self.total_events == 0:
            return 100.0
        
        # Weight critical and high-risk events more heavily
        weighted_events = (
            self.critical_events * 10 +
            self.high_risk_events * 5 +
            (self.total_events - self.critical_events - self.high_risk_events) * 1
        )
        
        max_weighted_events = self.total_events * 10
        if max_weighted_events == 0:
            return 100.0
        
        return max(0, 100 - (weighted_events / max_weighted_events * 100))
    
    def to_dict(self) -> dict:
        """Convert compliance report to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'report_type': self.report_type,
            'report_name': self.report_name,
            'description': self.description,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'status': self.status,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'report_data': self.report_data,
            'summary': self.summary,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'total_events': self.total_events,
            'critical_events': self.critical_events,
            'high_risk_events': self.high_risk_events,
            'compliance_score': self.compliance_score or self.calculate_compliance_score(),
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'approved': self.approved,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_completed': self.is_completed,
            'is_pending': self.is_pending,
            'is_failed': self.is_failed,
            'is_approved': self.is_approved,
            'is_rejected': self.is_rejected,
            'period_days': self.period_days
        }