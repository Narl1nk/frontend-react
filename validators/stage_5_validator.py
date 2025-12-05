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
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urlparse

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
        self.base_path = Path("generated_project").resolve()  # Normalize to absolute path
        
        # Track exported symbols and imports
        self.file_exports = {}
        self.file_imports = {}
        
        # Track auth requirements
        self.auth_enabled = False
        
        # Track installed packages
        self.installed_packages = set()
    
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
            with open(self.erd_path, 'r') as f:
                self.erd_data = json.load(f)
                business_logic = self.erd_data.get('business_logic', {})
                authentication = business_logic.get('authentication', {})
                self.auth_enabled = authentication.get('enabled', False)
            
            self.openapi_data = self.load_openapi_file(self.openapi_path)
            if self.openapi_data is None:
                print_error(f"Failed to load OpenAPI file: {self.openapi_path}")
                return False
            
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
            
            # Check for App component export (named or default)
            # Pattern 1: export const App or export function App
            has_named_export = bool(re.search(r"export\s+(const|function)\s+App\b", content))
            # Pattern 2: const/function App defined + export default App
            has_app_definition = bool(re.search(r"(const|function)\s+App\b", content))
            has_default_export_identifier = bool(re.search(r"export\s+default\s+App\b", content))
            # Pattern 3: export default function App or export default const App (inline)
            has_default_export_inline = bool(re.search(r"export\s+default\s+(function|const)\s+App\b", content))
            
            # Check for INVALID pattern: both definition + inline export (duplicate App)
            if has_app_definition and has_default_export_inline:
                file_errors.append("Invalid App export: Found both 'const/function App' definition AND 'export default function App'. Remove one - use EITHER 'const App = () => {}; export default App;' OR 'export default function App() {}'")
            # Valid if: named export OR (definition + default export) OR inline default export
            elif not (has_named_export or (has_app_definition and has_default_export_identifier) or has_default_export_inline):
                # Add detailed error message showing what was found
                debug_info = f"App export validation failed:\n"
                debug_info += f"  - has_named_export (export const/function App): {has_named_export}\n"
                debug_info += f"  - has_app_definition (const/function App): {has_app_definition}\n"
                debug_info += f"  - has_default_export_identifier (export default App): {has_default_export_identifier}\n"
                debug_info += f"  - has_default_export_inline (export default function/const App): {has_default_export_inline}\n"
                debug_info += f"  - File preview (first 500 chars):\n{content[:500]}"
                file_errors.append(f"Missing App component export\n{debug_info}")
            
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
            else:
                # Check if import matches export type in App.tsx
                app_file = self.base_path / "src" / "App.tsx"
                if app_file.exists():
                    try:
                        with open(app_file, 'r', encoding='utf-8') as f:
                            app_content = f.read()
                        
                        # Check how App is imported in main.tsx
                        has_named_import = bool(re.search(r"import\s*\{\s*App\s*\}", content))
                        has_default_import = bool(re.search(r"import\s+App\s+from", content))
                        
                        # Check how App is exported in App.tsx
                        has_named_export = bool(re.search(r"export\s+(const|function)\s+App\b", app_content))
                        has_default_export = bool(re.search(r"export\s+default", app_content))
                        
                        # Validate match
                        if has_named_import and not has_named_export:
                            file_errors.append("Import mismatch: main.tsx uses 'import { App }' but App.tsx uses 'export default'. Change to 'import App from './App''")
                        elif has_default_import and not has_default_export:
                            file_errors.append("Import mismatch: main.tsx uses 'import App from' but App.tsx uses 'export const App'. Change to 'import { App } from './App''")
                    except:
                        pass
            
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
    
    def validate_backend_api_matching(self):
        """Validate frontend API calls match OpenAPI backend spec"""
        validation_name = "Backend API Matching with the one defined inside input/openapi.json"
        
        api_errors = []
        
        try:
            # Extract backend URL from openapi.json - try multiple formats
            backend_url = None
            
            # Standard OpenAPI 3.0: servers array
            openapi_servers = self.openapi_data.get('servers', [])
            if openapi_servers and len(openapi_servers) > 0:
                backend_url = openapi_servers[0].get('url', '').rstrip('/')
            
            # Alternative: root-level url field
            if not backend_url:
                backend_url = self.openapi_data.get('url', '').rstrip('/')
            
            # Alternative: host + basePath (OpenAPI 2.0 / Swagger)
            if not backend_url:
                host = self.openapi_data.get('host', '')
                schemes = self.openapi_data.get('schemes', ['http'])
                basePath = self.openapi_data.get('basePath', '')
                if host:
                    backend_url = f"{schemes[0]}://{host}{basePath}".rstrip('/')
            
            if not backend_url:
                warning_msg = f"Could not find backend URL in openapi.json (checked: servers[].url, url, host+basePath)"
                self.warnings.append(f"{validation_name}: {warning_msg}")
                # Add any accumulated errors before returning
                if api_errors:
                    for error in api_errors:
                        self.errors.append(f"{validation_name}: {error}")
                    self.validation_results[validation_name] = False
                else:
                    self.validation_results[validation_name] = True
                return
            
            # Check .env file
            env_file = self.base_path / ".env"
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                
                env_match = re.search(r'VITE_API_BASE_URL\s*=\s*(.+)', env_content)
                if env_match:
                    env_url = env_match.group(1).strip().strip('"').strip("'").rstrip('/')
                    if env_url != backend_url:
                        api_errors.append(f".env URL mismatch: has '{env_url}', openapi.json expects '{backend_url}'")
                else:
                    api_errors.append(".env missing VITE_API_BASE_URL")
            else:
                api_errors.append(".env file not found")
            
            # Check API config uses environment variable
            api_config = self.base_path / "src" / "config" / "api.config.ts"
            api_base_path = ""  # Track if baseURL includes path prefix like /api
            
            if api_config.exists():
                with open(api_config, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                if 'import.meta.env.VITE_API_BASE_URL' not in config_content:
                    api_errors.append("api.config.ts not using import.meta.env.VITE_API_BASE_URL")
                
                # Check if baseURL has a path component (e.g., /api)
                # This affects how services should construct paths
                base_url_match = re.search(r'baseURL:\s*[\'"`]([^\'"`]+)[\'"`]', config_content)
                if base_url_match:
                    # Extract path from hardcoded URL if present
                    parsed = urlparse(base_url_match.group(1))
                    api_base_path = parsed.path.rstrip('/')
            
            # Extract API endpoints from openapi.json
            # Support both standard OpenAPI format and custom format
            openapi_paths = set()
            
            # Standard OpenAPI 3.0: paths object
            if 'paths' in self.openapi_data and isinstance(self.openapi_data['paths'], dict):
                openapi_paths = set(self.openapi_data['paths'].keys())
            
            # Custom format: endpoints array
            elif 'endpoints' in self.openapi_data:
                endpoints_data = self.openapi_data['endpoints']
                if isinstance(endpoints_data, list):
                    for endpoint in endpoints_data:
                        if isinstance(endpoint, dict) and 'path' in endpoint:
                            openapi_paths.add(endpoint['path'])
                elif isinstance(endpoints_data, dict):
                    openapi_paths = set(endpoints_data.keys())
            
            # Alternative: routes key
            elif 'routes' in self.openapi_data:
                routes_data = self.openapi_data['routes']
                if isinstance(routes_data, dict):
                    openapi_paths = set(routes_data.keys())
            
            # Collect all frontend endpoints from service files
            frontend_endpoints = {}
            services_dir = self.base_path / "src" / "services"
            
            if services_dir.exists():
                for service_file in services_dir.glob("*.service.ts"):
                    if service_file.name == 'api.ts':
                        continue
                    try:
                        with open(service_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Extract endpoints - handle both {id} and ${id} syntax
                        endpoints = re.findall(r'api\.\w+\([\'"`](/[^\'"` ]+)[\'"`]', content)
                        if endpoints:
                            frontend_endpoints[service_file.name] = endpoints
                    except:
                        pass
            
            if not openapi_paths:
                # Show comparison even when no backend paths found
                print("\n" + "="*70)
                print("  ❌ BACKEND API VALIDATION FAILED")
                print("="*70)
                
                print(f"\n  📁 BACKEND ENDPOINTS: None found in openapi.json")
                print(f"     → Checked: 'paths', 'endpoints', 'routes' keys")
                
                print(f"\n  💻 FRONTEND ENDPOINTS:")
                if frontend_endpoints:
                    for service, endpoints in sorted(frontend_endpoints.items()):
                        print(f"     {service}:")
                        for ep in endpoints:
                            print(f"       → {ep}")
                else:
                    print(f"     None found")
                
                print("="*70 + "\n")
                
                error_msg = "No API paths found in openapi.json - cannot validate service endpoints"
                api_errors.append(error_msg)
                for error in api_errors:
                    self.errors.append(f"{validation_name}: {error}")
                self.validation_results[validation_name] = False
                return
            
            # Determine if OpenAPI paths have a common prefix (like /api)
            openapi_prefix = ""
            if openapi_paths:
                sample_paths = list(openapi_paths)
                # Check if ALL paths start with same prefix
                if all(p.startswith('/api/') or p == '/api' for p in sample_paths):
                    openapi_prefix = "/api"
            
            # Check service files for endpoint mismatches AND proper API client usage
            services_dir = self.base_path / "src" / "services"
            if not services_dir.exists():
                # If there are already errors collected, add them before returning
                if api_errors:
                    for error in api_errors:
                        self.errors.append(f"{validation_name}: {error}")
                    self.validation_results[validation_name] = False
                else:
                    # No services directory but also no other errors - this is OK
                    self.validation_results[validation_name] = True
                return
            
            service_files = list(services_dir.glob("*.service.ts"))
            
            if services_dir.exists():
                for service_file in services_dir.glob("*.service.ts"):
                    if service_file.name == 'api.ts':
                        continue
                    
                    try:
                        with open(service_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # CRITICAL: Check if service imports the API client
                        has_api_import = "from './api'" in content or 'from "./api"' in content or "from '../config/api" in content
                        
                        if not has_api_import:
                            api_errors.append(f"{service_file.name}: Missing API client import. Add: import {{ api }} from './api'")
                            continue
                        
                        # CRITICAL: Check if service actually uses the api client
                        api_calls = re.findall(r'\bapi\.(get|post|put|patch|delete)\(', content)
                        
                        if not api_calls:
                            api_errors.append(f"{service_file.name}: Imports 'api' but never calls api.get/post/put/delete methods")
                            continue
                        
                        # Check for direct axios usage (bypassing API client)
                        if re.search(r'\baxios\.(get|post|put|patch|delete)\(', content):
                            api_errors.append(f"{service_file.name}: Uses axios directly. Must use 'api.get()' not 'axios.get()' to apply baseURL")
                        
                        # Check for hardcoded full URLs
                        hardcoded = re.findall(r'[\'"`](https?://[^\'"`]+)[\'"`]', content)
                        if hardcoded:
                            api_errors.append(f"{service_file.name}: Contains hardcoded URL(s) {hardcoded}. Use 'api.get(\"/path\")' with relative paths")
                        
                        # CRITICAL: Extract and validate endpoint paths
                        # Handle multiple patterns:
                        # - api.get('/users') 
                        # - api.get(`/users/${id}`)
                        # - api.get( '/users' ) (with spaces)
                        endpoints_raw = re.findall(r'api\.\w+\(\s*[\'"`]([/][^\'"` ]*)[\'"`]\s*[,\)]', content)
                        
                        # Also try without requiring comma/paren at end (for edge cases)
                        if not endpoints_raw:
                            endpoints_raw = re.findall(r'api\.\w+\([\'"`](/[^\'"` ]+)[\'"`]', content)
                        
                        # Remove duplicates while preserving order
                        endpoints = []
                        seen = set()
                        for ep in endpoints_raw:
                            if ep not in seen:
                                endpoints.append(ep)
                                seen.add(ep)
                        
                        if not endpoints:
                            # Service uses api client but no endpoints found - might be a parsing issue
                            self.warnings.append(f"{validation_name}: {service_file.name} uses api client but no endpoints detected (check syntax)")
                            continue
                        
                        # Find line numbers for each endpoint
                        lines = content.split('\n')
                        
                        for endpoint in endpoints:
                            endpoint_clean = endpoint.rstrip('/')
                            
                            # Normalize endpoint for comparison: ${id} -> {id}
                            endpoint_normalized = re.sub(r'\$\{(\w+)\}', r'{\1}', endpoint_clean)
                            
                            # Find which line this endpoint is on
                            line_num = None
                            for i, line in enumerate(lines, 1):
                                if endpoint in line and 'api.' in line:
                                    line_num = i
                                    break
                            
                            # Construct full path as backend will see it
                            full_path = f"{api_base_path}{endpoint_normalized}"
                            
                            # Check if this full path exists in OpenAPI (with variations)
                            path_found = (
                                full_path in openapi_paths or
                                f"{full_path}/" in openapi_paths or
                                endpoint_normalized in openapi_paths or
                                f"{endpoint_normalized}/" in openapi_paths
                            )
                            
                            if not path_found:
                                # PATH MISMATCH - This is a CRITICAL ERROR
                                # Determine what the correct path should be
                                
                                location = f"{service_file.name}:{line_num}" if line_num else service_file.name
                                
                                # Case 1: OpenAPI has prefix but service endpoint doesn't
                                if openapi_prefix and not endpoint_normalized.startswith(openapi_prefix):
                                    correct_path = f"{openapi_prefix}{endpoint_normalized}"
                                    if correct_path in openapi_paths or f"{correct_path}/" in openapi_paths:
                                        api_errors.append(
                                            f"{location}: API endpoint mismatch\n"
                                            f"  ❌ Current: api.XXX('{endpoint}')\n"
                                            f"  ✓ Expected: api.XXX('{correct_path}')\n"
                                            f"  → Backend path: '{correct_path}'\n"
                                            f"  → Fix line {line_num}: Change '{endpoint}' to '{correct_path}'"
                                        )
                                    else:
                                        api_errors.append(
                                            f"{location}: Endpoint not found in backend\n"
                                            f"  → Frontend calls: '{endpoint}'\n"
                                            f"  → Backend has prefix: '{openapi_prefix}'\n"
                                            f"  → Available backend paths:\n" +
                                            '\n'.join(f"      • {p}" for p in sorted(openapi_paths)[:10])
                                        )
                                
                                # Case 2: baseURL already has path but service repeats it
                                elif api_base_path and endpoint_normalized.startswith(api_base_path):
                                    correct_path = endpoint_normalized.replace(api_base_path, '', 1)
                                    api_errors.append(
                                        f"{location}: Duplicate path prefix\n"
                                        f"  ❌ Current: api.XXX('{endpoint}')\n"
                                        f"  ✓ Expected: api.XXX('{correct_path}')\n"
                                        f"  → Reason: baseURL already includes '{api_base_path}'\n"
                                        f"  → Fix line {line_num}: Remove duplicate prefix"
                                    )
                                
                                # Case 3: Path simply not in OpenAPI
                                else:
                                    # Try to find similar paths
                                    endpoint_parts = endpoint_normalized.split('/')
                                    last_part = endpoint_parts[-1] if endpoint_parts else ''
                                    similar = [p for p in openapi_paths if last_part and last_part in p]
                                    
                                    error_msg = (
                                        f"{location}: Endpoint does not exist in backend\n"
                                        f"  ❌ Frontend calls: api.XXX('{endpoint}')\n"
                                        f"  → Normalized: '{endpoint_normalized}'\n"
                                        f"  → Full path: '{full_path}'\n"
                                        f"  → NOT FOUND in backend API\n"
                                    )
                                    if similar:
                                        error_msg += f"  → Similar backend paths:\n"
                                        error_msg += '\n'.join(f"      • {p}" for p in similar[:5])
                                        error_msg += f"\n  → Fix line {line_num}: Use correct backend path"
                                    else:
                                        error_msg += f"  → Available backend paths:\n"
                                        error_msg += '\n'.join(f"      • {p}" for p in sorted(openapi_paths)[:10])
                                        error_msg += f"\n  → Fix line {line_num}: Match one of the above"
                                    api_errors.append(error_msg)
                    except Exception as e:
                        api_errors.append(f"{service_file.name}: Failed to validate - {str(e)}")
        
        except Exception as e:
            api_errors.append(f"Validation error: {e}")
        
        # ALWAYS show endpoint comparison summary
        has_frontend_endpoints = 'frontend_endpoints' in locals() and frontend_endpoints
        has_backend_endpoints = 'openapi_paths' in locals() and openapi_paths
        
        if has_frontend_endpoints or has_backend_endpoints:
            print("\n" + "="*70)
            if api_errors:
                print("  ❌ BACKEND API ENDPOINT MISMATCH DETECTED")
            else:
                print("  ✓ BACKEND API ENDPOINT VALIDATION")
            print("="*70)
            
            # Show backend URL if available
            if 'backend_url' in locals() and backend_url:
                print(f"\n  🌐 Backend URL: {backend_url}")
            
            # Show available backend paths
            if has_backend_endpoints:
                print(f"\n  📁 Backend Endpoints (from openapi.json): {len(openapi_paths)} total")
                for path in sorted(openapi_paths):
                    print(f"     ✓ {path}")
            else:
                print(f"\n  📁 Backend Endpoints: None found in openapi.json")
            
            # Show frontend endpoints
            if has_frontend_endpoints:
                total_fe_endpoints = sum(len(eps) for eps in frontend_endpoints.values())
                print(f"\n  💻 Frontend Endpoints (from service files): {total_fe_endpoints} total")
                for service, endpoints in sorted(frontend_endpoints.items()):
                    print(f"     {service}: {len(endpoints)} endpoint(s)")
                    for ep in endpoints:
                        # Normalize for display
                        ep_normalized = re.sub(r'\$\{(\w+)\}', r'{\1}', ep)
                        # Check if matches backend
                        matches = ep_normalized in openapi_paths or f"{ep_normalized}/" in openapi_paths
                        status = "✓" if matches else "✗"
                        if ep != ep_normalized:
                            print(f"       {status} {ep} → {ep_normalized}")
                        else:
                            print(f"       {status} {ep}")
            else:
                print(f"\n  💻 Frontend Endpoints: None found in service files")
            
            if api_errors:
                print(f"\n  ❗ Mismatches Found: {len(api_errors)}")
                print("  " + "-"*66)
                
                # Collect files that need fixing
                files_to_fix = set()
                for i, error in enumerate(api_errors, 1):
                    print(f"\n  {i}. {error}")
                    # Extract filename if present
                    first_line = error.split('\n')[0]
                    if ':' in first_line:
                        file_loc = first_line.split(':')[0]
                        if file_loc.endswith('.ts'):
                            files_to_fix.add(file_loc)
                
                if files_to_fix:
                    print("\n" + "="*70)
                    print("  🔧 FILES REQUIRING FIXES:")
                    print("="*70)
                    for file in sorted(files_to_fix):
                        file_path = f"generated_project/src/services/{file}"
                        print(f"     → {file_path}")
                    print("="*70 + "\n")
            else:
                print(f"\n  ✓ All endpoints validated successfully")
                print("="*70 + "\n")
        
        if api_errors:
            for error in api_errors:
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
    
    def _scan_file_exports(self, file_path: Path, visited: Set[Path] = None) -> Set[str]:
        """Scan a TypeScript file for exported symbols"""
        # Normalize path to absolute resolved path
        file_path = file_path.resolve()
        
        # Check if already scanned and cached
        if file_path in self.file_exports:
            return self.file_exports[file_path]
        
        if visited is None:
            visited = set()
        
        # Prevent infinite recursion - return empty set but DON'T cache it
        # The first non-recursive call will cache the proper result
        if file_path in visited:
            return set()
        
        visited.add(file_path)
        exports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Direct exports
            named_exports = re.findall(r'export\s+(?:interface|type|const|let|var|function|class)\s+(\w+)', content)
            exports.update(named_exports)
            
            # Export declarations: export { foo, bar as baz } (NOT from another file)
            export_declarations = re.findall(r'export\s*\{\s*([^}]+)\s*\}(?!\s*from)', content)
            for decl in export_declarations:
                symbols = [s.strip().split(' as ')[-1].strip() for s in decl.split(',')]
                exports.update(symbols)
            
            # Named re-exports: export { foo, default as bar } from './file'
            named_reexports = re.findall(r'export\s*\{\s*([^}]+)\s*\}\s*from\s+[\'"]([^"\']+)[\'"]', content)
            for symbols_str, export_path in named_reexports:
                symbols = [s.strip().split(' as ')[-1].strip() for s in symbols_str.split(',')]
                exports.update(symbols)
            
            # Wildcard re-exports: export * from './file'
            wildcard_exports = re.findall(r'export\s+\*\s+from\s+[\'"]([^"\']+)[\'"]', content)
            if wildcard_exports:
                for export_path in wildcard_exports:
                    resolved_path = self._resolve_import_path(file_path, export_path)
                    if resolved_path and resolved_path.exists():
                        # Recursively get exports from that file (share visited set)
                        re_exported = self._scan_file_exports(resolved_path, visited)
                        # Wildcard re-exports don't include 'default'
                        exports.update(re_exported - {'default'})
            
            # Default export
            if re.search(r'export\s+default', content):
                exports.add('default')
        
        except Exception as e:
            # Log the error for debugging
            print(f"Warning: Failed to scan exports from {file_path}: {str(e)}", file=sys.stderr)
        
        # ALWAYS cache the result (even if empty due to error or circular dependency)
        self.file_exports[file_path] = exports
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
                    index_path = (resolved / 'index.ts').resolve()
                    if index_path.exists():
                        return index_path
                    index_path = (resolved / 'index.tsx').resolve()
                    if index_path.exists():
                        return index_path
                else:
                    file_with_ext = Path(str(resolved) + ext).resolve()
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
                
                file_path = (Path(root) / file).resolve()  # Normalize to absolute path
                # _scan_file_exports now caches internally, so just call it
                self._scan_file_exports(file_path)
                
                # Check for duplicate exports in this file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all named exports: export const/let/var/function/class X
                    named_exports = re.findall(r'export\s+(?:const|let|var|function|class)\s+(\w+)', content)
                    # Find all re-exports: export { X, Y, Z }
                    reexport_blocks = re.findall(r'export\s*\{\s*([^}]+)\s*\}(?!\s*from)', content)
                    reexported_names = set()
                    for block in reexport_blocks:
                        names = [s.strip().split(' as ')[0].strip() for s in block.split(',')]
                        reexported_names.update(names)
                    
                    # Check for duplicates
                    duplicates = set(named_exports) & reexported_names
                    if duplicates:
                        rel_path = str(file_path.relative_to(self.base_path))
                        for dup in duplicates:
                            duplicate_export_errors.append(f"{rel_path}: Duplicate export '{dup}' (exported with 'export const {dup}' AND 'export {{ {dup} }}'). Remove 'export {{ {dup} }}'")
                except Exception as e:
                    pass
        
        # Collect all external package imports
        external_imports = set()
        
        # Validate imports
        import_errors = []
        duplicate_export_errors = []
        
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            
            for file in files:
                if not (file.endswith('.ts') or file.endswith('.tsx')):
                    continue
                
                file_path = (Path(root) / file).resolve()  # Normalize to absolute path
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
                        
                        # Check for import/export type mismatch
                        if resolved_path.exists() and not resolved_path.name.startswith('index.'):
                            try:
                                with open(resolved_path, 'r', encoding='utf-8') as f:
                                    target_content = f.read()
                                
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    import_line = None
                                    for line in f:
                                        if from_path in line and 'import' in line:
                                            import_line = line
                                            break
                                
                                if import_line:
                                    for symbol in symbols:
                                        # Check if this is a named import: import { Symbol }
                                        is_named_import = bool(re.search(rf"import\s*\{{[^}}]*\b{symbol}\b[^}}]*\}}", import_line))
                                        # Check if this is a default import: import Symbol
                                        is_default_import = not is_named_import and bool(re.search(rf"import\s+{symbol}\b", import_line))
                                        
                                        if is_named_import:
                                            # Named import requires named export
                                            has_named_export = bool(re.search(rf"export\s+(const|function|class|interface|type)\s+{symbol}\b", target_content))
                                            if not has_named_export:
                                                has_default_export = bool(re.search(r"export\s+default", target_content))
                                                if has_default_export:
                                                    import_errors.append(f"{rel_path}: Import/export mismatch for '{symbol}' from '{from_path}'\n  → Import uses: import {{ {symbol} }}\n  → Export uses: export default\n  → Fix: Change import to 'import {symbol} from'{from_path}''")
                                        
                                        elif is_default_import:
                                            # Default import requires default export
                                            has_default_export = bool(re.search(r"export\s+default", target_content))
                                            if not has_default_export:
                                                has_named_export = bool(re.search(rf"export\s+(const|function|class)\s+{symbol}\b", target_content))
                                                if has_named_export:
                                                    import_errors.append(f"{rel_path}: Import/export mismatch for '{symbol}' from '{from_path}'\n  → Import uses: import {symbol}\n  → Export uses: export const/function {symbol}\n  → Fix: Change import to 'import {{ {symbol} }} from'{from_path}''")
                            except:
                                pass
                        
                        if resolved_path not in self.file_exports:
                            # File was not in export map - check why
                            # Show what was imported for context
                            requested_str = ', '.join(f"'{s}'" for s in symbols)
                            
                            # First check if the import refers to a directory
                            base_import_path = (file_path.parent / from_path.lstrip('./')).resolve()
                            
                            if base_import_path.is_dir():
                                # It's a directory - check for index files
                                index_ts = base_import_path / 'index.ts'
                                index_tsx = base_import_path / 'index.tsx'
                                
                                if index_ts.exists() or index_tsx.exists():
                                    # index file exists but wasn't scanned or has no exports
                                    actual_index = index_ts if index_ts.exists() else index_tsx
                                    try:
                                        with open(actual_index, 'r', encoding='utf-8') as f:
                                            content = f.read().strip()
                                        
                                        error_msg = f"{rel_path}: Import from directory '{from_path}'\n"
                                        error_msg += f"  → Requested imports: {requested_str}\n"
                                        
                                        if not content:
                                            error_msg += f"  → Issue: {actual_index.name} exists but is empty\n"
                                            error_msg += f"  → Fix: Add exports to {base_import_path.name}/{actual_index.name}"
                                        elif 'export' not in content:
                                            error_msg += f"  → Issue: {actual_index.name} exists but has no exports\n"
                                            error_msg += f"  → Fix: Add 'export * from' or 'export {{ ... }}' statements to {base_import_path.name}/{actual_index.name}"
                                        else:
                                            error_msg += f"  → Issue: {base_import_path.name}/{actual_index.name} exists but exports are incorrect or incomplete\n"
                                            error_msg += f"  → Fix: Ensure {actual_index.name} properly exports all required symbols"
                                        
                                        import_errors.append(error_msg.rstrip())
                                    except Exception as e:
                                        import_errors.append(f"{rel_path}: Import '{from_path}' is a directory. Found {actual_index.name} but failed to read it: {str(e)}")
                                else:
                                    # Directory exists but no index file
                                    error_msg = f"{rel_path}: Import from directory '{from_path}'\n"
                                    error_msg += f"  → Requested imports: {requested_str}\n"
                                    error_msg += f"  → Issue: Directory '{base_import_path.name}' exists but is missing index.ts or index.tsx\n"
                                    error_msg += f"  → Fix: Create {base_import_path.name}/index.ts with proper exports"
                                    import_errors.append(error_msg)
                            elif not resolved_path.exists():
                                # Neither file nor directory exists
                                error_msg = f"{rel_path}: Import path not found\n"
                                error_msg += f"  → Requested: '{from_path}'\n"
                                error_msg += f"  → Issue: Path does not exist (not a file or directory)\n"
                                error_msg += f"  → Fix: Check the import path is correct"
                                import_errors.append(error_msg)
                            elif resolved_path.name in ['index.ts', 'index.tsx']:
                                # This is a barrel export file that exists but failed to scan
                                try:
                                    with open(resolved_path, 'r', encoding='utf-8') as f:
                                        barrel_content = f.read().strip()
                                    
                                    error_msg = f"{rel_path}: Import from barrel file '{from_path}'\n"
                                    error_msg += f"  → Requested imports: {requested_str}\n"
                                    error_msg += f"  → File: {resolved_path.parent.name}/{resolved_path.name}\n"
                                    
                                    if not barrel_content:
                                        error_msg += f"  → Issue: Barrel file is empty\n"
                                        error_msg += f"  → Fix: Add exports to {resolved_path.parent.name}/{resolved_path.name}"
                                    elif 'export' not in barrel_content:
                                        error_msg += f"  → Issue: Barrel file has no exports\n"
                                        error_msg += f"  → Fix: Add 'export * from' statements to {resolved_path.parent.name}/{resolved_path.name}"
                                    else:
                                        error_msg += f"  → Issue: Barrel file exists but exports are incorrect or incomplete\n"
                                        error_msg += f"  → Current content:\n"
                                        for line in barrel_content.split('\n')[:5]:  # Show first 5 lines
                                            error_msg += f"      {line}\n"
                                        error_msg += f"  → Fix: Ensure {resolved_path.name} exports all required symbols"
                                    
                                    import_errors.append(error_msg.rstrip())
                                except Exception as e:
                                    import_errors.append(f"{rel_path}: Failed to read barrel file '{from_path}': {str(e)}")
                            else:
                                # Regular file exists but has no exports
                                error_msg = f"{rel_path}: Import from file '{from_path}'\n"
                                error_msg += f"  → Requested imports: {requested_str}\n"
                                error_msg += f"  → File: {resolved_path.name}\n"
                                error_msg += f"  → Issue: File exists but has no exports or failed to scan\n"
                                error_msg += f"  → Fix: Add 'export const/function/class' statements to {resolved_path.name}"
                                import_errors.append(error_msg)
                            continue
                        
                        available_exports = self.file_exports[resolved_path]
                        
                        # Debug: Show what we found if there's a mismatch
                        if any(s not in available_exports and 'default' not in available_exports for s in symbols):
                            # At least one symbol is missing - prepare detailed error
                            pass
                        
                        for symbol in symbols:
                            if symbol not in available_exports and 'default' not in available_exports:
                                # Provide detailed error with what was expected vs found
                                available_list = sorted(list(available_exports - {'default'}))
                                available_str = ', '.join(f"'{e}'" for e in available_list) if available_list else "(none)"
                                
                                error_msg = f"{rel_path}: Import mismatch for '{from_path}'\n"
                                error_msg += f"  → Requested: '{symbol}'\n"
                                error_msg += f"  → Available exports: {available_str}\n"
                                
                                # Try to give a helpful error message based on the situation
                                if resolved_path.name in ['index.ts', 'index.tsx']:
                                    try:
                                        with open(resolved_path, 'r', encoding='utf-8') as f:
                                            barrel_content = f.read()
                                        
                                        # Check if there's a wildcard re-export for this symbol
                                        if f"export * from './{symbol}" in barrel_content or f'export * from "./{symbol}' in barrel_content:
                                            error_msg += f"  → Issue: Barrel file has 'export * from './{symbol}'' but {symbol} file likely uses 'export default'\n"
                                            error_msg += f"  → Fix Option 1: Change {symbol}.tsx to use 'export const {symbol}' instead of 'export default'\n"
                                            error_msg += f"  → Fix Option 2: Change index.ts to 'export {{ default as {symbol} }} from './{symbol}''"
                                        else:
                                            error_msg += f"  → Issue: Symbol '{symbol}' is not exported from {resolved_path.parent.name}/{resolved_path.name}\n"
                                            error_msg += f"  → Fix: Add 'export * from './{symbol}'' or 'export {{ default as {symbol} }} from './{symbol}'' to {resolved_path.name}"
                                    except Exception as e:
                                        error_msg += f"  → Issue: Symbol not found in barrel export file"
                                else:
                                    error_msg += f"  → Fix: Add 'export const {symbol}' or 'export function {symbol}' to {resolved_path.name}"
                                
                                import_errors.append(error_msg.rstrip())
                    
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
        
        # Add all errors
        all_errors = duplicate_export_errors + import_errors
        
        if all_errors:
            for error in all_errors:
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
                # Extract entity name from view (e.g., 'User' from 'UserView')
                base_name = view_name.replace('View', '')
                
                # Convert camelCase to SNAKE_CASE for matching
                # e.g., 'UserForm' -> 'USER_FORM', 'UserList' -> 'USER_LIST'
                snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', base_name).upper()
                
                # Try multiple naming patterns for route constants:
                # 1. EXACT_SNAKE_CASE: (e.g., USER_FORM:)
                # 2. EXACT_SNAKE_CASE_VIEW: (e.g., USER_FORM_VIEW:)
                # 3. Any constant containing the snake_case pattern
                
                patterns = [
                    rf"\b{snake_case}\s*:",           # USER_FORM:
                    rf"\b{snake_case}_VIEW\s*:",      # USER_FORM_VIEW:
                    rf"\b{snake_case}_[A-Z_]+\s*:",   # USER_FORM_SOMETHING:
                ]
                
                found = False
                for pattern in patterns:
                    if re.search(pattern, routes_content):
                        found = True
                        break
                
                if not found:
                    file_errors.append(f"View '{view_name}' missing route constant in routes.ts (expected: {snake_case}* constant)")
                
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
        self.validate_backend_api_matching()  # NEW: Check frontend matches backend API
        self.validate_no_previous_modifications()
        self.validate_route_view_matching()  # NEW: Check views match routes
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
        
        # Determine overall success based on validation results
        all_passed = len(failed) == 0
        
        # Final result
        print()
        # Determine overall success based on validation results
        all_passed = len(failed) == 0
        
        if not all_passed:
            print_error(f"✗ VALIDATION FAILED")
            print_error(f"  → {len(failed)} validation(s) failed")
            print_error(f"  → {len(self.errors)} total error(s)")
            if len(self.warnings) > 0:
                print_warning(f"  → {len(self.warnings)} warning(s)")
            print()
            print_error("Failed validations:")
            for validation in failed:
                print(f"  ✗ {validation}")
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
        if not all_passed:
            print_error(f"✗ VALIDATION FAILED")
            print_error(f"  → {len(failed)} validation(s) failed")
            print_error(f"  → {len(self.errors)} total error(s)")
            if len(self.warnings) > 0:
                print_warning(f"  → {len(self.warnings)} warning(s)")
            print()
            print_error("Failed validations:")
            for validation in failed:
                print(f"  ✗ {validation}")
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


    def validate_stage_output(self):
        """Validate all stage outputs - gather from stages 2-5 and verify completeness"""
        print_section("STAGE OUTPUT VALIDATION (ALL STAGES)")
        
        # Gather all documented files from all stages
        all_documented_files = set()
        stages_found = []
        
        for stage in [2, 3, 4, 5]:
            output_file = Path(f"output/stage_{stage}_output.json")
            
            if not output_file.exists():
                print_warning(f"output/stage_{stage}_output.json not found (skipping)")
                continue
            
            try:
                with open(output_file, 'r') as f:
                    output_data = json.load(f)
                
                if 'files' not in output_data:
                    print_error(f"stage_{stage}_output.json missing 'files' key")
                    continue
                
                stage_files = set(output_data['files'].keys())
                all_documented_files.update(stage_files)
                stages_found.append(stage)
                print_info(f"Stage {stage}: {len(stage_files)} files documented")
                
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON in stage_{stage}_output.json: {e}")
            except Exception as e:
                print_error(f"Error reading stage_{stage}_output.json: {e}")
        
        if not stages_found:
            print_error("No stage output files found")
            return
        
        print_info(f"Total documented files across stages {stages_found}: {len(all_documented_files)}")
        
        # Scan all actual files in generated_project
        actual_files = set()
        base_path = Path("generated_project")
        
        if not base_path.exists():
            print_error("generated_project directory not found")
            return
        
        # Scan src directory for TypeScript files
        src_path = base_path / "src"
        if src_path.exists():
            for root, dirs, files in os.walk(src_path):
                # Skip node_modules and other build directories
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '.vite']]
                
                for file in files:
                    if file.endswith(('.ts', '.tsx', '.css')) and not file.endswith('.d.ts'):
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(base_path)
                        actual_files.add(str(rel_path))
        
        # Check root-level files
        for file_name in ['index.html', '.env', '.env.example', 'vite.config.ts', 'tsconfig.json']:
            file_path = base_path / file_name
            if file_path.exists():
                actual_files.add(file_name)
        
        print_info(f"Total actual files in project: {len(actual_files)}")
        
        # Bidirectional validation
        errors_found = False
        
        # Check 1: All documented files exist
        missing_files = []
        for doc_file in sorted(all_documented_files):
            file_path = base_path / doc_file
            if not file_path.exists():
                missing_files.append(doc_file)
        
        if missing_files:
            errors_found = True
            print_error(f"Documented files that don't exist ({len(missing_files)}):")
            for file in missing_files[:20]:  # Limit output
                print(f"  - {file}")
            if len(missing_files) > 20:
                print(f"  ... and {len(missing_files) - 20} more")
        
        # Check 2: All actual files are documented
        undocumented_files = actual_files - all_documented_files
        if undocumented_files:
            errors_found = True
            print_error(f"Generated files not documented in any stage ({len(undocumented_files)}):")
            for file in sorted(undocumented_files)[:20]:  # Limit output
                print(f"  - {file}")
            if len(undocumented_files) > 20:
                print(f"  ... and {len(undocumented_files) - 20} more")
        
        if not errors_found:
            print_success(f"✓ Perfect match: All {len(all_documented_files)} documented files exist")
            print_success(f"✓ Complete documentation: All {len(actual_files)} generated files documented")
        
        return not errors_found
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