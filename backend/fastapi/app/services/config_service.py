
"""
VELOX-N8N Configuration Service
Business logic for configuration management
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import logging
import uuid
import json
import os
import yaml

from app.core.database import get_db
from app.models.user import User
from app.models.strategy import Strategy
from app.schemas.config import (
    ConfigCreate, ConfigUpdate, ConfigResponse, ConfigExportRequest,
    ConfigImportRequest, ConfigBackupRequest, ConfigBackupResponse,
    ConfigRestoreRequest, ConfigValidationRequest, ConfigValidationResponse,
    ConfigHistoryRequest, ConfigHistoryResponse, ConfigTemplate,
    ConfigSearchRequest, ConfigStats, ConfigNotification,
    ConfigType, ConfigScope, ConfigFormat
)
from app.core.logging import log_api_request, log_error
from app.core.security import generate_api_key

logger = logging.getLogger(__name__)


class ConfigurationService:
    """Service for configuration management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_dir = "/app/config"
        self.backup_dir = "/app/backups"
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def get_config(self, key: str, scope: ConfigScope, user_id: Optional[int] = None, 
                      strategy_id: Optional[int] = None) -> Optional[ConfigResponse]:
        """Get configuration value by key"""
        try:
            # Determine config file path based on scope
            config_file = self._get_config_file_path(scope, user_id, strategy_id)
            
            # Load configuration
            config_data = self._load_config_file(config_file)
            
            if not config_data or key not in config_data:
                logger.warning(f"Configuration key '{key}' not found")
                return None
            
            # Get configuration item
            config_item = config_data[key]
            
            # Get metadata
            metadata = self._get_config_metadata(key, scope)
            
            return ConfigResponse(
                key=key,
                value=config_item.get('value'),
                type=config_item.get('type', 'string'),
                display_name=metadata.get('display_name', key),
                description=metadata.get('description', ''),
                category=metadata.get('category', 'general'),
                scope=scope,
                is_sensitive=metadata.get('is_sensitive', False),
                is_required=metadata.get('is_required', False),
                is_readonly=metadata.get('is_readonly', False),
                validation=metadata.get('validation'),
                default_value=metadata.get('default_value'),
                options=metadata.get('options'),
                order=metadata.get('order', 0),
                created_at=config_item.get('created_at'),
                updated_at=config_item.get('updated_at')
            )
            
        except Exception as e:
            logger.error(f"Error getting config key '{key}': {e}")
            return None
    
    async def set_config(self, config_data: ConfigCreate, user_id: Optional[int] = None,
                      strategy_id: Optional[int] = None) -> Optional[ConfigResponse]:
        """Set configuration value"""
        try:
            # Validate permissions
            if scope == ConfigScope.USER and not user_id:
                raise ValueError("User ID is required for user scope")
            
            if scope == ConfigScope.STRATEGY and not strategy_id:
                raise ValueError("Strategy ID is required for strategy scope")
            
            # Get current config
            config_file = self._get_config_file_path(config_data.scope, user_id, strategy_id)
            current_config = self._load_config_file(config_file) or {}
            
            # Get metadata
            metadata = self._get_config_metadata(config_data.key, config_data.scope)
            
            # Validate value
            validation_rules = metadata.get('validation')
            if validation_rules:
                self._validate_config_value(config_data.value, validation_rules)
            
            # Update configuration
            current_config[config_data.key] = {
                'value': config_data.value,
                'type': metadata.get('type', 'string'),
                'updated_at': datetime.utcnow()
            }
            
            # Save configuration
            self._save_config_file(config_file, current_config)
            
            # Log configuration change
            await self._log_config_change(
                config_data.key, 
                current_config.get(config_data.key, {}).get('value'),
                config_data.value,
                config_data.scope,
                user_id,
                strategy_id
            )
            
            # Return updated configuration
            return await self.get_config(config_data.key, config_data.scope, user_id, strategy_id)
            
        except Exception as e:
            logger.error(f"Error setting config key '{config_data.key}': {e}")
            raise
    
    async def update_config(self, key: str, config_update: ConfigUpdate, scope: ConfigScope,
                        user_id: Optional[int] = None, strategy_id: Optional[int] = None) -> Optional[ConfigResponse]:
        """Update configuration value"""
        try:
            # Create config data
            config_data = ConfigCreate(
                key=key,
                value=config_update.value,
                scope=scope,
                user_id=user_id,
                strategy_id=strategy_id
            )
            
            # Update configuration
            return await self.set_config(config_data, user_id, strategy_id)
            
        except Exception as e:
            logger.error(f"Error updating config key '{key}': {e}")
            raise
    
    async def delete_config(self, key: str, scope: ConfigScope, user_id: Optional[int] = None,
                        strategy_id: Optional[int] = None) -> bool:
        """Delete configuration key"""
        try:
            # Get current config
            config_file = self._get_config_file_path(scope, user_id, strategy_id)
            current_config = self._load_config_file(config_file) or {}
            
            # Check if key exists
            if key not in current_config:
                logger.warning(f"Configuration key '{key}' not found")
                return False
            
            # Get old value for logging
            old_value = current_config[key].get('value')
            
            # Delete key
            del current_config[key]
            
            # Save configuration
            self._save_config_file(config_file, current_config)
            
            # Log configuration change
            await self._log_config_change(
                key, old_value, None, scope, user_id, strategy_id
            )
            
            logger.info(f"Deleted config key '{key}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting config key '{key}': {e}")
            return False
    
    async def list_configs(self, scope: Optional[ConfigScope] = None, category: Optional[str] = None,
                        user_id: Optional[int] = None, strategy_id: Optional[int] = None) -> List[ConfigResponse]:
        """List configuration keys"""
        try:
            # Get all config files for scope
            config_files = self._get_config_files(scope, user_id, strategy_id)
            
            configs = []
            
            for config_file in config_files:
                # Load configuration
                config_data = self._load_config_file(config_file) or {}
                
                # Get metadata for all keys
                for key, value in config_data.items():
                    metadata = self._get_config_metadata(key, scope)
                    
                    configs.append(ConfigResponse(
                        key=key,
                        value=value.get('value'),
                        type=value.get('type', 'string'),
                        display_name=metadata.get('display_name', key),
                        description=metadata.get('description', ''),
                        category=metadata.get('category', 'general'),
                        scope=scope,
                        is_sensitive=metadata.get('is_sensitive', False),
                        is_required=metadata.get('is_required', False),
                        is_readonly=metadata.get('is_readonly', False),
                        validation=metadata.get('validation'),
                        default_value=metadata.get('default_value'),
                        options=metadata.get('options'),
                        order=metadata.get('order', 0),
                        created_at=value.get('created_at'),
                        updated_at=value.get('updated_at')
                    ))
            
            # Filter by category if specified
            if category:
                configs = [c for c in configs if c.category == category]
            
            # Sort by order
            configs.sort(key=lambda c: c.order)
            
            return configs
            
        except Exception as e:
            logger.error(f"Error listing configs: {e}")
            return []
    
    async def export_config(self, request: ConfigExportRequest, user_id: Optional[int] = None,
                       strategy_id: Optional[int] = None) -> Dict[str, Any]:
        """Export configuration"""
        try:
            # Get all configs for scope
            configs = await self.list_configs(request.scope, None, user_id, strategy_id)
            
            # Filter by category if specified
            if request.category:
                configs = [c for c in configs if c.category == request.category]
            
            # Filter sensitive values if requested
            if not request.include_sensitive:
                configs = [c for c in configs if not c.is_sensitive]
            
            # Convert to dictionary
            config_dict = {c.key: c.value for c in configs}
            
            # Format based on requested format
            if request.format == ConfigFormat.JSON:
                return config_dict
            elif request.format == ConfigFormat.YAML:
                return yaml.dump(config_dict, default_flow_style=False)
            elif request.format == ConfigFormat.XML:
                # Simple XML conversion
                xml_data = ['<config>']
                for key, value in config_dict.items():
                    xml_data.append(f'  <{key}>{value}</{key}>')
                xml_data.append('</config>')
                return '\n'.join(xml_data)
            else:
                raise ValueError(f"Unsupported export format: {request.format}")
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            raise
    
    async def import_config(self, request: ConfigImportRequest, user_id: Optional[int] = None,
                       strategy_id: Optional[int] = None) -> Dict[str, Any]:
        """Import configuration"""
        try:
            # Get current config
            config_file = self._get_config_file_path(request.scope, user_id, strategy_id)
            current_config = self._load_config_file(config_file) or {}
            
            # Merge or replace based on strategy
            if request.merge_strategy == "replace":
                new_config = request.config_data
            else:  # merge
                new_config = {**current_config, **request.config_data}
            
            # Validate imported configuration
            validation_result = await self.validate_config(
                ConfigValidationRequest(config_data=new_config, scope=request.scope)
            )
            
            if not validation_result.is_valid:
                raise ValueError(f"Invalid configuration: {', '.join(validation_result.errors)}")
            
            # Save configuration
            self._save_config_file(config_file, new_config)
            
            # Log import
            logger.info(f"Imported configuration for scope {request.scope}")
            
            return {
                "imported_keys": list(request.config_data.keys()),
                "validation_result": validation_result.dict()
            }
            
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            raise
    
    async def backup_config(self, request: ConfigBackupRequest, user_id: Optional[int] = None,
                        strategy_id: Optional[int] = None) -> ConfigBackupResponse:
        """Backup configuration"""
        try:
            # Get all configs for scope
            configs = await self.list_configs(request.scope, None, user_id, strategy_id)
            
            # Filter sensitive values if requested
            if not request.include_sensitive:
                configs = [c for c in configs if not c.is_sensitive]
            
            # Convert to dictionary
            config_dict = {c.key: c.value for c in configs}
            
            # Generate backup file
            backup_id = f"BACKUP_{uuid.uuid4().hex[:12].upper()}"
            backup_filename = f"{backup_id}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Save backup
            with open(backup_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(backup_path)
            file_size = os.path.getsize(backup_path)
            
            # Create backup record
            backup_response = ConfigBackupResponse(
                id=0,  # Would be saved to database
                uuid=backup_id,
                name=request.name,
                description=request.description,
                scope=request.scope,
                file_path=backup_path,
                file_size=file_size,
                file_hash=file_hash,
                item_count=len(config_dict),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),  # 30 days
                is_expired=False
            )
            
            logger.info(f"Created backup {backup_id} with {len(config_dict)} items")
            return backup_response
            
        except Exception as e:
            logger.error(f"Error backing up config: {e}")
            raise
    
    async def restore_config(self, request: ConfigRestoreRequest, user_id: Optional[int] = None,
                        strategy_id: Optional[int] = None) -> Dict[str, Any]:
        """Restore configuration from backup"""
        try:
            # Get backup file path
            backup_path = os.path.join(self.backup_dir, f"{request.backup_id}.json")
            
            # Check if backup exists
            if not os.path.exists(backup_path):
                raise ValueError(f"Backup {request.backup_id} not found")
            
            # Load backup
            with open(backup_path, 'r') as f:
                backup_config = json.load(f)
            
            # Get current config
            config_file = self._get_config_file_path(ConfigScope.GLOBAL, user_id, strategy_id)
            current_config = self._load_config_file(config_file) or {}
            
            # Merge or replace based on strategy
            if request.merge_strategy == "replace":
                new_config = backup_config
            else:  # merge
                new_config = {**current_config, **backup_config}
            
            # Validate restored configuration
            validation_result = await self.validate_config(
                ConfigValidationRequest(config_data=new_config, scope=ConfigScope.GLOBAL)
            )
            
            if not validation_result.is_valid:
                raise ValueError(f"Invalid configuration: {', '.join(validation_result.errors)}")
            
            # Save configuration
            self._save_config_file(config_file, new_config)
            
            # Log restore
            logger.info(f"Restored configuration from backup {request.backup_id}")
            
            return {
                "restored_keys": list(backup_config.keys()),
