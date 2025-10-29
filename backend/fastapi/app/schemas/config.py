"""
VELOX-N8N Configuration Schemas
Pydantic models for configuration API validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConfigType(str, Enum):
    """Configuration type enumeration"""
    SYSTEM = "system"
    USER = "user"
    TRADING = "trading"
    STRATEGY = "strategy"
    RISK = "risk"
    NOTIFICATION = "notification"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"


class ConfigScope(str, Enum):
    """Configuration scope enumeration"""
    GLOBAL = "global"
    USER = "user"
    STRATEGY = "strategy"
    SYSTEM = "system"


class ConfigFormat(str, Enum):
    """Configuration format enumeration"""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    ENV = "env"


class ConfigCategory(BaseModel):
    """Configuration category schema"""
    name: str = Field(..., description="Category name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Category description")
    icon: Optional[str] = Field(None, description="Category icon")
    order: int = Field(0, description="Display order")


class ConfigItem(BaseModel):
    """Configuration item schema"""
    key: str = Field(..., description="Configuration key")
    value: Any = Field(..., description="Configuration value")
    type: str = Field(..., description="Value type (string, number, boolean, array, object)")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Item description")
    category: str = Field(..., description="Configuration category")
    scope: ConfigScope = Field(..., description="Configuration scope")
    is_sensitive: bool = Field(False, description="Whether value is sensitive")
    is_required: bool = Field(False, description="Whether value is required")
    is_readonly: bool = Field(False, description="Whether value is read-only")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    default_value: Optional[Any] = Field(None, description="Default value")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Available options")
    order: int = Field(0, description="Display order")
    
    @validator('value')
    def validate_value(cls, v, values):
        """Validate value based on type and validation rules"""
        value_type = values.get('type')
        validation_rules = values.get('validation')
        
        # Type validation
        if value_type == 'string':
            if not isinstance(v, str):
                raise ValueError('Value must be a string')
        elif value_type == 'number':
            if not isinstance(v, (int, float)):
                raise ValueError('Value must be a number')
        elif value_type == 'boolean':
            if not isinstance(v, bool):
                raise ValueError('Value must be a boolean')
        elif value_type == 'array':
            if not isinstance(v, list):
                raise ValueError('Value must be an array')
        elif value_type == 'object':
            if not isinstance(v, dict):
                raise ValueError('Value must be an object')
        
        # Custom validation rules
        if validation_rules:
            if 'min' in validation_rules and isinstance(v, (int, float)):
                if v < validation_rules['min']:
                    raise ValueError(f"Value must be at least {validation_rules['min']}")
            
            if 'max' in validation_rules and isinstance(v, (int, float)):
                if v > validation_rules['max']:
                    raise ValueError(f"Value must be at most {validation_rules['max']}")
            
            if 'pattern' in validation_rules and isinstance(v, str):
                import re
                pattern = validation_rules['pattern']
                if not re.match(pattern, v):
                    raise ValueError(f"Value must match pattern {pattern}")
            
            if 'enum' in validation_rules:
                if v not in validation_rules['enum']:
                    raise ValueError(f"Value must be one of {validation_rules['enum']}")
        
        return v


class ConfigCreate(BaseModel):
    """Configuration creation schema"""
    key: str = Field(..., description="Configuration key")
    value: Any = Field(..., description="Configuration value")
    scope: ConfigScope = Field(..., description="Configuration scope")
    user_id: Optional[int] = Field(None, description="User ID (for user scope)")
    strategy_id: Optional[int] = Field(None, description="Strategy ID (for strategy scope)")


class ConfigUpdate(BaseModel):
    """Configuration update schema"""
    value: Any = Field(..., description="New configuration value")


class ConfigResponse(BaseModel):
    """Configuration response schema"""
    key: str
    value: Any
    type: str
    display_name: str
    description: str
    category: str
    scope: ConfigScope
    is_sensitive: bool
    is_required: bool
    is_readonly: bool
    validation: Optional[Dict[str, Any]]
    default_value: Optional[Any]
    options: Optional[List[Dict[str, Any]]]
    order: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConfigExportRequest(BaseModel):
    """Configuration export request schema"""
    scope: Optional[ConfigScope] = Field(None, description="Filter by scope")
    category: Optional[str] = Field(None, description="Filter by category")
    format: ConfigFormat = Field(ConfigFormat.JSON, description="Export format")
    include_sensitive: bool = Field(False, description="Include sensitive values")
    user_id: Optional[int] = Field(None, description="User ID (for user scope)")
    strategy_id: Optional[int] = Field(None, description="Strategy ID (for strategy scope)")


class ConfigImportRequest(BaseModel):
    """Configuration import request schema"""
    config_data: Dict[str, Any] = Field(..., description="Configuration data")
    scope: ConfigScope = Field(..., description="Configuration scope")
    merge_strategy: str = Field("replace", description="Merge strategy (replace, merge)")
    user_id: Optional[int] = Field(None, description="User ID (for user scope)")
    strategy_id: Optional[int] = Field(None, description="Strategy ID (for strategy scope)")
    
    @validator('merge_strategy')
    def validate_merge_strategy(cls, v):
        """Validate merge strategy"""
        if v not in ['replace', 'merge']:
            raise ValueError('Merge strategy must be either "replace" or "merge"')
        return v


class ConfigBackupRequest(BaseModel):
    """Configuration backup request schema"""
    name: str = Field(..., description="Backup name")
    description: Optional[str] = Field(None, description="Backup description")
    scope: Optional[ConfigScope] = Field(None, description="Filter by scope")
    include_sensitive: bool = Field(False, description="Include sensitive values")
    user_id: Optional[int] = Field(None, description="User ID (for user scope)")
    strategy_id: Optional[int] = Field(None, description="Strategy ID (for strategy scope)")


class ConfigBackupResponse(BaseModel):
    """Configuration backup response schema"""
    id: int
    uuid: str
    name: str
    description: Optional[str]
    scope: ConfigScope
    file_path: str
    file_size: int
    file_hash: str
    item_count: int
    created_at: datetime
    expires_at: Optional[datetime]
    is_expired: bool
    
    class Config:
        from_attributes = True


class ConfigRestoreRequest(BaseModel):
    """Configuration restore request schema"""
    backup_id: int = Field(..., description="Backup ID")
    merge_strategy: str = Field("replace", description="Merge strategy (replace, merge)")
    
    @validator('merge_strategy')
    def validate_merge_strategy(cls, v):
        """Validate merge strategy"""
        if v not in ['replace', 'merge']:
            raise ValueError('Merge strategy must be either "replace" or "merge"')
        return v


class ConfigValidationRequest(BaseModel):
    """Configuration validation request schema"""
    config_data: Dict[str, Any] = Field(..., description="Configuration data to validate")
    scope: ConfigScope = Field(..., description="Configuration scope")


class ConfigValidationResponse(BaseModel):
    """Configuration validation response schema"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    validated_at: datetime
    
    class Config:
        from_attributes = True


