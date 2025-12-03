#!/usr/bin/env python3
"""
Stage 5 Validator - Application Shell & Integration Validator

Validates that application shell is correctly integrated

CRITICAL VALIDATIONS:
1. App.tsx with router integration
2. main.tsx with React 18 API
3. App.css with component styles
4. index.css with CSS reset
5. AuthContext (if auth enabled)
6. Context barrel exports
7. index.html template
8. package.json dependencies
9. Import validation
10. TypeScript types
11. No modifications to previous stages
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

class Stage5Validator:
    def __init__(self, erd_path: str, openapi_path: str):
        self.erd_path = erd_path
        self.openapi_path = openapi_path
        self.errors = []
        self.warnings = []
        self.validation_results = {}
        self.base_path = Path("generated_project")
        
        # Track exported symbols and imports
        self.file_exports = {}
        self.file_imports = {}
        
        # Track auth requirements
        self.auth_enabled = False
        
        # Track installed packages
        self.installed_packages = set()
        
    def load_inputs(self) -> bool:
        """Load ERD and OpenAPI files"""
        try:
            with open(self.erd_path, 'r') as f:
                self.erd_data = json.load(f)
                business_logic = self.erd_data.get('business_logic', {})
                authentication = business_logic.get('authentication', {})
                self.auth_enabled = authentication.get('enabled', False)
            
            with open(self.openapi_path, 'r') as f:
                self.openapi_data = json.load(f)
            
            return True
        except Exception as e:
            self.errors.append(f"Error loading inputs: {e}")
            return False
    
    def validate_app_component(self):
        """Validate App.tsx component"""
        validation_name = "App Component"
        app_file = self.base_path / "src" / "App.tsx"
        
        if not app_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/App.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for App component export
            if not re.search(r"export\s+(const|function)\s+App", content):
                file_errors.append("Missing App component export")
            
            # Check for AppRouter import
            if not re.search(r"import.*AppRouter.*from.*router", content):
                file_errors.append("Missing AppRouter import from router")
            
            # Check for App.css import
            if not re.search(r"import\s+['\"]\.\/App\.css['\"]", content):
                file_errors.append("Missing App.css import")
            
            # Check for AppRouter usage
            if not re.search(r"<AppRouter\s*/?>", content):
                file_errors.append("AppRouter component not used")
            
            # Check for AuthProvider if auth enabled
            if self.auth_enabled:
                if not re.search(r"import.*AuthProvider.*from", content):
                    file_errors.append("Auth enabled but missing AuthProvider import")
                
                if not re.search(r"<AuthProvider>", content):
                    file_errors.append("Auth enabled but AuthProvider not wrapping AppRouter")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_main_entry(self):
        """Validate main.tsx entry point"""
        validation_name = "Main Entry Point"
        main_file = self.base_path / "src" / "main.tsx"
        
        if not main_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/main.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for ReactDOM import
            if not re.search(r"import.*ReactDOM.*from\s+['\"]react-dom/client['\"]", content):
                file_errors.append("Missing ReactDOM import from 'react-dom/client'")
            
            # Check for App import
            if not re.search(r"import.*App.*from.*App", content):
                file_errors.append("Missing App component import")
            
            # Check for index.css import
            if not re.search(r"import\s+['\"]\.\/index\.css['\"]", content):
                file_errors.append("Missing index.css import")
            
            # Check for React 18 createRoot API
            if not re.search(r"ReactDOM\.createRoot", content):
                file_errors.append("Not using React 18 createRoot API")
            
            # Check for StrictMode
            if not re.search(r"<React\.StrictMode>", content):
                self.warnings.append(f"{validation_name}: Should wrap App in React.StrictMode")
            
            # Check for root element
            if not re.search(r"getElementById\(['\"]root['\"]", content):
                file_errors.append("Missing root element selection")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_app_css(self):
        """Validate App.css styles"""
        validation_name = "App.css Styles"
        css_file = self.base_path / "src" / "App.css"
        
        if not css_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/App.css")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for essential component styles
            required_selectors = [
                '.app',
                '.layout',
                '.navbar',
                'button'
            ]
            
            for selector in required_selectors:
                if not re.search(rf"{re.escape(selector)}\s*\{{", content):
                    file_errors.append(f"Missing styles for '{selector}'")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_index_css(self):
        """Validate index.css reset"""
        validation_name = "index.css Reset"
        css_file = self.base_path / "src" / "index.css"
        
        if not css_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/index.css")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for CSS reset patterns
            if not re.search(r"box-sizing\s*:\s*border-box", content):
                file_errors.append("Missing box-sizing reset")
            
            if not re.search(r"body\s*\{", content):
                file_errors.append("Missing body styles")
            
            # Check for root or html styles
            if not re.search(r"(:root|html)\s*\{", content):
                self.warnings.append(f"{validation_name}: Should include :root or html styles")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_auth_context(self):
        """Validate AuthContext (if auth enabled)"""
        validation_name = "Auth Context"
        auth_file = self.base_path / "src" / "context" / "AuthContext.tsx"
        
        if not self.auth_enabled:
            self.validation_results[validation_name] = True
            return
        
        if not auth_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/context/AuthContext.tsx (auth is enabled)")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(auth_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React imports
            if not re.search(r"import.*createContext.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing createContext import from React")
            
            if not re.search(r"import.*useContext.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing useContext import from React")
            
            # Check for AuthContext creation
            if not re.search(r"const\s+AuthContext\s*=\s*createContext", content):
                file_errors.append("Missing AuthContext creation with createContext")
            
            # Check for AuthProvider export
            if not re.search(r"export\s+(const|function)\s+AuthProvider", content):
                file_errors.append("Missing AuthProvider export")
            
            # Check for useAuth hook export
            if not re.search(r"export\s+(const|function)\s+useAuth", content):
                file_errors.append("Missing useAuth hook export")
            
            # Check for auth methods
            required_methods = ['login', 'logout']
            for method in required_methods:
                if not re.search(rf"{method}\s*[:=]", content):
                    file_errors.append(f"Missing {method} method")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_context_barrel_exports(self):
        """Validate context barrel exports"""
        validation_name = "Context Barrel Exports"
        
        # Only required if contexts exist
        context_dir = self.base_path / "src" / "context"
        if not context_dir.exists() or not self.auth_enabled:
            self.validation_results[validation_name] = True
            return
        
        context_index = context_dir / "index.ts"
        
        if not context_index.exists():
            self.errors.append(f"{validation_name}: File not found - src/context/index.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(context_index, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for AuthContext export
            if self.auth_enabled:
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/AuthContext['\"]", content):
                    file_errors.append("Missing export for AuthContext")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_html_template(self):
        """Validate index.html template"""
        validation_name = "HTML Template"
        html_file = self.base_path / "index.html"
        
        if not html_file.exists():
            self.errors.append(f"{validation_name}: File not found - index.html")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for DOCTYPE
            if not re.search(r"<!DOCTYPE html>", content, re.IGNORECASE):
                file_errors.append("Missing DOCTYPE declaration")
            
            # Check for charset meta tag
            if not re.search(r'<meta\s+charset=["\']UTF-8["\']', content, re.IGNORECASE):
                file_errors.append("Missing charset meta tag")
            
            # Check for viewport meta tag
            if not re.search(r'<meta\s+name=["\']viewport["\']', content, re.IGNORECASE):
                file_errors.append("Missing viewport meta tag")
            
            # Check for root div
            if not re.search(r'<div\s+id=["\']root["\']', content):
                file_errors.append("Missing root div element")
            
            # Check for script tag
            if not re.search(r'<script.*src=["\'].*main\.tsx["\']', content):
                file_errors.append("Missing script tag for main.tsx")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_package_json(self):
        """Validate package.json dependencies"""
        validation_name = "Package.json Dependencies"
        package_file = self.base_path / "package.json"
        
        if not package_file.exists():
            self.errors.append(f"{validation_name}: File not found - package.json")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(package_file, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}
            
            # Store for later import validation
            self.installed_packages = set(all_deps.keys())
            
            # Check required dependencies
            required_deps = [
                'react',
                'react-dom',
                'react-router-dom',
                'axios'
            ]
            
            for dep in required_deps:
                if dep not in all_deps:
                    file_errors.append(f"Missing required dependency: {dep}")
            
            # Check required dev dependencies
            required_dev_deps = [
                '@types/react',
                '@types/react-dom',
                '@vitejs/plugin-react',
                'typescript',
                'vite'
            ]
            
            for dep in required_dev_deps:
                if dep not in all_deps:
                    file_errors.append(f"Missing required dev dependency: {dep}")
            
            # Check scripts
            scripts = package_data.get('scripts', {})
            required_scripts = ['dev', 'build']
            
            for script in required_scripts:
                if script not in scripts:
                    file_errors.append(f"Missing script: {script}")
        
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
    
    def validate_no_previous_modifications(self):
        """Validate no modifications to previous stage files"""
        validation_name = "No Previous Stage Modifications"
        
        # This is a soft check - we validate that key files still exist and have expected structure
        # We can't fully guarantee no modifications without comparing to baseline
        
        critical_files = [
            "src/router/index.tsx",
            "src/router/routes.ts",
            "src/components/Layout.tsx",
            "src/components/Navbar.tsx",
            "src/services/api.ts"
        ]
        
        file_errors = []
        
        for file_path in critical_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                file_errors.append(f"Critical file missing or moved: {file_path}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
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
            
            for ext in ['.ts', '.tsx', '.js', '.jsx', '.css', '']:
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
        
        # Build export map for internal files
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = Path(root) / file
                exports = self._scan_file_exports(file_path)
                self.file_exports[file_path] = exports
        
        # Collect all external package imports
        external_imports = set()
        
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
                    # Handle relative imports (internal)
                    if from_path.startswith('.'):
                        # Skip CSS imports
                        if from_path.endswith('.css'):
                            continue
                        
                        resolved_path = self._resolve_import_path(file_path, from_path)
                        
                        if resolved_path is None:
                            import_errors.append(f"{rel_path}: Import path not found '{from_path}'")
                            continue
                        
                        # Skip CSS files
                        if str(resolved_path).endswith('.css'):
                            continue
                        
                        if resolved_path not in self.file_exports:
                            continue
                        
                        available_exports = self.file_exports[resolved_path]
                        
                        if '*' in available_exports:
                            continue
                        
                        for symbol in symbols:
                            if symbol not in available_exports and 'default' not in available_exports:
                                import_errors.append(f"{rel_path}: Symbol '{symbol}' not exported from '{from_path}'")
                    
                    # Handle external package imports
                    else:
                        # Extract base package name
                        package_name = self._extract_package_name(from_path)
                        if package_name:
                            external_imports.add(package_name)
        
        # Validate external imports against package.json
        if hasattr(self, 'installed_packages'):
            for package in external_imports:
                if package not in self.installed_packages:
                    import_errors.append(f"Package '{package}' is imported but not in package.json dependencies")
        
        if import_errors:
            for error in import_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def _extract_package_name(self, import_path: str) -> Optional[str]:
        """Extract package name from import path"""
        # Handle scoped packages like @vitejs/plugin-react
        if import_path.startswith('@'):
            parts = import_path.split('/')
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            return parts[0]
        
        # Handle regular packages like react, react-dom/client
        parts = import_path.split('/')
        return parts[0] if parts else None
    
    def validate_route_view_matching(self):
        """Validate that all views have corresponding routes defined"""
        validation_name = "Route-View Matching"
        
        views_path = self.base_path / "src" / "views"
        routes_file = self.base_path / "src" / "router" / "routes.ts"
        router_file = self.base_path / "src" / "router" / "index.tsx"
        
        if not views_path.exists():
            self.validation_results[validation_name] = True
            return
        
        if not routes_file.exists():
            self.errors.append(f"{validation_name}: routes.ts not found")
            self.validation_results[validation_name] = False
            return
        
        if not router_file.exists():
            self.errors.append(f"{validation_name}: router/index.tsx not found")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            # Get all view files
            view_files = []
            for view_file in views_path.glob("*.tsx"):
                view_name = view_file.stem
                # Skip Home and NotFound as they have special routes
                if view_name not in ['Home', 'NotFound']:
                    view_files.append(view_name)
            
            # Read routes.ts
            with open(routes_file, 'r', encoding='utf-8') as f:
                routes_content = f.read()
            
            # Read router/index.tsx
            with open(router_file, 'r', encoding='utf-8') as f:
                router_content = f.read()
            
            # Check each view has a route definition
            for view_name in view_files:
                # Check in routes.ts (e.g., USER: '/user' for UserView)
                entity_name = view_name.replace('View', '')
                route_constant = entity_name.upper()
                
                if not re.search(rf"{route_constant}\s*:", routes_content):
                    file_errors.append(f"View '{view_name}' missing route constant in routes.ts")
                
                # Check view is imported in router/index.tsx
                if not re.search(rf"import.*{view_name}.*from.*views", router_content):
                    file_errors.append(f"View '{view_name}' not imported in router/index.tsx")
                
                # Check view is used in a Route component
                if not re.search(rf"<Route.*element=\{{<{view_name}", router_content):
                    file_errors.append(f"View '{view_name}' not used in any Route in router/index.tsx")
        
        except Exception as e:
            file_errors.append(f"Error validating routes: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_html_location(self):
        """Validate that index.html is in project root"""
        validation_name = "HTML Template Location"
        
        # Check in project root (generated_project/)
        root_html = self.base_path / "index.html"
        
        if not root_html.exists():
            self.errors.append(f"{validation_name}: index.html not found in project root (generated_project/)")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_storage_exports(self):
        """Validate that tokenStorage is exported from storage.ts"""
        validation_name = "Storage Exports"
        storage_file = self.base_path / "src" / "utils" / "storage.ts"
        
        if not storage_file.exists():
            self.validation_results[validation_name] = True
            return
        
        file_errors = []
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if tokenStorage is exported
            if not re.search(r"export.*tokenStorage", content):
                file_errors.append("tokenStorage not exported from storage.ts")
        
        except Exception as e:
            file_errors.append(f"Error reading storage.ts: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_component_barrel_exports(self):
        """Validate that entity components are exported from components/index.ts"""
        validation_name = "Component Barrel Exports"
        components_index = self.base_path / "src" / "components" / "index.ts"
        components_dir = self.base_path / "src" / "components"
        
        if not components_dir.exists() or not components_index.exists():
            self.validation_results[validation_name] = True
            return
        
        file_errors = []
        
        try:
            # Find all component files
            component_files = []
            for component_file in components_dir.glob("*.tsx"):
                component_name = component_file.stem
                # Skip Layout, Navbar, Sidebar
                if component_name not in ['Layout', 'Navbar', 'Sidebar']:
                    component_files.append(component_name)
            
            # Read barrel export file
            with open(components_index, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check each component is exported
            for component_name in component_files:
                if not re.search(rf"export.*{component_name}", content):
                    file_errors.append(f"Component '{component_name}' not exported from components/index.ts")
        
        except Exception as e:
            file_errors.append(f"Error validating component exports: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_inputs():
            return False
        
        # Run all validations silently
        self.validate_app_component()
        self.validate_main_entry()
        self.validate_app_css()
        self.validate_index_css()
        self.validate_auth_context()
        self.validate_context_barrel_exports()
        self.validate_html_template()
        self.validate_html_location()  # NEW: Check index.html is in project root
        self.validate_package_json()  # Must run before validate_imports
        self.validate_no_previous_modifications()
        self.validate_route_view_matching()  # NEW: Check views match routes
        self.validate_storage_exports()  # NEW: Check tokenStorage export
        self.validate_component_barrel_exports()  # NEW: Check entity components exported
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
        
        # Print validation statistics
        print_section("VALIDATION STATISTICS")
        
        # Count files scanned
        src_path = self.base_path / "src"
        ts_files = []
        if src_path.exists():
            for root, dirs, files in os.walk(src_path):
                dirs[:] = [d for d in dirs if d != 'node_modules']
                for file in files:
                    if file.endswith('.ts') or file.endswith('.tsx'):
                        ts_files.append(Path(root) / file)
        
        print_info(f"TypeScript files scanned: {len(ts_files)}")
        print_info(f"Files with exports validated: {len(self.file_exports)}")
        print_info(f"External packages detected: {len(self.installed_packages)}")
        
        # Final result
        print()
        if len(self.errors) > 0:
            print_error(f"VALIDATION FAILED: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
            return False
        else:
            print_success(f"✓ ALL VALIDATIONS PASSED")
            if len(self.warnings) > 0:
                print_info(f"Note: {len(self.warnings)} warning(s) found")
            print_info(f"Application shell integrated successfully")
            if self.auth_enabled:
                print_info("Authentication context enabled and configured")
            print_success("All imports validated against package.json")
            return True

def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_5_validator.py <erd.json> <openapi.json>")
        print_info("Example: python3 validators/stage_5_validator.py output/erd.json output/openapi.json")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage5Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()