#!/usr/bin/env python3
"""
Stage 2 Validator - React TypeScript Entity Layer Validator

Validates that all entity files are correctly generated for React TypeScript frontend

CRITICAL VALIDATIONS:
1. Type definitions for all entities
2. Service files with correct operations
3. Create and Update DTOs
4. ES6 import/export style
5. Barrel exports
6. TypeScript interface completeness
7. All imports exist and are valid
8. All imported functions/methods exist
"""

import sys
import os
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_section(title):
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.RESET}")

class Stage2Validator:
    def __init__(self, erd_path: str, openapi_path: str):
        self.erd_path = erd_path
        self.openapi_path = openapi_path
        self.errors = []
        self.warnings = []
        self.entities = []
        self.entity_operations = {}
        self.openapi_entities = set()
        self.base_path = Path("generated_project")
        
        # Track exported symbols from each file
        self.file_exports = {}  # file_path -> set of exported symbols
        self.file_imports = {}  # file_path -> list of (imported_symbols, from_path)
    
    def load_openapi_file(self, file_path: str) -> Optional[dict]:
        """Load OpenAPI file supporting both JSON and YAML formats"""
        # Try JSON first
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass  # Not JSON, try YAML
        
        # Try YAML if JSON failed or doesn't exist
        yaml_path = file_path.replace('.json', '.yaml')
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print_error(f"Error parsing YAML file {yaml_path}: {e}")
                return None
        
        # Try original path as YAML
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            try:
                with open(file_path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print_error(f"Error parsing YAML file {file_path}: {e}")
                return None
        
        return None
        
    def load_inputs(self) -> bool:
        """Load ERD and OpenAPI files"""
        try:
            # Load ERD
            with open(self.erd_path, 'r') as f:
                erd_data = json.load(f)
                self.entities = erd_data.get('entities', [])
                
                # Extract operations per entity
                for entity in self.entities:
                    entity_name = entity.get('name')
                    operations = entity.get('operations', [])
                    self.entity_operations[entity_name] = operations
            
            # Load OpenAPI (JSON or YAML)
            openapi_data = self.load_openapi_file(self.openapi_path)
            if openapi_data is None:
                print_error(f"Failed to load OpenAPI file: {self.openapi_path}")
                return False
            
            paths = openapi_data.get('paths', {})
            
            # Extract entities that have API endpoints
            for path in paths.keys():
                    # Extract entity name from path like /api/users or /api/v1/users
                    match = re.search(r'/api/(?:v\d+/)?(\w+)', path)
                    if match:
                        entity_name = match.group(1)
                        # Convert plural to singular and capitalize
                        if entity_name.endswith('s'):
                            entity_name = entity_name[:-1]
                        entity_name = entity_name[0].upper() + entity_name[1:]
                        self.openapi_entities.add(entity_name)
            
            return True
        except json.JSONDecodeError as e:
            print_error(f"Error parsing JSON: {e}")
            return False
        except Exception as e:
            print_error(f"Error loading inputs: {e}")
            return False
    
    def _scan_file_exports(self, file_path: Path) -> Set[str]:
        """Scan a TypeScript file for exported symbols"""
        exports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Export named items: export interface Foo, export const foo, export function foo
            named_exports = re.findall(r'export\s+(?:interface|type|const|let|var|function|class)\s+(\w+)', content)
            exports.update(named_exports)
            
            # Export declarations: export { Foo, Bar }
            export_declarations = re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
            for decl in export_declarations:
                symbols = [s.strip().split(' as ')[0].strip() for s in decl.split(',')]
                exports.update(symbols)
            
            # Re-exports: export * from './foo'
            if re.search(r'export\s+\*\s+from', content):
                exports.add('*')  # Wildcard export
            
            # Default export
            if re.search(r'export\s+default', content):
                exports.add('default')
        
        except Exception as e:
            pass
        
        return exports
    
    def _resolve_import_path(self, importing_file: Path, import_path: str) -> Optional[Path]:
        """Resolve relative import path to absolute file path"""
        if import_path.startswith('.'):
            # Relative import
            base_dir = importing_file.parent
            resolved = (base_dir / import_path).resolve()
            
            # Try various extensions
            for ext in ['.ts', '.tsx', '.js', '.jsx', '']:
                if ext == '':
                    # Check for index file
                    index_path = resolved / 'index.ts'
                    if index_path.exists():
                        return index_path
                    index_path = resolved / 'index.tsx'
                    if index_path.exists():
                        return index_path
                else:
                    file_with_ext = Path(str(resolved) + ext)
                    if file_with_ext.exists():
                        return file_with_ext
        
        return None
    
    def _scan_file_imports(self, file_path: Path) -> List[Tuple[List[str], str]]:
        """Scan a TypeScript file for imports"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match: import { Foo, Bar } from './path'
            named_imports = re.finditer(r"import\s*\{\s*([^}]+)\s*\}\s*from\s*['\"]([^'\"]+)['\"]", content)
            for match in named_imports:
                symbols_str = match.group(1)
                from_path = match.group(2)
                symbols = [s.strip().split(' as ')[0].strip() for s in symbols_str.split(',')]
                imports.append((symbols, from_path))
            
            # Match: import Foo from './path'
            default_imports = re.finditer(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in default_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
            
            # Match: import * as Foo from './path'
            wildcard_imports = re.finditer(r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in wildcard_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
        
        except Exception as e:
            pass
        
        return imports
    
    def _build_export_map(self):
        """Build a map of all exports in the project"""
        print_info("Building export map...")
        
        src_path = self.base_path / "src"
        if not src_path.exists():
            return
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                exports = self._scan_file_exports(file_path)
                self.file_exports[file_path] = exports
    
    def _build_import_map(self):
        """Build a map of all imports in the project"""
        src_path = self.base_path / "src"
        if not src_path.exists():
            return
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                imports = self._scan_file_imports(file_path)
                self.file_imports[file_path] = imports
    
    def validate_imports(self):
        """Validate all imports are valid and exported symbols exist"""
        print_section("VALIDATING IMPORTS")
        
        self._build_export_map()
        self._build_import_map()
        
        all_valid = True
        import_errors = []
        
        for file_path, imports in self.file_imports.items():
            rel_path = str(file_path.relative_to(self.base_path))
            
            for symbols, from_path in imports:
                # Skip external packages (not relative imports)
                if not from_path.startswith('.'):
                    continue
                
                # Resolve the import path
                resolved_path = self._resolve_import_path(file_path, from_path)
                
                if resolved_path is None:
                    print_error(f"{rel_path}: Import path not found: '{from_path}'")
                    import_errors.append(f"{rel_path}: Missing import file '{from_path}'")
                    all_valid = False
                    continue
                
                # Check if the imported file has exports
                if resolved_path not in self.file_exports:
                    continue
                
                available_exports = self.file_exports[resolved_path]
                
                # If wildcard export, skip individual symbol check
                if '*' in available_exports:
                    continue
                
                # Check each imported symbol exists
                for symbol in symbols:
                    if symbol not in available_exports and 'default' not in available_exports:
                        print_error(f"{rel_path}: Symbol '{symbol}' not exported from '{from_path}'")
                        import_errors.append(f"{rel_path}: Missing symbol '{symbol}' from '{from_path}'")
                        all_valid = False
        
        if all_valid:
            total_imports = sum(len(imports) for imports in self.file_imports.values())
            print_success(f"All {total_imports} imports are valid")
        else:
            print_error(f"Found {len(import_errors)} import errors")
            for error in import_errors[:10]:
                print(f"  {Colors.RED}{error}{Colors.RESET}")
            if len(import_errors) > 10:
                print(f"  ... and {len(import_errors) - 10} more")
            
            self.errors.extend(import_errors)
    
    def validate_type_definitions(self):
        """Validate that all entities have type definitions"""
        print_section("VALIDATING TYPE DEFINITIONS")
        
        types_path = self.base_path / "src" / "types"
        if not types_path.exists():
            print_error("Types directory not found: src/types/")
            self.errors.append("Types directory missing")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            type_file = types_path / f"{entity_name}.types.ts"
            
            if not type_file.exists():
                print_error(f"{entity_name}: Type file not found - {entity_name}.types.ts")
                self.errors.append(f"Missing type file: {entity_name}.types.ts")
                all_valid = False
                continue
            
            # Read type file and validate content
            try:
                with open(type_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for base interface
                base_interface_pattern = rf"export\s+interface\s+{entity_name}\s*\{{"
                if not re.search(base_interface_pattern, content):
                    print_error(f"{entity_name}: Missing base interface '{entity_name}'")
                    self.errors.append(f"{entity_name}: Missing base interface")
                    all_valid = False
                
                # Check for Create DTO
                create_interface_pattern = rf"export\s+interface\s+{entity_name}Create\s*\{{"
                if not re.search(create_interface_pattern, content):
                    print_error(f"{entity_name}: Missing Create DTO '{entity_name}Create'")
                    self.errors.append(f"{entity_name}: Missing Create DTO")
                    all_valid = False
                
                # Check for Update DTO
                update_interface_pattern = rf"export\s+interface\s+{entity_name}Update\s*\{{"
                if not re.search(update_interface_pattern, content):
                    print_error(f"{entity_name}: Missing Update DTO '{entity_name}Update'")
                    self.errors.append(f"{entity_name}: Missing Update DTO")
                    all_valid = False
                
                # Check for Response interface
                response_interface_pattern = rf"export\s+interface\s+{entity_name}Response\s*\{{"
                if not re.search(response_interface_pattern, content):
                    print_warning(f"{entity_name}: Missing Response interface '{entity_name}Response'")
                    self.warnings.append(f"{entity_name}: Missing Response interface")
                
                # Validate fields in base interface
                entity_fields = entity.get('fields', {})
                for field_name in entity_fields.keys():
                    field_pattern = rf"{field_name}\s*[?:]"
                    if not re.search(field_pattern, content):
                        print_warning(f"{entity_name}: Field '{field_name}' not found in type definition")
            
            except Exception as e:
                print_error(f"{entity_name}: Error reading type file - {e}")
                self.errors.append(f"{entity_name}: Error reading type file")
                all_valid = False
        
        if all_valid:
            print_success(f"All {len(self.entities)} entities have complete type definitions")
        else:
            print_error("Some type definitions are missing or incomplete")
    
    def validate_service_files(self):
        """Validate that entities with endpoints have service files"""
        print_section("VALIDATING SERVICE FILES")
        
        services_path = self.base_path / "src" / "services"
        if not services_path.exists():
            print_error("Services directory not found: src/services/")
            self.errors.append("Services directory missing")
            return
        
        all_valid = True
        
        # Check entities that have OpenAPI endpoints
        for entity_name in self.openapi_entities:
            # Convert to camelCase for service file name
            service_name = entity_name[0].lower() + entity_name[1:]
            service_file = services_path / f"{service_name}.service.ts"
            
            if not service_file.exists():
                print_error(f"{entity_name}: Service file not found - {service_name}.service.ts")
                self.errors.append(f"Missing service file: {service_name}.service.ts")
                all_valid = False
                continue
            
            # Validate service content
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for service object export
                service_export_pattern = rf"export\s+const\s+{service_name}Service\s*="
                if not re.search(service_export_pattern, content):
                    print_error(f"{entity_name}: Missing service export '{service_name}Service'")
                    self.errors.append(f"{entity_name}: Missing service export")
                    all_valid = False
                
                # Check for operations based on entity operations
                operations = self.entity_operations.get(entity_name, [])
                operation_methods = {
                    'list': 'getAll',
                    'read': 'getById',
                    'create': 'create',
                    'update': 'update',
                    'delete': 'delete'
                }
                
                for operation in operations:
                    method_name = operation_methods.get(operation)
                    if method_name:
                        method_pattern = rf"{method_name}\s*[:(]"
                        if not re.search(method_pattern, content):
                            print_error(f"{entity_name}: Missing service method '{method_name}' for operation '{operation}'")
                            self.errors.append(f"{entity_name}: Missing method {method_name}")
                            all_valid = False
                
                # Check for type imports
                type_import_pattern = rf"import\s+.*from\s+['\"].*types['\"]"
                if not re.search(type_import_pattern, content):
                    print_warning(f"{entity_name}: Missing type imports")
                    self.warnings.append(f"{entity_name}: Missing type imports in service")
                
                # Check for api import
                api_import_pattern = r"import\s+.*api.*from\s+['\"].*api['\"]"
                if not re.search(api_import_pattern, content):
                    print_error(f"{entity_name}: Missing api import")
                    self.errors.append(f"{entity_name}: Missing api import in service")
                    all_valid = False
            
            except Exception as e:
                print_error(f"{entity_name}: Error reading service file - {e}")
                self.errors.append(f"{entity_name}: Error reading service file")
                all_valid = False
        
        if all_valid:
            print_success(f"All {len(self.openapi_entities)} entities with endpoints have complete service files")
        else:
            print_error("Some service files are missing or incomplete")
    
    def validate_components(self):
        """Validate component generation based on operations"""
        print_section("VALIDATING COMPONENTS")
        
        components_path = self.base_path / "src" / "components"
        if not components_path.exists():
            print_error("Components directory not found: src/components/")
            self.errors.append("Components directory missing")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            operations = entity.get('operations', [])
            
            # Check for List component if 'list' in operations
            if 'list' in operations:
                list_component = components_path / f"{entity_name}List.tsx"
                if not list_component.exists():
                    print_error(f"{entity_name}: List component not found - {entity_name}List.tsx")
                    self.errors.append(f"Missing component: {entity_name}List.tsx")
                    all_valid = False
                else:
                    # Validate component content
                    try:
                        with open(list_component, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for React.FC or function component
                        if not re.search(r"(React\.FC|function\s+\w+|const\s+\w+.*=>)", content):
                            print_error(f"{entity_name}List: Not a valid React component")
                            self.errors.append(f"{entity_name}List: Invalid component structure")
                            all_valid = False
                        
                        # Check for TypeScript types
                        if not re.search(rf"import.*{entity_name}.*from", content):
                            print_warning(f"{entity_name}List: Missing entity type import")
                    except Exception as e:
                        print_error(f"{entity_name}List: Error reading component - {e}")
            
            # Check for Form component if 'create' or 'update' in operations
            if 'create' in operations or 'update' in operations:
                form_component = components_path / f"{entity_name}Form.tsx"
                if not form_component.exists():
                    print_error(f"{entity_name}: Form component not found - {entity_name}Form.tsx")
                    self.errors.append(f"Missing component: {entity_name}Form.tsx")
                    all_valid = False
                else:
                    # Validate component content
                    try:
                        with open(form_component, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for form element
                        if not re.search(r"<form", content):
                            print_warning(f"{entity_name}Form: No form element found")
                        
                        # Check for TypeScript types
                        if not re.search(rf"import.*{entity_name}(Create|Update).*from", content):
                            print_warning(f"{entity_name}Form: Missing Create/Update DTO import")
                    except Exception as e:
                        print_error(f"{entity_name}Form: Error reading component - {e}")
        
        if all_valid:
            print_success("All required components are present")
        else:
            print_error("Some components are missing")
    
    def validate_barrel_exports(self):
        """Validate barrel exports (index.ts files)"""
        print_section("VALIDATING BARREL EXPORTS")
        
        directories_to_check = ['types', 'services', 'components', 'views']
        all_valid = True
        
        for directory in directories_to_check:
            dir_path = self.base_path / "src" / directory
            if not dir_path.exists():
                continue
            
            index_file = dir_path / "index.ts"
            if not index_file.exists():
                print_error(f"{directory}: Missing index.ts barrel export")
                self.errors.append(f"Missing barrel export: {directory}/index.ts")
                all_valid = False
                continue
            
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for ES6 export statements
                if not re.search(r"export\s+.*from", content):
                    print_error(f"{directory}/index.ts: No export statements found")
                    self.errors.append(f"{directory}/index.ts: Missing exports")
                    all_valid = False
                
                # For each entity, check if it's exported
                for entity in self.entities:
                    entity_name = entity.get('name')
                    
                    if directory == 'types':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}\.types['\"]"
                    elif directory == 'services':
                        service_name = entity_name[0].lower() + entity_name[1:]
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{service_name}\.service['\"]"
                    elif directory == 'components':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}(List|Form|Detail)['\"]"
                    elif directory == 'views':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}View['\"]"
                    else:
                        continue
                    
                    if not re.search(export_pattern, content):
                        print_warning(f"{directory}/index.ts: Missing export for {entity_name}")
            
            except Exception as e:
                print_error(f"{directory}/index.ts: Error reading file - {e}")
                self.errors.append(f"{directory}/index.ts: Error reading file")
                all_valid = False
        
        if all_valid:
            print_success("All barrel exports are properly configured")
        else:
            print_error("Some barrel exports are missing or incomplete")
    
    def validate_es6_style(self):
        """Validate ES6 import/export style"""
        print_section("VALIDATING ES6 IMPORT/EXPORT STYLE")
        
        src_path = self.base_path / "src"
        if not src_path.exists():
            print_error("src directory not found")
            return
        
        commonjs_violations = []
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.base_path))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for CommonJS require
                    if re.search(r"=\s*require\s*\(", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'require()'")
                    
                    # Check for CommonJS module.exports
                    if re.search(r"module\.exports\s*=", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'module.exports'")
                
                except Exception as e:
                    pass
        
        if commonjs_violations:
            print_error(f"Found {len(commonjs_violations)} files using CommonJS style")
            for violation in commonjs_violations[:10]:
                print_error(violation)
                print(f"  {Colors.YELLOW}FIX: Use ES6 import/export syntax{Colors.RESET}")
            
            if len(commonjs_violations) > 10:
                print(f"  ... and {len(commonjs_violations) - 10} more")
            
            for violation in commonjs_violations:
                self.errors.append(violation)
        else:
            # Count total files checked
            ts_files = list(src_path.rglob("*.ts")) + list(src_path.rglob("*.tsx"))
            print_success(f"All {len(ts_files)} TypeScript files use ES6 import/export style")
    
    def validate_typescript_interfaces(self):
        """Validate TypeScript interface completeness"""
        print_section("VALIDATING TYPESCRIPT INTERFACES")
        
        types_path = self.base_path / "src" / "types"
        if not types_path.exists():
            print_error("Types directory not found")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            type_file = types_path / f"{entity_name}.types.ts"
            
            if not type_file.exists():
                continue
            
            try:
                with open(type_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check that base interface has all required fields
                entity_fields = entity.get('fields', {})
                base_interface_match = re.search(
                    rf"export\s+interface\s+{entity_name}\s*\{{([^}}]+)\}}",
                    content,
                    re.DOTALL
                )
                
                if base_interface_match:
                    interface_body = base_interface_match.group(1)
                    
                    for field_name, field_info in entity_fields.items():
                        field_type = field_info.get('type')
                        constraints = field_info.get('constraints', [])
                        
                        # Check if field exists in interface
                        field_pattern = rf"{field_name}\s*[?:]"
                        if not re.search(field_pattern, interface_body):
                            print_error(f"{entity_name}: Field '{field_name}' missing in base interface")
                            self.errors.append(f"{entity_name}: Missing field {field_name}")
                            all_valid = False
                        else:
                            # Check if optional marker (?) matches required constraint
                            is_required = 'required' in constraints
                            has_optional = bool(re.search(rf"{field_name}\s*\?:", interface_body))
                            
                            if is_required and has_optional:
                                print_warning(f"{entity_name}: Field '{field_name}' is required but marked optional")
                            elif not is_required and not has_optional and field_name not in ['id', 'createdAt', 'updatedAt']:
                                print_warning(f"{entity_name}: Field '{field_name}' is optional but not marked with '?'")
            
            except Exception as e:
                print_error(f"{entity_name}: Error validating interface - {e}")
                all_valid = False
        
        if all_valid:
            print_success("All TypeScript interfaces are complete")
        else:
            print_error("Some TypeScript interfaces are incomplete")
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_inputs():
            return False
        
        self.validate_type_definitions()
        self.validate_service_files()
        self.validate_components()
        self.validate_barrel_exports()
        self.validate_es6_style()
        self.validate_typescript_interfaces()
        self.validate_imports()
        
        print_section("SUMMARY")
        
        if len(self.errors) > 0:
            print_error(f"Validation FAILED with {len(self.errors)} error(s)")
            if len(self.warnings) > 0:
                print_warning(f"Also found {len(self.warnings)} warning(s)")
            return False
        else:
            print_success("✓ ALL VALIDATIONS PASSED")
            if len(self.warnings) > 0:
                print_warning(f"Found {len(self.warnings)} warning(s)")
            print(f"  Entities: {len(self.entities)}")
            print(f"  Entities with endpoints: {len(self.openapi_entities)}")
            return True

def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_2_validator.py <erd.json> <openapi.json>")
        print_info("Example: python3 validators/stage_2_validator.py output/erd.json output/openapi.json")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage2Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
    
    def validate_type_definitions(self):
        """Validate that all entities have type definitions"""
        print_section("VALIDATING TYPE DEFINITIONS")
        
        types_path = self.base_path / "src" / "types"
        if not types_path.exists():
            print_error("Types directory not found: src/types/")
            self.errors.append("Types directory missing")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            type_file = types_path / f"{entity_name}.types.ts"
            
            if not type_file.exists():
                print_error(f"{entity_name}: Type file not found - {entity_name}.types.ts")
                self.errors.append(f"Missing type file: {entity_name}.types.ts")
                all_valid = False
                continue
            
            # Read type file and validate content
            try:
                with open(type_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for base interface
                base_interface_pattern = rf"export\s+interface\s+{entity_name}\s*\{{"
                if not re.search(base_interface_pattern, content):
                    print_error(f"{entity_name}: Missing base interface '{entity_name}'")
                    self.errors.append(f"{entity_name}: Missing base interface")
                    all_valid = False
                
                # Check for Create DTO
                create_interface_pattern = rf"export\s+interface\s+{entity_name}Create\s*\{{"
                if not re.search(create_interface_pattern, content):
                    print_error(f"{entity_name}: Missing Create DTO '{entity_name}Create'")
                    self.errors.append(f"{entity_name}: Missing Create DTO")
                    all_valid = False
                
                # Check for Update DTO
                update_interface_pattern = rf"export\s+interface\s+{entity_name}Update\s*\{{"
                if not re.search(update_interface_pattern, content):
                    print_error(f"{entity_name}: Missing Update DTO '{entity_name}Update'")
                    self.errors.append(f"{entity_name}: Missing Update DTO")
                    all_valid = False
                
                # Check for Response interface
                response_interface_pattern = rf"export\s+interface\s+{entity_name}Response\s*\{{"
                if not re.search(response_interface_pattern, content):
                    print_warning(f"{entity_name}: Missing Response interface '{entity_name}Response'")
                    self.warnings.append(f"{entity_name}: Missing Response interface")
                
                # Validate fields in base interface
                entity_fields = entity.get('fields', {})
                for field_name in entity_fields.keys():
                    field_pattern = rf"{field_name}\s*[?:]"
                    if not re.search(field_pattern, content):
                        print_warning(f"{entity_name}: Field '{field_name}' not found in type definition")
            
            except Exception as e:
                print_error(f"{entity_name}: Error reading type file - {e}")
                self.errors.append(f"{entity_name}: Error reading type file")
                all_valid = False
        
        if all_valid:
            print_success(f"All {len(self.entities)} entities have complete type definitions")
        else:
            print_error("Some type definitions are missing or incomplete")
    
    def validate_service_files(self):
        """Validate that entities with endpoints have service files"""
        print_section("VALIDATING SERVICE FILES")
        
        services_path = self.base_path / "src" / "services"
        if not services_path.exists():
            print_error("Services directory not found: src/services/")
            self.errors.append("Services directory missing")
            return
        
        all_valid = True
        
        # Check entities that have OpenAPI endpoints
        for entity_name in self.openapi_entities:
            # Convert to camelCase for service file name
            service_name = entity_name[0].lower() + entity_name[1:]
            service_file = services_path / f"{service_name}.service.ts"
            
            if not service_file.exists():
                print_error(f"{entity_name}: Service file not found - {service_name}.service.ts")
                self.errors.append(f"Missing service file: {service_name}.service.ts")
                all_valid = False
                continue
            
            # Validate service content
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for service object export
                service_export_pattern = rf"export\s+const\s+{service_name}Service\s*="
                if not re.search(service_export_pattern, content):
                    print_error(f"{entity_name}: Missing service export '{service_name}Service'")
                    self.errors.append(f"{entity_name}: Missing service export")
                    all_valid = False
                
                # Check for operations based on entity operations
                operations = self.entity_operations.get(entity_name, [])
                operation_methods = {
                    'list': 'getAll',
                    'read': 'getById',
                    'create': 'create',
                    'update': 'update',
                    'delete': 'delete'
                }
                
                for operation in operations:
                    method_name = operation_methods.get(operation)
                    if method_name:
                        method_pattern = rf"{method_name}\s*[:(]"
                        if not re.search(method_pattern, content):
                            print_error(f"{entity_name}: Missing service method '{method_name}' for operation '{operation}'")
                            self.errors.append(f"{entity_name}: Missing method {method_name}")
                            all_valid = False
                
                # Check for type imports
                type_import_pattern = rf"import\s+.*from\s+['\"].*types['\"]"
                if not re.search(type_import_pattern, content):
                    print_warning(f"{entity_name}: Missing type imports")
                    self.warnings.append(f"{entity_name}: Missing type imports in service")
                
                # Check for api import
                api_import_pattern = r"import\s+.*api.*from\s+['\"].*api['\"]"
                if not re.search(api_import_pattern, content):
                    print_error(f"{entity_name}: Missing api import")
                    self.errors.append(f"{entity_name}: Missing api import in service")
                    all_valid = False
            
            except Exception as e:
                print_error(f"{entity_name}: Error reading service file - {e}")
                self.errors.append(f"{entity_name}: Error reading service file")
                all_valid = False
        
        if all_valid:
            print_success(f"All {len(self.openapi_entities)} entities with endpoints have complete service files")
        else:
            print_error("Some service files are missing or incomplete")
    
    def validate_components(self):
        """Validate component generation based on operations"""
        print_section("VALIDATING COMPONENTS")
        
        components_path = self.base_path / "src" / "components"
        if not components_path.exists():
            print_error("Components directory not found: src/components/")
            self.errors.append("Components directory missing")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            operations = entity.get('operations', [])
            
            # Check for List component if 'list' in operations
            if 'list' in operations:
                list_component = components_path / f"{entity_name}List.tsx"
                if not list_component.exists():
                    print_error(f"{entity_name}: List component not found - {entity_name}List.tsx")
                    self.errors.append(f"Missing component: {entity_name}List.tsx")
                    all_valid = False
                else:
                    # Validate component content
                    try:
                        with open(list_component, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for React.FC or function component
                        if not re.search(r"(React\.FC|function\s+\w+|const\s+\w+.*=>)", content):
                            print_error(f"{entity_name}List: Not a valid React component")
                            self.errors.append(f"{entity_name}List: Invalid component structure")
                            all_valid = False
                        
                        # Check for TypeScript types
                        if not re.search(rf"import.*{entity_name}.*from", content):
                            print_warning(f"{entity_name}List: Missing entity type import")
                    except Exception as e:
                        print_error(f"{entity_name}List: Error reading component - {e}")
            
            # Check for Form component if 'create' or 'update' in operations
            if 'create' in operations or 'update' in operations:
                form_component = components_path / f"{entity_name}Form.tsx"
                if not form_component.exists():
                    print_error(f"{entity_name}: Form component not found - {entity_name}Form.tsx")
                    self.errors.append(f"Missing component: {entity_name}Form.tsx")
                    all_valid = False
                else:
                    # Validate component content
                    try:
                        with open(form_component, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for form element
                        if not re.search(r"<form", content):
                            print_warning(f"{entity_name}Form: No form element found")
                        
                        # Check for TypeScript types
                        if not re.search(rf"import.*{entity_name}(Create|Update).*from", content):
                            print_warning(f"{entity_name}Form: Missing Create/Update DTO import")
                    except Exception as e:
                        print_error(f"{entity_name}Form: Error reading component - {e}")
        
        if all_valid:
            print_success("All required components are present")
        else:
            print_error("Some components are missing")
    
    def validate_barrel_exports(self):
        """Validate barrel exports (index.ts files)"""
        print_section("VALIDATING BARREL EXPORTS")
        
        directories_to_check = ['types', 'services', 'components', 'views']
        all_valid = True
        
        for directory in directories_to_check:
            dir_path = self.base_path / "src" / directory
            if not dir_path.exists():
                continue
            
            index_file = dir_path / "index.ts"
            if not index_file.exists():
                print_error(f"{directory}: Missing index.ts barrel export")
                self.errors.append(f"Missing barrel export: {directory}/index.ts")
                all_valid = False
                continue
            
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for ES6 export statements
                if not re.search(r"export\s+.*from", content):
                    print_error(f"{directory}/index.ts: No export statements found")
                    self.errors.append(f"{directory}/index.ts: Missing exports")
                    all_valid = False
                
                # For each entity, check if it's exported
                for entity in self.entities:
                    entity_name = entity.get('name')
                    
                    if directory == 'types':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}\.types['\"]"
                    elif directory == 'services':
                        service_name = entity_name[0].lower() + entity_name[1:]
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{service_name}\.service['\"]"
                    elif directory == 'components':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}(List|Form|Detail)['\"]"
                    elif directory == 'views':
                        export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_name}View['\"]"
                    else:
                        continue
                    
                    if not re.search(export_pattern, content):
                        print_warning(f"{directory}/index.ts: Missing export for {entity_name}")
            
            except Exception as e:
                print_error(f"{directory}/index.ts: Error reading file - {e}")
                self.errors.append(f"{directory}/index.ts: Error reading file")
                all_valid = False
        
        if all_valid:
            print_success("All barrel exports are properly configured")
        else:
            print_error("Some barrel exports are missing or incomplete")
    
    def validate_es6_style(self):
        """Validate ES6 import/export style"""
        print_section("VALIDATING ES6 IMPORT/EXPORT STYLE")
        
        src_path = self.base_path / "src"
        if not src_path.exists():
            print_error("src directory not found")
            return
        
        commonjs_violations = []
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.base_path))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for CommonJS require
                    if re.search(r"=\s*require\s*\(", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'require()'")
                    
                    # Check for CommonJS module.exports
                    if re.search(r"module\.exports\s*=", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'module.exports'")
                
                except Exception as e:
                    pass
        
        if commonjs_violations:
            print_error(f"Found {len(commonjs_violations)} files using CommonJS style")
            for violation in commonjs_violations[:10]:
                print_error(violation)
                print(f"  {Colors.YELLOW}FIX: Use ES6 import/export syntax{Colors.RESET}")
            
            if len(commonjs_violations) > 10:
                print(f"  ... and {len(commonjs_violations) - 10} more")
            
            for violation in commonjs_violations:
                self.errors.append(violation)
        else:
            # Count total files checked
            ts_files = list(src_path.rglob("*.ts")) + list(src_path.rglob("*.tsx"))
            print_success(f"All {len(ts_files)} TypeScript files use ES6 import/export style")
    
    def validate_typescript_interfaces(self):
        """Validate TypeScript interface completeness"""
        print_section("VALIDATING TYPESCRIPT INTERFACES")
        
        types_path = self.base_path / "src" / "types"
        if not types_path.exists():
            print_error("Types directory not found")
            return
        
        all_valid = True
        
        for entity in self.entities:
            entity_name = entity.get('name')
            type_file = types_path / f"{entity_name}.types.ts"
            
            if not type_file.exists():
                continue
            
            try:
                with open(type_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check that base interface has all required fields
                entity_fields = entity.get('fields', {})
                base_interface_match = re.search(
                    rf"export\s+interface\s+{entity_name}\s*\{{([^}}]+)\}}",
                    content,
                    re.DOTALL
                )
                
                if base_interface_match:
                    interface_body = base_interface_match.group(1)
                    
                    for field_name, field_info in entity_fields.items():
                        field_type = field_info.get('type')
                        constraints = field_info.get('constraints', [])
                        
                        # Check if field exists in interface
                        field_pattern = rf"{field_name}\s*[?:]"
                        if not re.search(field_pattern, interface_body):
                            print_error(f"{entity_name}: Field '{field_name}' missing in base interface")
                            self.errors.append(f"{entity_name}: Missing field {field_name}")
                            all_valid = False
                        else:
                            # Check if optional marker (?) matches required constraint
                            is_required = 'required' in constraints
                            has_optional = bool(re.search(rf"{field_name}\s*\?:", interface_body))
                            
                            if is_required and has_optional:
                                print_warning(f"{entity_name}: Field '{field_name}' is required but marked optional")
                            elif not is_required and not has_optional and field_name not in ['id', 'createdAt', 'updatedAt']:
                                print_warning(f"{entity_name}: Field '{field_name}' is optional but not marked with '?'")
            
            except Exception as e:
                print_error(f"{entity_name}: Error validating interface - {e}")
                all_valid = False
        
        if all_valid:
            print_success("All TypeScript interfaces are complete")
        else:
            print_error("Some TypeScript interfaces are incomplete")
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_inputs():
            return False
        
        self.validate_type_definitions()
        self.validate_service_files()
        self.validate_components()
        self.validate_barrel_exports()
        self.validate_es6_style()
        self.validate_typescript_interfaces()
        
        print_section("SUMMARY")
        
        if len(self.errors) > 0:
            print_error(f"Validation FAILED with {len(self.errors)} error(s)")
            if len(self.warnings) > 0:
                print_warning(f"Also found {len(self.warnings)} warning(s)")
            return False
        else:
            print_success("✓ ALL VALIDATIONS PASSED")
            if len(self.warnings) > 0:
                print_warning(f"Found {len(self.warnings)} warning(s)")
            print(f"  Entities: {len(self.entities)}")
            print(f"  Entities with endpoints: {len(self.openapi_entities)}")
            return True


    def validate_stage_output(self):
        """Validate stage_2_output.json completeness"""
        print_section("STAGE OUTPUT VALIDATION")
        
        output_file = Path("output/stage_2_output.json")
        
        if not output_file.exists():
            print_error("output/stage_2_output.json not found")
            return
        
        try:
            with open(output_file, 'r') as f:
                output_data = json.load(f)
            
            if 'files' not in output_data:
                print_error("output/stage_2_output.json missing 'files' key")
                return
            
            documented_files = set(output_data['files'].keys())
            
            # Scan actual project files
            actual_files = set()
            src_path = Path("generated_project/src")
            
            if src_path.exists():
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        if file.endswith(('.ts', '.tsx')) and not file.endswith('.d.ts'):
                            full_path = Path(root) / file
                            rel_path = full_path.relative_to(Path("generated_project"))
                            actual_files.add(str(rel_path))
            
            # Check all actual files are documented
            undocumented = actual_files - documented_files
            if undocumented:
                print_error(f"Files not documented in stage_2_output.json:")
                for file in sorted(undocumented):
                    print(f"  - {file}")
            
            # Check all documented files exist
            missing = documented_files - actual_files
            if missing:
                print_error(f"Documented files that don't exist:")
                for file in sorted(missing):
                    print(f"  - {file}")
            
            if not undocumented and not missing:
                print_success(f"All {len(actual_files)} files properly documented")
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in stage_2_output.json: {e}")
        except Exception as e:
            print_error(f"Error validating stage output: {e}")
def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_2_validator.py <erd.json> <openapi.yaml>")
        print_info("Example: python3 validators/stage_2_validator.py output/erd.json input/openapi.yaml")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage2Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()