class ConfigHistoryRequest(BaseModel):
    """Configuration history request schema"""
    key: Optional[str] = Field(None, description="Filter by configuration key")
    scope: Optional[ConfigScope] = Field(None, description="Filter by scope")
    category: Optional[str] = Field(None, description="Filter by category")
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    strategy_id: Optional[int] = Field(None, description="Filter by strategy ID")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class ConfigHistoryResponse(BaseModel):
    """Configuration history response schema"""
    id: int
    key: str
    old_value: Any
    new_value: Any
    scope: ConfigScope
    user_id: Optional[int]
    strategy_id: Optional[int]
    changed_by: int
    changed_at: datetime
    reason: Optional[str]
    
    class Config:
        from_attributes = True


class ConfigTemplate(BaseModel):
    """Configuration template schema"""
    id: int
    name: str
    display_name: str
    description: str
    category: str
    scope: ConfigScope
    template_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConfigSearchRequest(BaseModel):
    """Configuration search request schema"""
    query: str = Field(..., min_length=2, max_length=100, description="Search query")
    scope: Optional[ConfigScope] = Field(None, description="Filter by scope")
    category: Optional[str] = Field(None, description="Filter by category")
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    strategy_id: Optional[int] = Field(None, description="Filter by strategy ID")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class ConfigStats(BaseModel):
    """Configuration statistics schema"""
    total_configs: int
    configs_by_scope: Dict[str, int]
    configs_by_category: Dict[str, int]
    sensitive_configs: int
    readonly_configs: int
    last_updated: datetime
    most_updated_category: str
    backup_count: int
    total_backups_size: int
    
    class Config:
        from_attributes = True


class ConfigNotification(BaseModel):
    """Configuration notification schema"""
    id: int
    config_key: str
    notification_type: str
    message: str
    user_id: Optional[int]
    strategy_id: Optional[int]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True