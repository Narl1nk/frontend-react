#!/usr/bin/env python3
"""
Stage 3 Validator - Infrastructure & Configuration Validator

Validates that all infrastructure files are correctly generated for React TypeScript frontend

CRITICAL VALIDATIONS:
1. API client with interceptors
2. Utility functions (formatting, storage)
3. Custom hooks (useApi, usePagination)
4. Environment configuration
5. Build configuration (vite.config.ts)
6. TypeScript configuration (tsconfig.json)
7. Barrel exports
8. ES6 import/export style
9. TypeScript type safety
10. Import validation
"""

import sys
import os
import json
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

class Stage3Validator:
    def __init__(self, erd_path: str, openapi_path: str):
        self.erd_path = erd_path
        self.openapi_path = openapi_path
        self.errors = []
        self.warnings = []
        self.validation_results = {}
        self.base_path = Path("generated_project")
        
        # Track exported symbols from each file
        self.file_exports = {}
        self.file_imports = {}
        
    def load_inputs(self) -> bool:
        """Load ERD and OpenAPI files"""
        try:
            with open(self.erd_path, 'r') as f:
                self.erd_data = json.load(f)
            
            with open(self.openapi_path, 'r') as f:
                self.openapi_data = json.load(f)
            
            return True
        except Exception as e:
            self.errors.append(f"Error loading inputs: {e}")
            return False
    
    def validate_api_client(self):
        """Validate API client with interceptors"""
        validation_name = "API Client"
        api_file = self.base_path / "src" / "services" / "api.ts"
        
        if not api_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/services/api.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not re.search(r"import.*axios", content):
                file_errors.append("Missing axios import")
            
            if not re.search(r"axios\.create\s*\(", content):
                file_errors.append("Missing axios instance creation (axios.create)")
            
            if not re.search(r"baseURL\s*:", content):
                file_errors.append("Missing baseURL configuration")
            
            if not re.search(r"interceptors\.request\.use", content):
                file_errors.append("Missing request interceptor")
            
            if not re.search(r"interceptors\.response\.use", content):
                file_errors.append("Missing response interceptor")
            
            if not re.search(r"export\s+default", content):
                file_errors.append("Missing default export")
            
            if not re.search(r"import\.meta\.env\.VITE_API_BASE_URL", content):
                self.warnings.append(f"{validation_name}: Should use VITE_API_BASE_URL from environment")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_formatting_utilities(self):
        """Validate formatting utilities"""
        validation_name = "Formatting Utilities"
        formatting_file = self.base_path / "src" / "utils" / "formatting.ts"
        
        if not formatting_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/utils/formatting.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        required_functions = [
            'formatDate',
            'formatDateTime',
            'formatCurrency',
            'formatNumber',
            'truncate',
            'capitalize'
        ]
        
        try:
            with open(formatting_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for func in required_functions:
                if not re.search(rf"export\s+(const|function)\s+{func}", content):
                    file_errors.append(f"Missing function: {func}()")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_storage_utilities(self):
        """Validate storage utilities"""
        validation_name = "Storage Utilities"
        storage_file = self.base_path / "src" / "utils" / "storage.ts"
        
        if not storage_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/utils/storage.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not re.search(r"export\s+const\s+(storage|storageUtil)\s*=", content):
                file_errors.append("Missing storage object export")
            
            required_methods = ['get', 'set', 'remove', 'clear']
            for method in required_methods:
                # Match both shorthand (get(...)) and arrow function (get: (...) =>)
                if not re.search(rf"{method}\s*[:(=<]", content):
                    file_errors.append(f"Missing {method}() method")
            
            if not re.search(r"<T>", content):
                self.warnings.append(f"{validation_name}: Should use TypeScript generics for type safety")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_custom_hooks(self):
        """Validate custom hooks"""
        validation_name = "Custom Hooks"
        hooks_path = self.base_path / "src" / "hooks"
        
        if not hooks_path.exists():
            self.errors.append(f"{validation_name}: Directory not found - src/hooks/")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        # Check useApi hook
        use_api_file = hooks_path / "useApi.ts"
        if not use_api_file.exists():
            file_errors.append("Missing useApi.ts file")
        else:
            try:
                with open(use_api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Match both 'export const useApi', 'export function useApi', and 'export default useApi'
                if not re.search(r"(export\s+(const|function)\s+useApi|export\s+default\s+useApi)", content):
                    file_errors.append("useApi.ts: Missing hook export")
                
                if not re.search(r"import.*from\s+['\"]react['\"]", content):
                    file_errors.append("useApi.ts: Missing React imports")
                
                if not re.search(r"<T[,>]", content):
                    self.warnings.append(f"{validation_name}: useApi.ts should use TypeScript generics")
            
            except Exception as e:
                file_errors.append(f"useApi.ts: Error reading file - {e}")
        
        # Check usePagination hook
        use_pagination_file = hooks_path / "usePagination.ts"
        if not use_pagination_file.exists():
            file_errors.append("Missing usePagination.ts file")
        else:
            try:
                with open(use_pagination_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Match both 'export const usePagination', 'export function usePagination', and 'export default usePagination'
                if not re.search(r"(export\s+(const|function)\s+usePagination|export\s+default\s+usePagination)", content):
                    file_errors.append("usePagination.ts: Missing hook export")
                
                if not re.search(r"import.*from\s+['\"]react['\"]", content):
                    file_errors.append("usePagination.ts: Missing React imports")
            
            except Exception as e:
                file_errors.append(f"usePagination.ts: Error reading file - {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_environment_config(self):
        """Validate environment configuration"""
        validation_name = "Environment Config"
        env_file = self.base_path / ".env"
        
        if not env_file.exists():
            self.errors.append(f"{validation_name}: File not found - .env")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not re.search(r"VITE_API_BASE_URL\s*=", content):
                file_errors.append("Missing VITE_API_BASE_URL variable")
            
            env_vars = re.findall(r"^([A-Z_]+)\s*=", content, re.MULTILINE)
            for var in env_vars:
                if not var.startswith('VITE_') and var not in ['NODE_ENV', 'PORT']:
                    self.warnings.append(f"{validation_name}: Variable '{var}' should have VITE_ prefix")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_vite_config(self):
        """Validate Vite configuration"""
        validation_name = "Vite Config"
        vite_config = self.base_path / "vite.config.ts"
        
        if not vite_config.exists():
            self.errors.append(f"{validation_name}: File not found - vite.config.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(vite_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not re.search(r"import.*defineConfig.*from\s+['\"]vite['\"]", content):
                file_errors.append("Missing defineConfig import from vite")
            
            if not re.search(r"import.*react.*from\s+['\"]@vitejs/plugin-react['\"]", content):
                file_errors.append("Missing React plugin import")
            
            if not re.search(r"proxy\s*:", content):
                self.warnings.append(f"{validation_name}: Missing proxy configuration")
            
            if not re.search(r"['\"]\/api['\"]", content):
                self.warnings.append(f"{validation_name}: Should proxy /api requests")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_typescript_config(self):
        """Validate TypeScript configuration"""
        validation_name = "TypeScript Config"
        tsconfig = self.base_path / "tsconfig.json"
        
        if not tsconfig.exists():
            self.errors.append(f"{validation_name}: File not found - tsconfig.json")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(tsconfig, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            compiler_options = config.get('compilerOptions', {})
            
            if not compiler_options.get('strict'):
                self.warnings.append(f"{validation_name}: Strict mode not enabled")
            
            if compiler_options.get('jsx') not in ['react', 'react-jsx']:
                file_errors.append("Missing or incorrect jsx compiler option (should be 'react-jsx')")
            
            if 'moduleResolution' not in compiler_options:
                self.warnings.append(f"{validation_name}: Should specify moduleResolution")
        
        except json.JSONDecodeError as e:
            file_errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_barrel_exports(self):
        """Validate barrel exports"""
        validation_name = "Barrel Exports"
        file_errors = []
        
        # Check utils/index.ts
        utils_index = self.base_path / "src" / "utils" / "index.ts"
        if not utils_index.exists():
            file_errors.append("Missing src/utils/index.ts")
        else:
            try:
                with open(utils_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/formatting['\"]", content):
                    file_errors.append("utils/index.ts: Missing export for formatting")
                
                # Accept both 'storage' and 'storageUtil' exports
                if not re.search(r"export.*from\s+['\"]\.\/storage['\"]", content):
                    file_errors.append("utils/index.ts: Missing export for storage")
            
            except Exception as e:
                file_errors.append(f"utils/index.ts: Error reading file - {e}")
        
        # Check hooks/index.ts
        hooks_index = self.base_path / "src" / "hooks" / "index.ts"
        if not hooks_index.exists():
            file_errors.append("Missing src/hooks/index.ts")
        else:
            try:
                with open(hooks_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for useApi export - accept both patterns:
                # export * from './useApi' OR export { default as useApi } from './useApi'
                if not re.search(r"(export\s+\*\s+from\s+['\"]\.\/useApi['\"]|export\s*\{\s*default\s+as\s+useApi\s*\}\s*from)", content):
                    file_errors.append("hooks/index.ts: Missing export for useApi")
                
                # Check for usePagination export - accept both patterns
                if not re.search(r"(export\s+\*\s+from\s+['\"]\.\/usePagination['\"]|export\s*\{\s*default\s+as\s+usePagination\s*\}\s*from)", content):
                    file_errors.append("hooks/index.ts: Missing export for usePagination")
            
            except Exception as e:
                file_errors.append(f"hooks/index.ts: Error reading file - {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_es6_style(self):
        """Validate ES6 import/export style"""
        validation_name = "ES6 Import/Export"
        src_path = self.base_path / "src"
        
        if not src_path.exists():
            self.errors.append(f"{validation_name}: src directory not found")
            self.validation_results[validation_name] = False
            return
        
        commonjs_violations = []
        
        for directory in ['utils', 'hooks', 'services']:
            dir_path = src_path / directory
            if not dir_path.exists():
                continue
            
            for file in dir_path.glob("*.ts"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    rel_path = str(file.relative_to(self.base_path))
                    
                    if re.search(r"=\s*require\s*\(", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'require()'")
                    
                    if re.search(r"module\.exports\s*=", content):
                        commonjs_violations.append(f"{rel_path}: Uses CommonJS 'module.exports'")
                
                except Exception as e:
                    pass
        
        if commonjs_violations:
            for violation in commonjs_violations:
                self.errors.append(f"{validation_name}: {violation}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_typescript_types(self):
        """Validate TypeScript type safety"""
        validation_name = "TypeScript Types"
        files_to_check = []
        
        for directory in ['utils', 'hooks']:
            dir_path = self.base_path / "src" / directory
            if dir_path.exists():
                files_to_check.extend(dir_path.glob("*.ts"))
        
        api_file = self.base_path / "src" / "services" / "api.ts"
        if api_file.exists():
            files_to_check.append(api_file)
        
        untyped_functions = []
        
        for file in files_to_check:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = str(file.relative_to(self.base_path))
                
                untyped = re.findall(
                    r"export\s+(?:const|function)\s+(\w+)\s*=\s*(?:<[^>]+>)?\s*\([^)]*\)\s*=>(?!\s*:)",
                    content
                )
                
                if untyped:
                    for func_name in untyped:
                        untyped_functions.append(f"{rel_path}: Function '{func_name}' missing return type")
            
            except Exception as e:
                pass
        
        if untyped_functions:
            for func in untyped_functions:
                self.warnings.append(f"{validation_name}: {func}")
        
        self.validation_results[validation_name] = True
    
    def _scan_file_exports(self, file_path: Path) -> Set[str]:
        """Scan a TypeScript file for exported symbols"""
        exports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            named_exports = re.findall(r'export\s+(?:interface|type|const|let|var|function|class)\s+(\w+)', content)
            exports.update(named_exports)
            
            export_declarations = re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
            for decl in export_declarations:
                symbols = [s.strip().split(' as ')[0].strip() for s in decl.split(',')]
                exports.update(symbols)
            
            if re.search(r'export\s+\*\s+from', content):
                exports.add('*')
            
            if re.search(r'export\s+default', content):
                exports.add('default')
        
        except Exception as e:
            pass
        
        return exports
    
    def _scan_file_imports(self, file_path: Path) -> List[Tuple[List[str], str]]:
        """Scan a TypeScript file for imports"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            named_imports = re.finditer(r"import\s*\{\s*([^}]+)\s*\}\s*from\s*['\"]([^'\"]+)['\"]", content)
            for match in named_imports:
                symbols_str = match.group(1)
                from_path = match.group(2)
                symbols = [s.strip().split(' as ')[0].strip() for s in symbols_str.split(',')]
                imports.append((symbols, from_path))
            
            default_imports = re.finditer(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in default_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
            
            wildcard_imports = re.finditer(r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in wildcard_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
        
        except Exception as e:
            pass
        
        return imports
    
    def _resolve_import_path(self, importing_file: Path, import_path: str) -> Optional[Path]:
        """Resolve relative import path to absolute file path"""
        if import_path.startswith('.'):
            base_dir = importing_file.parent
            resolved = (base_dir / import_path).resolve()
            
            for ext in ['.ts', '.tsx', '.js', '.jsx', '']:
                if ext == '':
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
    
    def validate_imports(self):
        """Validate all imports are valid"""
        validation_name = "Import Validation"
        src_path = self.base_path / "src"
        
        if not src_path.exists():
            self.validation_results[validation_name] = True
            return
        
        # Build export map
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                exports = self._scan_file_exports(file_path)
                self.file_exports[file_path] = exports
        
        # Validate imports
        import_errors = []
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.base_path))
                imports = self._scan_file_imports(file_path)
                
                for symbols, from_path in imports:
                    if not from_path.startswith('.'):
                        continue
                    
                    resolved_path = self._resolve_import_path(file_path, from_path)
                    
                    if resolved_path is None:
                        import_errors.append(f"{rel_path}: Import path not found '{from_path}'")
                        continue
                    
                    if resolved_path not in self.file_exports:
                        continue
                    
                    available_exports = self.file_exports[resolved_path]
                    
                    if '*' in available_exports:
                        continue
                    
                    for symbol in symbols:
                        if symbol not in available_exports and 'default' not in available_exports:
                            import_errors.append(f"{rel_path}: Symbol '{symbol}' not exported from '{from_path}'")
        
        if import_errors:
            for error in import_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_inputs():
            return False
        
        # Run all validations silently
        self.validate_api_client()
        self.validate_formatting_utilities()
        self.validate_storage_utilities()
        self.validate_custom_hooks()
        self.validate_environment_config()
        self.validate_vite_config()
        self.validate_typescript_config()
        self.validate_barrel_exports()
        self.validate_es6_style()
        self.validate_typescript_types()
        self.validate_imports()
        
        # Print summary
        print_section("VALIDATION SUMMARY")
        
        passed = []
        failed = []
        
        for validation, result in self.validation_results.items():
            if result:
                passed.append(validation)
            else:
                failed.append(validation)
        
        # Print passed validations
        for validation in passed:
            print_success(f"{validation}: PASSED")
        
        # Print failed validations
        for validation in failed:
            print_error(f"{validation}: FAILED")
        
        # Print detailed errors if any exist
        if self.errors:
            print_section("ERROR DETAILS")
            for i, error in enumerate(self.errors, 1):
                print_error(f"{i}. {error}")
        
        # Print warnings if any exist
        if self.warnings:
            print(f"\n{Colors.YELLOW}WARNINGS:{Colors.RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print_warning(f"{i}. {warning}")
        
        # Final result
        print()
        if len(self.errors) > 0:
            print_error(f"VALIDATION FAILED: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
            return False
        else:
            print_success(f"✓ ALL VALIDATIONS PASSED")
            if len(self.warnings) > 0:
                print_info(f"Note: {len(self.warnings)} warning(s) found")
            return True

def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_3_validator.py <erd.json> <openapi.json>")
        print_info("Example: python3 validators/stage_3_validator.py output/erd.json output/openapi.json")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage3Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
        
    def load_inputs(self) -> bool:
        """Load ERD and OpenAPI files"""
        try:
            with open(self.erd_path, 'r') as f:
                self.erd_data = json.load(f)
            
            with open(self.openapi_path, 'r') as f:
                self.openapi_data = json.load(f)
            
            return True
        except Exception as e:
            print_error(f"Error loading inputs: {e}")
            return False
    
    def validate_api_client(self):
        """Validate API client with interceptors"""
        print_section("VALIDATING API CLIENT")
        
        api_file = self.base_path / "src" / "services" / "api.ts"
        
        if not api_file.exists():
            print_error("API client not found: src/services/api.ts")
            self.errors.append("Missing API client file")
            return
        
        all_valid = True
        
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for axios import
            if not re.search(r"import.*axios", content):
                print_error("Missing axios import")
                self.errors.append("api.ts: Missing axios import")
                all_valid = False
            
            # Check for axios instance creation
            if not re.search(r"axios\.create\s*\(", content):
                print_error("Missing axios instance creation (axios.create)")
                self.errors.append("api.ts: Missing axios.create()")
                all_valid = False
            
            # Check for baseURL configuration
            if not re.search(r"baseURL\s*:", content):
                print_error("Missing baseURL configuration")
                self.errors.append("api.ts: Missing baseURL")
                all_valid = False
            
            # Check for request interceptor
            if not re.search(r"interceptors\.request\.use", content):
                print_error("Missing request interceptor")
                self.errors.append("api.ts: Missing request interceptor")
                all_valid = False
            
            # Check for response interceptor
            if not re.search(r"interceptors\.response\.use", content):
                print_error("Missing response interceptor")
                self.errors.append("api.ts: Missing response interceptor")
                all_valid = False
            
            # Check for default export
            if not re.search(r"export\s+default", content):
                print_error("Missing default export")
                self.errors.append("api.ts: Missing default export")
                all_valid = False
            
            # Check for environment variable usage
            if not re.search(r"import\.meta\.env\.VITE_API_BASE_URL", content):
                print_warning("API client doesn't use VITE_API_BASE_URL from environment")
                self.warnings.append("api.ts: Should use import.meta.env.VITE_API_BASE_URL")
        
        except Exception as e:
            print_error(f"Error reading api.ts: {e}")
            self.errors.append("api.ts: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success("API client properly configured with interceptors")
        else:
            print_error("API client is missing required features")
    
    def validate_formatting_utilities(self):
        """Validate formatting utilities"""
        print_section("VALIDATING FORMATTING UTILITIES")
        
        formatting_file = self.base_path / "src" / "utils" / "formatting.ts"
        
        if not formatting_file.exists():
            print_error("Formatting utilities not found: src/utils/formatting.ts")
            self.errors.append("Missing formatting utilities file")
            return
        
        all_valid = True
        required_functions = [
            'formatDate',
            'formatDateTime',
            'formatCurrency',
            'formatNumber',
            'truncate',
            'capitalize'
        ]
        
        try:
            with open(formatting_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for func in required_functions:
                if not re.search(rf"export\s+(const|function)\s+{func}", content):
                    print_error(f"Missing function: {func}")
                    self.errors.append(f"formatting.ts: Missing {func}()")
                    all_valid = False
        
        except Exception as e:
            print_error(f"Error reading formatting.ts: {e}")
            self.errors.append("formatting.ts: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success(f"All {len(required_functions)} formatting functions present")
        else:
            print_error("Some formatting functions are missing")
    
    def validate_storage_utilities(self):
        """Validate storage utilities"""
        print_section("VALIDATING STORAGE UTILITIES")
        
        storage_file = self.base_path / "src" / "utils" / "storage.ts"
        
        if not storage_file.exists():
            print_error("Storage utilities not found: src/utils/storage.ts")
            self.errors.append("Missing storage utilities file")
            return
        
        all_valid = True
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for storage object export
            if not re.search(r"export\s+const\s+storage\s*=", content):
                print_error("Missing storage object export")
                self.errors.append("storage.ts: Missing storage export")
                all_valid = False
            
            # Check for required methods
            required_methods = ['get', 'set', 'remove', 'clear']
            for method in required_methods:
                if not re.search(rf"{method}\s*[:=]", content):
                    print_error(f"Missing storage method: {method}")
                    self.errors.append(f"storage.ts: Missing {method}() method")
                    all_valid = False
            
            # Check for TypeScript generics
            if not re.search(r"<T>", content):
                print_warning("Storage utilities should use TypeScript generics for type safety")
                self.warnings.append("storage.ts: Missing generic types")
        
        except Exception as e:
            print_error(f"Error reading storage.ts: {e}")
            self.errors.append("storage.ts: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success("Storage utilities properly configured")
        else:
            print_error("Storage utilities are incomplete")
    
    def validate_custom_hooks(self):
        """Validate custom hooks"""
        print_section("VALIDATING CUSTOM HOOKS")
        
        hooks_path = self.base_path / "src" / "hooks"
        
        if not hooks_path.exists():
            print_error("Hooks directory not found: src/hooks/")
            self.errors.append("Missing hooks directory")
            return
        
        all_valid = True
        
        # Check useApi hook
        use_api_file = hooks_path / "useApi.ts"
        if not use_api_file.exists():
            print_error("useApi hook not found: src/hooks/useApi.ts")
            self.errors.append("Missing useApi.ts")
            all_valid = False
        else:
            try:
                with open(use_api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hook export
                if not re.search(r"export\s+const\s+useApi", content):
                    print_error("useApi: Missing hook export")
                    self.errors.append("useApi.ts: Missing export")
                    all_valid = False
                
                # Check for React imports
                if not re.search(r"import.*from\s+['\"]react['\"]", content):
                    print_error("useApi: Missing React imports")
                    self.errors.append("useApi.ts: Missing React imports")
                    all_valid = False
                
                # Check for TypeScript generics
                if not re.search(r"<T[,>]", content):
                    print_warning("useApi: Should use TypeScript generics")
                    self.warnings.append("useApi.ts: Missing generic types")
            
            except Exception as e:
                print_error(f"Error reading useApi.ts: {e}")
                self.errors.append("useApi.ts: Error reading file")
                all_valid = False
        
        # Check usePagination hook
        use_pagination_file = hooks_path / "usePagination.ts"
        if not use_pagination_file.exists():
            print_error("usePagination hook not found: src/hooks/usePagination.ts")
            self.errors.append("Missing usePagination.ts")
            all_valid = False
        else:
            try:
                with open(use_pagination_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hook export
                if not re.search(r"export\s+const\s+usePagination", content):
                    print_error("usePagination: Missing hook export")
                    self.errors.append("usePagination.ts: Missing export")
                    all_valid = False
                
                # Check for React imports
                if not re.search(r"import.*from\s+['\"]react['\"]", content):
                    print_error("usePagination: Missing React imports")
                    self.errors.append("usePagination.ts: Missing React imports")
                    all_valid = False
            
            except Exception as e:
                print_error(f"Error reading usePagination.ts: {e}")
                self.errors.append("usePagination.ts: Error reading file")
                all_valid = False
        
        if all_valid:
            print_success("All custom hooks properly configured")
        else:
            print_error("Some custom hooks are missing or incomplete")
    
    def validate_environment_config(self):
        """Validate environment configuration"""
        print_section("VALIDATING ENVIRONMENT CONFIGURATION")
        
        env_file = self.base_path / ".env"
        
        if not env_file.exists():
            print_error(".env file not found")
            self.errors.append("Missing .env file")
            return
        
        all_valid = True
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for VITE_API_BASE_URL
            if not re.search(r"VITE_API_BASE_URL\s*=", content):
                print_error("Missing VITE_API_BASE_URL in .env")
                self.errors.append(".env: Missing VITE_API_BASE_URL")
                all_valid = False
            
            # Check for VITE_ prefix convention
            env_vars = re.findall(r"^([A-Z_]+)\s*=", content, re.MULTILINE)
            for var in env_vars:
                if not var.startswith('VITE_') and var not in ['NODE_ENV', 'PORT']:
                    print_warning(f"Environment variable '{var}' should have VITE_ prefix for Vite access")
        
        except Exception as e:
            print_error(f"Error reading .env: {e}")
            self.errors.append(".env: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success("Environment configuration properly set")
        else:
            print_error("Environment configuration is incomplete")
    
    def validate_vite_config(self):
        """Validate Vite configuration"""
        print_section("VALIDATING VITE CONFIGURATION")
        
        vite_config = self.base_path / "vite.config.ts"
        
        if not vite_config.exists():
            print_error("vite.config.ts not found")
            self.errors.append("Missing vite.config.ts")
            return
        
        all_valid = True
        
        try:
            with open(vite_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for defineConfig import
            if not re.search(r"import.*defineConfig.*from\s+['\"]vite['\"]", content):
                print_error("Missing defineConfig import from vite")
                self.errors.append("vite.config.ts: Missing defineConfig import")
                all_valid = False
            
            # Check for React plugin
            if not re.search(r"import.*react.*from\s+['\"]@vitejs/plugin-react['\"]", content):
                print_error("Missing React plugin import")
                self.errors.append("vite.config.ts: Missing React plugin")
                all_valid = False
            
            # Check for proxy configuration
            if not re.search(r"proxy\s*:", content):
                print_warning("Missing proxy configuration for API calls")
                self.warnings.append("vite.config.ts: Missing proxy configuration")
            
            # Check for /api proxy
            if not re.search(r"['\"]\/api['\"]", content):
                print_warning("Missing /api proxy configuration")
                self.warnings.append("vite.config.ts: Should proxy /api requests")
        
        except Exception as e:
            print_error(f"Error reading vite.config.ts: {e}")
            self.errors.append("vite.config.ts: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success("Vite configuration properly set")
        else:
            print_error("Vite configuration is incomplete")
    
    def validate_typescript_config(self):
        """Validate TypeScript configuration"""
        print_section("VALIDATING TYPESCRIPT CONFIGURATION")
        
        tsconfig = self.base_path / "tsconfig.json"
        
        if not tsconfig.exists():
            print_error("tsconfig.json not found")
            self.errors.append("Missing tsconfig.json")
            return
        
        all_valid = True
        
        try:
            with open(tsconfig, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            compiler_options = config.get('compilerOptions', {})
            
            # Check for strict mode
            if not compiler_options.get('strict'):
                print_warning("TypeScript strict mode not enabled")
                self.warnings.append("tsconfig.json: strict mode should be enabled")
            
            # Check for jsx
            if compiler_options.get('jsx') not in ['react', 'react-jsx']:
                print_error("Missing or incorrect jsx compiler option")
                self.errors.append("tsconfig.json: jsx should be 'react-jsx'")
                all_valid = False
            
            # Check for module resolution
            if 'moduleResolution' not in compiler_options:
                print_warning("Missing moduleResolution option")
                self.warnings.append("tsconfig.json: Should specify moduleResolution")
        
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in tsconfig.json: {e}")
            self.errors.append("tsconfig.json: Invalid JSON")
            all_valid = False
        except Exception as e:
            print_error(f"Error reading tsconfig.json: {e}")
            self.errors.append("tsconfig.json: Error reading file")
            all_valid = False
        
        if all_valid:
            print_success("TypeScript configuration properly set")
        else:
            print_error("TypeScript configuration is incomplete")
    
    def validate_barrel_exports(self):
        """Validate barrel exports"""
        print_section("VALIDATING BARREL EXPORTS")
        
        all_valid = True
        
        # Check utils/index.ts
        utils_index = self.base_path / "src" / "utils" / "index.ts"
        if not utils_index.exists():
            print_error("Missing barrel export: src/utils/index.ts")
            self.errors.append("Missing utils/index.ts")
            all_valid = False
        else:
            try:
                with open(utils_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for formatting export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/formatting['\"]", content):
                    print_error("utils/index.ts: Missing export for formatting")
                    self.errors.append("utils/index.ts: Missing formatting export")
                    all_valid = False
                
                # Check for storage export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/storage['\"]", content):
                    print_error("utils/index.ts: Missing export for storage")
                    self.errors.append("utils/index.ts: Missing storage export")
                    all_valid = False
            
            except Exception as e:
                print_error(f"Error reading utils/index.ts: {e}")
                all_valid = False
        
        # Check hooks/index.ts
        hooks_index = self.base_path / "src" / "hooks" / "index.ts"
        if not hooks_index.exists():
            print_error("Missing barrel export: src/hooks/index.ts")
            self.errors.append("Missing hooks/index.ts")
            all_valid = False
        else:
            try:
                with open(hooks_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for useApi export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/useApi['\"]", content):
                    print_error("hooks/index.ts: Missing export for useApi")
                    self.errors.append("hooks/index.ts: Missing useApi export")
                    all_valid = False
                
                # Check for usePagination export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/usePagination['\"]", content):
                    print_error("hooks/index.ts: Missing export for usePagination")
                    self.errors.append("hooks/index.ts: Missing usePagination export")
                    all_valid = False
            
            except Exception as e:
                print_error(f"Error reading hooks/index.ts: {e}")
                all_valid = False
        
        if all_valid:
            print_success("All barrel exports properly configured")
        else:
            print_error("Some barrel exports are missing")
    
    def validate_es6_style(self):
        """Validate ES6 import/export style"""
        print_section("VALIDATING ES6 IMPORT/EXPORT STYLE")
        
        src_path = self.base_path / "src"
        if not src_path.exists():
            print_error("src directory not found")
            return
        
        commonjs_violations = []
        
        # Check utils and hooks directories
        for directory in ['utils', 'hooks', 'services']:
            dir_path = src_path / directory
            if not dir_path.exists():
                continue
            
            for file in dir_path.glob("*.ts"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    rel_path = str(file.relative_to(self.base_path))
                    
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
            for violation in commonjs_violations:
                print_error(violation)
                print(f"  {Colors.YELLOW}FIX: Use ES6 import/export syntax{Colors.RESET}")
            
            self.errors.extend(commonjs_violations)
        else:
            print_success("All infrastructure files use ES6 import/export style")
    
    def validate_typescript_types(self):
        """Validate TypeScript type safety"""
        print_section("VALIDATING TYPESCRIPT TYPE SAFETY")
        
        all_valid = True
        files_to_check = []
        
        # Collect all TypeScript files in utils and hooks
        for directory in ['utils', 'hooks']:
            dir_path = self.base_path / "src" / directory
            if dir_path.exists():
                files_to_check.extend(dir_path.glob("*.ts"))
        
        # Also check api.ts
        api_file = self.base_path / "src" / "services" / "api.ts"
        if api_file.exists():
            files_to_check.append(api_file)
        
        untyped_functions = []
        
        for file in files_to_check:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = str(file.relative_to(self.base_path))
                
                # Check for explicit return types on exported functions
                # Pattern: export (const|function) name = (...) =>  (without explicit return type)
                untyped = re.findall(
                    r"export\s+(?:const|function)\s+(\w+)\s*=\s*(?:<[^>]+>)?\s*\([^)]*\)\s*=>(?!\s*:)",
                    content
                )
                
                if untyped:
                    for func_name in untyped:
                        untyped_functions.append(f"{rel_path}: Function '{func_name}' missing return type")
                        all_valid = False
            
            except Exception as e:
                pass
        
        if untyped_functions:
            print_warning(f"Found {len(untyped_functions)} functions without explicit return types")
            for issue in untyped_functions[:5]:
                print_warning(issue)
            if len(untyped_functions) > 5:
                print(f"  ... and {len(untyped_functions) - 5} more")
        
        if all_valid:
            print_success("All functions are properly typed")
        else:
            print_warning("Some functions could benefit from explicit return types")
    
    def _scan_file_exports(self, file_path: Path) -> Set[str]:
        """Scan a TypeScript file for exported symbols"""
        exports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Export named items
            named_exports = re.findall(r'export\s+(?:interface|type|const|let|var|function|class)\s+(\w+)', content)
            exports.update(named_exports)
            
            # Export declarations
            export_declarations = re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
            for decl in export_declarations:
                symbols = [s.strip().split(' as ')[0].strip() for s in decl.split(',')]
                exports.update(symbols)
            
            # Re-exports
            if re.search(r'export\s+\*\s+from', content):
                exports.add('*')
            
            # Default export
            if re.search(r'export\s+default', content):
                exports.add('default')
        
        except Exception as e:
            pass
        
        return exports
    
    def _scan_file_imports(self, file_path: Path) -> List[Tuple[List[str], str]]:
        """Scan a TypeScript file for imports"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Named imports
            named_imports = re.finditer(r"import\s*\{\s*([^}]+)\s*\}\s*from\s*['\"]([^'\"]+)['\"]", content)
            for match in named_imports:
                symbols_str = match.group(1)
                from_path = match.group(2)
                symbols = [s.strip().split(' as ')[0].strip() for s in symbols_str.split(',')]
                imports.append((symbols, from_path))
            
            # Default imports
            default_imports = re.finditer(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in default_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
            
            # Wildcard imports
            wildcard_imports = re.finditer(r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            for match in wildcard_imports:
                symbol = match.group(1)
                from_path = match.group(2)
                imports.append(([symbol], from_path))
        
        except Exception as e:
            pass
        
        return imports
    
    def _resolve_import_path(self, importing_file: Path, import_path: str) -> Optional[Path]:
        """Resolve relative import path to absolute file path"""
        if import_path.startswith('.'):
            base_dir = importing_file.parent
            resolved = (base_dir / import_path).resolve()
            
            for ext in ['.ts', '.tsx', '.js', '.jsx', '']:
                if ext == '':
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
    
    def validate_imports(self):
        """Validate all imports are valid"""
        print_section("VALIDATING IMPORTS")
        
        print_info("Building export map...")
        
        src_path = self.base_path / "src"
        if not src_path.exists():
            return
        
        # Build export map
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                exports = self._scan_file_exports(file_path)
                self.file_exports[file_path] = exports
        
        # Validate imports
        all_valid = True
        import_errors = []
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.base_path))
                imports = self._scan_file_imports(file_path)
                
                for symbols, from_path in imports:
                    # Skip external packages
                    if not from_path.startswith('.'):
                        continue
                    
                    resolved_path = self._resolve_import_path(file_path, from_path)
                    
                    if resolved_path is None:
                        print_error(f"{rel_path}: Import path not found: '{from_path}'")
                        import_errors.append(f"{rel_path}: Missing import file '{from_path}'")
                        all_valid = False
                        continue
                    
                    if resolved_path not in self.file_exports:
                        continue
                    
                    available_exports = self.file_exports[resolved_path]
                    
                    if '*' in available_exports:
                        continue
                    
                    for symbol in symbols:
                        if symbol not in available_exports and 'default' not in available_exports:
                            print_error(f"{rel_path}: Symbol '{symbol}' not exported from '{from_path}'")
                            import_errors.append(f"{rel_path}: Missing symbol '{symbol}' from '{from_path}'")
                            all_valid = False
        
        if all_valid:
            print_success("All imports are valid")
        else:
            print_error(f"Found {len(import_errors)} import errors")
            for error in import_errors[:10]:
                print(f"  {Colors.RED}{error}{Colors.RESET}")
            if len(import_errors) > 10:
                print(f"  ... and {len(import_errors) - 10} more")
            
            self.errors.extend(import_errors)
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_inputs():
            return False
        
        self.validate_api_client()
        self.validate_formatting_utilities()
        self.validate_storage_utilities()
        self.validate_custom_hooks()
        self.validate_environment_config()
        self.validate_vite_config()
        self.validate_typescript_config()
        self.validate_barrel_exports()
        self.validate_es6_style()
        self.validate_typescript_types()
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
            return True

def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_3_validator.py <erd.json> <openapi.json>")
        print_info("Example: python3 validators/stage_3_validator.py output/erd.json output/openapi.json")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage3Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()