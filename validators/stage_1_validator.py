#!/usr/bin/env python3
"""
Stage 1 Validator - ERD Schema Validation

Validates erd.json structure and content against required specifications.
"""

import json
import sys
from typing import Dict, List, Any, Set
from pathlib import Path


class ERDValidator:
    """Validator for ERD JSON schema"""
    
    VALID_TYPES = {
        "integer", "float", "string", "boolean", 
        "datetime", "json", "array", "text"
    }
    
    VALID_CONSTRAINTS = {
        "primary_key", "auto_increment", "required", "unique",
        "foreign_key", "indexed"
    }
    
    VALID_OPERATIONS = {
        "create", "read", "update", "delete", "list"
    }
    
    VALID_RELATIONSHIP_TYPES = {
        "has_many", "belongs_to", "many_to_many", "has_one"
    }
    
    VALID_GLOBAL_RELATIONSHIP_TYPES = {
        "one_to_many", "many_to_one", "one_to_one", "many_to_many"
    }
    
    VALID_AUTH_METHODS = {
        "session", "token", "oauth", "none"
    }
    
    VALID_COMPLEXITY_LEVELS = {
        "simple", "moderate", "complex"
    }
    
    def __init__(self, erd_path: str):
        self.erd_path = Path(erd_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.erd_data: Dict[str, Any] = {}
        self.entity_names: Set[str] = set()
        
    def validate(self) -> bool:
        """Main validation method"""
        print(f"Validating ERD schema: {self.erd_path}")
        
        if not self._load_erd():
            return False
        
        if not self._validate_schema_structure():
            return False
        
        self._validate_project_info()
        self._validate_entities()
        self._validate_relationships()
        self._validate_frontend_pages()
        self._validate_business_logic()
        self._validate_cross_references()
        
        return self._report_results()
    
    def _validate_schema_structure(self) -> bool:
        """Validate top-level schema structure"""
        required_sections = [
            "project_info",
            "entities", 
            "relationships",
            "frontend_pages",
            "business_logic"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in self.erd_data:
                missing_sections.append(section)
        
        if missing_sections:
            print("\n" + "="*70)
            print("ERROR: INVALID SCHEMA STRUCTURE")
            print("="*70)
            print("✗ ERD schema is missing required top-level sections:")
            for section in missing_sections:
                print(f"    • {section}")
            print("\n  Fix: Add all required sections to your erd.json")
            print(f"\n  Expected schema structure:")
            print("  {")
            for section in required_sections:
                status = "✓" if section not in missing_sections else "✗"
                print(f"    {status} \"{section}\": {{ ... }},")
            print("  }")
            print("="*70)
            return False
        
        print("✓ Schema structure valid")
        return True
    
    def _load_erd(self) -> bool:
        """Load and parse ERD JSON file"""
        if not self.erd_path.exists():
            print("\n" + "="*70)
            print("ERROR: FILE NOT FOUND")
            print("="*70)
            print(f"✗ ERD file does not exist: {self.erd_path}")
            print(f"  Expected location: {self.erd_path.absolute()}")
            print("="*70)
            return False
        
        try:
            with open(self.erd_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    print("\n" + "="*70)
                    print("ERROR: EMPTY FILE")
                    print("="*70)
                    print(f"✗ ERD file is empty: {self.erd_path}")
                    print("="*70)
                    return False
                self.erd_data = json.loads(content)
            print("✓ ERD file loaded successfully")
            return True
        except json.JSONDecodeError as e:
            print("\n" + "="*70)
            print("ERROR: INVALID JSON")
            print("="*70)
            print(f"✗ Failed to parse JSON in: {self.erd_path}")
            print(f"  Line {e.lineno}, Column {e.colno}")
            print(f"  Issue: {e.msg}")
            if e.lineno:
                try:
                    with open(self.erd_path, 'r') as f:
                        lines = f.readlines()
                        if e.lineno <= len(lines):
                            print(f"\n  Problem line:")
                            print(f"  {e.lineno}: {lines[e.lineno-1].rstrip()}")
                            print(f"  {' ' * (len(str(e.lineno)) + e.colno + 1)}^")
                except:
                    pass
            print("\n  Fix: Check for missing commas, quotes, or brackets")
            print("="*70)
            return False
        except Exception as e:
            print("\n" + "="*70)
            print("ERROR: FILE READ FAILED")
            print("="*70)
            print(f"✗ Cannot read ERD file: {self.erd_path}")
            print(f"  Reason: {str(e)}")
            print("="*70)
            return False
    
    def _validate_project_info(self):
        """Validate project_info section"""
        project_info = self.erd_data.get("project_info", {})
        
        # Check required fields
        required_fields = ["name", "total_entities", "entity_complexity"]
        for field in required_fields:
            if field not in project_info:
                self.errors.append(f"project_info: Missing required field '{field}'")
        
        # Validate entity_complexity
        if "entity_complexity" in project_info:
            complexity = project_info["entity_complexity"]
            if complexity not in self.VALID_COMPLEXITY_LEVELS:
                self.errors.append(
                    f"project_info: Invalid entity_complexity '{complexity}' "
                    f"(must be: {', '.join(self.VALID_COMPLEXITY_LEVELS)})"
                )
        
        # Validate total_entities matches actual count
        if "total_entities" in project_info and "entities" in self.erd_data:
            expected = project_info["total_entities"]
            actual = len(self.erd_data["entities"])
            if expected != actual:
                self.errors.append(
                    f"project_info: total_entities mismatch (declared {expected}, found {actual})"
                )
        
        print("✓ project_info validated")
    
    def _validate_entities(self):
        """Validate entities section"""
        entities = self.erd_data.get("entities", [])
        
        if not isinstance(entities, list):
            self.errors.append("entities: Must be an array")
            return
        
        if len(entities) == 0:
            self.errors.append("entities: Array cannot be empty")
            return
        
        for idx, entity in enumerate(entities):
            self._validate_entity(entity, idx)
        
        print(f"✓ {len(entities)} entities validated")
    
    def _validate_entity(self, entity: Dict[str, Any], idx: int):
        """Validate single entity"""
        prefix = f"Entity[{idx}]"
        
        # Check required fields
        if "name" not in entity:
            self.errors.append(f"{prefix}: Missing 'name'")
            return
        
        entity_name = entity["name"]
        self.entity_names.add(entity_name)
        prefix = f"Entity '{entity_name}'"
        
        # Validate name format (PascalCase, singular)
        if not entity_name[0].isupper():
            self.warnings.append(f"{prefix}: Name should be PascalCase")
        
        if entity_name.endswith('s') and entity_name != "Status":
            self.warnings.append(f"{prefix}: Name should be singular")
        
        # Check required fields
        required_fields = ["description", "fields", "operations", "relationships"]
        for field in required_fields:
            if field not in entity:
                self.errors.append(f"{prefix}: Missing '{field}'")
        
        # Validate fields
        if "fields" in entity:
            self._validate_entity_fields(entity["fields"], entity_name)
        
        # Validate operations
        if "operations" in entity:
            self._validate_entity_operations(entity["operations"], entity_name)
        
        # Validate relationships
        if "relationships" in entity:
            self._validate_entity_relationships(entity["relationships"], entity_name)
    
    def _validate_entity_fields(self, fields: Dict[str, Any], entity_name: str):
        """Validate entity fields"""
        if not isinstance(fields, dict):
            self.errors.append(f"Entity '{entity_name}': 'fields' must be an object")
            return
        
        # Check for required default fields
        required_fields = ["id", "createdAt", "updatedAt"]
        for field_name in required_fields:
            if field_name not in fields:
                self.errors.append(
                    f"Entity '{entity_name}': Missing required field '{field_name}'"
                )
        
        # Validate id field
        if "id" in fields:
            id_field = fields["id"]
            if id_field.get("type") != "integer":
                self.errors.append(
                    f"Entity '{entity_name}': 'id' field must be type 'integer'"
                )
            if "primary_key" not in id_field.get("constraints", []):
                self.errors.append(
                    f"Entity '{entity_name}': 'id' field must have 'primary_key' constraint"
                )
        
        # Validate timestamp fields
        for ts_field in ["createdAt", "updatedAt"]:
            if ts_field in fields:
                field = fields[ts_field]
                if field.get("type") != "datetime":
                    self.errors.append(
                        f"Entity '{entity_name}': '{ts_field}' must be type 'datetime'"
                    )
                if "required" not in field.get("constraints", []):
                    self.errors.append(
                        f"Entity '{entity_name}': '{ts_field}' must have 'required' constraint"
                    )
        
        # Validate each field
        for field_name, field_data in fields.items():
            self._validate_field(field_data, entity_name, field_name)
    
    def _validate_field(self, field: Dict[str, Any], entity_name: str, field_name: str):
        """Validate single field"""
        prefix = f"Entity '{entity_name}', field '{field_name}'"
        
        # Check required attributes
        required_attrs = ["type", "constraints", "description"]
        for attr in required_attrs:
            if attr not in field:
                self.errors.append(f"{prefix}: Missing '{attr}'")
        
        # Validate type
        if "type" in field:
            field_type = field["type"]
            if field_type not in self.VALID_TYPES:
                self.errors.append(
                    f"{prefix}: Invalid type '{field_type}'. "
                    f"Must be one of: {self.VALID_TYPES}"
                )
        
        # Validate constraints
        if "constraints" in field:
            constraints = field["constraints"]
            if not isinstance(constraints, list):
                self.errors.append(f"{prefix}: 'constraints' must be an array")
            else:
                for constraint in constraints:
                    # Check for max_length:N pattern
                    if constraint.startswith("max_length:") or constraint.startswith("min_length:"):
                        continue
                    if constraint.startswith("min_value:") or constraint.startswith("max_value:"):
                        continue
                    if constraint not in self.VALID_CONSTRAINTS:
                        self.errors.append(
                            f"{prefix}: Invalid constraint '{constraint}'"
                        )
        
        # Validate description
        if "description" in field:
            if not isinstance(field["description"], str) or not field["description"].strip():
                self.errors.append(f"{prefix}: 'description' must be a non-empty string")
    
    def _validate_entity_operations(self, operations: List[str], entity_name: str):
        """Validate entity operations"""
        if not isinstance(operations, list):
            self.errors.append(
                f"Entity '{entity_name}': 'operations' must be an array"
            )
            return
        
        for operation in operations:
            if operation not in self.VALID_OPERATIONS:
                self.errors.append(
                    f"Entity '{entity_name}': Invalid operation '{operation}'. "
                    f"Must be one of: {self.VALID_OPERATIONS}"
                )
    
    def _validate_entity_relationships(self, relationships: List[Dict[str, Any]], entity_name: str):
        """Validate entity relationships"""
        if not isinstance(relationships, list):
            self.errors.append(
                f"Entity '{entity_name}': 'relationships' must be an array"
            )
            return
        
        for idx, rel in enumerate(relationships):
            prefix = f"Entity '{entity_name}', relationship[{idx}]"
            
            # Check required fields
            required_fields = ["type", "related_entity", "description"]
            for field in required_fields:
                if field not in rel:
                    self.errors.append(f"{prefix}: Missing '{field}'")
            
            # Validate type
            if "type" in rel:
                rel_type = rel["type"]
                if rel_type not in self.VALID_RELATIONSHIP_TYPES:
                    self.errors.append(
                        f"{prefix}: Invalid type '{rel_type}'. "
                        f"Must be one of: {self.VALID_RELATIONSHIP_TYPES}"
                    )
    
    def _validate_relationships(self):
        """Validate global relationships section"""
        relationships = self.erd_data.get("relationships", [])
        
        if not isinstance(relationships, list):
            self.errors.append("relationships: Must be an array")
            return
        
        for idx, rel in enumerate(relationships):
            self._validate_global_relationship(rel, idx)
        
        print(f"✓ {len(relationships)} relationships validated")
    
    def _validate_global_relationship(self, rel: Dict[str, Any], idx: int):
        """Validate single global relationship"""
        prefix = f"relationships[{idx}]"
        
        # Check required fields
        required_fields = ["from_entity", "to_entity", "relationship_type", "foreign_key", "description"]
        for field in required_fields:
            if field not in rel:
                self.errors.append(f"{prefix}: Missing '{field}'")
        
        # Validate relationship type
        if "relationship_type" in rel:
            rel_type = rel["relationship_type"]
            if rel_type not in self.VALID_GLOBAL_RELATIONSHIP_TYPES:
                self.errors.append(
                    f"{prefix}: Invalid relationship_type '{rel_type}' "
                    f"(must be: {', '.join(self.VALID_GLOBAL_RELATIONSHIP_TYPES)})"
                )
        
        # Validate entity references
        if "from_entity" in rel and rel["from_entity"] not in self.entity_names:
            self.errors.append(
                f"{prefix}: from_entity '{rel['from_entity']}' not found in entities"
            )
        
        if "to_entity" in rel and rel["to_entity"] not in self.entity_names:
            self.errors.append(
                f"{prefix}: to_entity '{rel['to_entity']}' not found in entities"
            )
        
        # Validate foreign_key format for many_to_many
        if rel.get("relationship_type") == "many_to_many":
            if "foreign_key" in rel:
                fk = rel["foreign_key"]
                if "," not in fk:
                    self.warnings.append(
                        f"{prefix}: many_to_many foreign_key should be comma-separated (e.g., 'entity1Id, entity2Id')"
                    )
    
    def _validate_frontend_pages(self):
        """Validate frontend_pages section"""
        pages = self.erd_data.get("frontend_pages", [])
        
        if not isinstance(pages, list):
            self.errors.append("frontend_pages: Must be an array")
            return
        
        for idx, page in enumerate(pages):
            self._validate_frontend_page(page, idx)
        
        print(f"✓ {len(pages)} frontend pages validated")
    
    def _validate_frontend_page(self, page: Dict[str, Any], idx: int):
        """Validate single frontend page"""
        prefix = f"Frontend page[{idx}]"
        
        # Check required fields
        required_fields = ["name", "description", "entities_used", "operations"]
        for field in required_fields:
            if field not in page:
                self.errors.append(f"{prefix}: Missing '{field}'")
        
        # Validate entities_used
        if "entities_used" in page:
            entities = page["entities_used"]
            if not isinstance(entities, list):
                self.errors.append(f"{prefix}: 'entities_used' must be an array")
            else:
                for entity_name in entities:
                    if entity_name not in self.entity_names:
                        self.errors.append(
                            f"{prefix}: Referenced entity '{entity_name}' not found"
                        )
        
        # Validate operations
        if "operations" in page:
            operations = page["operations"]
            if not isinstance(operations, list):
                self.errors.append(f"{prefix}: 'operations' must be an array")
            else:
                for operation in operations:
                    if operation not in self.VALID_OPERATIONS:
                        self.errors.append(
                            f"{prefix}: Invalid operation '{operation}'"
                        )
    
    def _validate_business_logic(self):
        """Validate business_logic section"""
        business_logic = self.erd_data.get("business_logic", {})
        
        # Validate authentication
        if "authentication" not in business_logic:
            self.errors.append("business_logic: Missing 'authentication'")
        else:
            self._validate_authentication(business_logic["authentication"])
        
        # Validate authorization
        if "authorization" not in business_logic:
            self.errors.append("business_logic: Missing 'authorization'")
        else:
            self._validate_authorization(business_logic["authorization"])
        
        print("✓ business_logic validated")
    
    def _validate_authentication(self, auth: Dict[str, Any]):
        """Validate authentication configuration"""
        prefix = "authentication"
        
        # Check required fields
        required_fields = ["enabled", "method", "login_fields", "password_requirements"]
        for field in required_fields:
            if field not in auth:
                self.errors.append(f"{prefix}: Missing '{field}'")
        
        # Validate enabled
        if "enabled" in auth and not isinstance(auth["enabled"], bool):
            self.errors.append(f"{prefix}: 'enabled' must be boolean")
        
        # Validate method
        if "method" in auth:
            method = auth["method"]
            if method not in self.VALID_AUTH_METHODS:
                self.errors.append(
                    f"{prefix}: Invalid method '{method}'. "
                    f"Must be one of: {self.VALID_AUTH_METHODS}"
                )
        
        # Validate login_fields
        if "login_fields" in auth:
            if not isinstance(auth["login_fields"], list):
                self.errors.append(f"{prefix}: 'login_fields' must be an array")
        
        # Validate password_requirements
        if "password_requirements" in auth:
            pwd_req = auth["password_requirements"]
            required_pwd_fields = [
                "min_length", "require_uppercase", "require_lowercase",
                "require_numbers", "require_special_chars"
            ]
            for field in required_pwd_fields:
                if field not in pwd_req:
                    self.errors.append(f"{prefix}.password_requirements: Missing '{field}'")
    
    def _validate_authorization(self, authz: Dict[str, Any]):
        """Validate authorization configuration"""
        prefix = "authorization"
        
        # Check required fields
        required_fields = ["role_based", "roles", "permissions", "resource_permissions"]
        for field in required_fields:
            if field not in authz:
                self.errors.append(f"{prefix}: Missing '{field}'")
        
        # Validate role_based
        if "role_based" in authz and not isinstance(authz["role_based"], bool):
            self.errors.append(f"{prefix}: 'role_based' must be boolean")
        
        # Validate roles
        if "roles" in authz:
            if not isinstance(authz["roles"], list):
                self.errors.append(f"{prefix}: 'roles' must be an array")
        
        # Validate permissions
        if "permissions" in authz:
            if not isinstance(authz["permissions"], dict):
                self.errors.append(f"{prefix}: 'permissions' must be an object")
        
        # Validate resource_permissions
        if "resource_permissions" in authz:
            res_perms = authz["resource_permissions"]
            if not isinstance(res_perms, dict):
                self.errors.append(f"{prefix}: 'resource_permissions' must be an object")
            else:
                for entity_name, perms in res_perms.items():
                    if entity_name not in self.entity_names:
                        self.warnings.append(
                            f"{prefix}.resource_permissions: Entity '{entity_name}' not found"
                        )
                    
                    # Validate CRUD permissions
                    for operation in ["create", "read", "update", "delete"]:
                        if operation not in perms:
                            self.warnings.append(
                                f"{prefix}.resource_permissions[{entity_name}]: Missing '{operation}' permission"
                            )
                        elif not isinstance(perms[operation], list):
                            self.errors.append(
                                f"{prefix}.resource_permissions[{entity_name}]: '{operation}' must be an array"
                            )
    
    def _validate_cross_references(self):
        """Validate cross-references between sections"""
        # Check that entities in relationships exist
        if "relationships" in self.erd_data:
            for rel in self.erd_data["relationships"]:
                from_entity = rel.get("from_entity")
                to_entity = rel.get("to_entity")
                
                if from_entity and from_entity not in self.entity_names:
                    self.errors.append(
                        f"Relationship references non-existent entity: {from_entity}"
                    )
                
                if to_entity and to_entity not in self.entity_names:
                    self.errors.append(
                        f"Relationship references non-existent entity: {to_entity}"
                    )
        
        print("✓ Cross-references validated")
    
    def _report_results(self) -> bool:
        """Report validation results"""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        
        if self.warnings:
            print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n✗ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            
            # Print quick summary of error types
            print(f"\n" + "-"*70)
            print("ERROR SUMMARY:")
            print("-"*70)
            
            error_categories = {
                'Missing required': 0,
                'Invalid type': 0,
                'Invalid format': 0,
                'Not found': 0,
                'Other': 0
            }
            
            for error in self.errors:
                if 'Missing' in error:
                    error_categories['Missing required'] += 1
                elif 'Invalid type' in error or 'Invalid constraint' in error or 'Invalid operation' in error:
                    error_categories['Invalid type'] += 1
                elif 'must be' in error or 'should be' in error:
                    error_categories['Invalid format'] += 1
                elif 'not found' in error:
                    error_categories['Not found'] += 1
                else:
                    error_categories['Other'] += 1
            
            for category, count in error_categories.items():
                if count > 0:
                    print(f"  • {category}: {count}")
            
            print("\n" + "="*70)
            print("❌ VALIDATION FAILED")
            print("="*70)
            print("\nAction Required:")
            print("  1. Fix the errors listed above")
            print("  2. Ensure all required fields are present")
            print("  3. Re-run the validator")
            print("="*70)
            return False
        else:
            print("\n✓ All checks passed!")
            if self.warnings:
                print("  Note: Some warnings detected but validation still passes")
            print("\n" + "="*70)
            print("✅ VALIDATION SUCCESSFUL")
            print("="*70)
            return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python stage_1_validator.py <erd.json>")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    
    validator = ERDValidator(erd_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()