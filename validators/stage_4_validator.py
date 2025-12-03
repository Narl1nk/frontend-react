#!/usr/bin/env python3
"""
Stage 4 Validator - Routing & Navigation Validator

Validates that routing and navigation layer is correctly generated

CRITICAL VALIDATIONS:
1. Home view created
2. NotFound view created
3. Route definitions (routes.ts)
4. Router setup (router/index.tsx)
5. Layout component
6. Navbar component
7. Sidebar component (conditional)
8. React Router v6 syntax
9. Barrel exports updated
10. TypeScript types
11. No duplicate entity views
12. Import validation
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

class Stage4Validator:
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
        
        # Track entity views
        self.entity_views = []
        self.entities = []
        
    def load_inputs(self) -> bool:
        """Load ERD and OpenAPI files"""
        try:
            with open(self.erd_path, 'r') as f:
                self.erd_data = json.load(f)
                self.entities = [entity.get('name') for entity in self.erd_data.get('entities', [])]
            
            with open(self.openapi_path, 'r') as f:
                self.openapi_data = json.load(f)
            
            # Scan existing entity views
            views_path = self.base_path / "src" / "views"
            if views_path.exists():
                for view_file in views_path.glob("*View.tsx"):
                    view_name = view_file.stem
                    self.entity_views.append(view_name)
            
            return True
        except Exception as e:
            self.errors.append(f"Error loading inputs: {e}")
            return False
    
    def validate_home_view(self):
        """Validate Home view exists"""
        validation_name = "Home View"
        home_file = self.base_path / "src" / "views" / "Home.tsx"
        
        if not home_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/views/Home.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(home_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for component export
            if not re.search(r"export\s+(const|function)\s+Home", content):
                file_errors.append("Missing Home component export")
            
            # Check for React Router Link import
            if not re.search(r"import.*Link.*from\s+['\"]react-router-dom['\"]", content):
                self.warnings.append(f"{validation_name}: Should use Link from react-router-dom")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_notfound_view(self):
        """Validate NotFound view exists"""
        validation_name = "NotFound View"
        notfound_file = self.base_path / "src" / "views" / "NotFound.tsx"
        
        if not notfound_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/views/NotFound.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(notfound_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for component export
            if not re.search(r"export\s+(const|function)\s+NotFound", content):
                file_errors.append("Missing NotFound component export")
            
            # Check for React Router Link import
            if not re.search(r"import.*Link.*from\s+['\"]react-router-dom['\"]", content):
                self.warnings.append(f"{validation_name}: Should use Link from react-router-dom")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_route_definitions(self):
        """Validate route definitions file"""
        validation_name = "Route Definitions"
        routes_file = self.base_path / "src" / "router" / "routes.ts"
        
        if not routes_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/router/routes.ts")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for ROUTES export
            if not re.search(r"export\s+const\s+ROUTES", content):
                file_errors.append("Missing ROUTES constant export")
            
            # Check for HOME route
            if not re.search(r"HOME\s*:\s*['\"]\/['\"]", content):
                file_errors.append("Missing HOME route definition")
            
            # Check for NOT_FOUND route
            if not re.search(r"NOT_FOUND\s*:\s*['\"]?\*['\"]?", content):
                file_errors.append("Missing NOT_FOUND route definition")
            
            # Check that all entity views have routes
            for entity_view in self.entity_views:
                entity_name = entity_view.replace('View', '')
                route_pattern = rf"{entity_name.upper()}\s*:"
                if not re.search(route_pattern, content, re.IGNORECASE):
                    file_errors.append(f"Missing route definition for {entity_view}")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_router_setup(self):
        """Validate router setup file"""
        validation_name = "Router Setup"
        router_file = self.base_path / "src" / "router" / "index.tsx"
        
        if not router_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/router/index.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React Router v6 imports
            if not re.search(r"import.*\{.*BrowserRouter.*\}.*from\s+['\"]react-router-dom['\"]", content):
                file_errors.append("Missing BrowserRouter import from react-router-dom")
            
            if not re.search(r"import.*\{.*Routes.*\}.*from\s+['\"]react-router-dom['\"]", content):
                file_errors.append("Missing Routes import from react-router-dom")
            
            if not re.search(r"import.*\{.*Route.*\}.*from\s+['\"]react-router-dom['\"]", content):
                file_errors.append("Missing Route import from react-router-dom")
            
            # Check for Layout import
            if not re.search(r"import.*Layout.*from", content):
                file_errors.append("Missing Layout component import")
            
            # Check for view imports
            if not re.search(r"import.*Home.*from", content):
                file_errors.append("Missing Home view import")
            
            if not re.search(r"import.*NotFound.*from", content):
                file_errors.append("Missing NotFound view import")
            
            # Check for ROUTES import
            if not re.search(r"import.*ROUTES.*from.*routes", content):
                file_errors.append("Missing ROUTES import from routes.ts")
            
            # Check for React Router v6 syntax (Routes/Route, not Switch)
            if re.search(r"<Switch", content):
                file_errors.append("Using React Router v5 Switch - should use v6 Routes")
            
            if not re.search(r"<Routes>", content):
                file_errors.append("Missing <Routes> component (React Router v6)")
            
            if not re.search(r"<Route.*path=.*element=", content):
                file_errors.append("Missing Route with element prop (React Router v6 syntax)")
            
            # Check for BrowserRouter
            if not re.search(r"<BrowserRouter>", content):
                file_errors.append("Missing <BrowserRouter> wrapper")
            
            # Check for Layout wrapper
            if not re.search(r"<Layout>", content):
                file_errors.append("Missing <Layout> wrapper around routes")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_layout_component(self):
        """Validate Layout component"""
        validation_name = "Layout Component"
        layout_file = self.base_path / "src" / "components" / "Layout.tsx"
        
        if not layout_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/components/Layout.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(layout_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for Layout component export
            if not re.search(r"export\s+(const|function)\s+Layout", content):
                file_errors.append("Missing Layout component export")
            
            # Check for children prop
            if not re.search(r"children.*React\.ReactNode", content):
                file_errors.append("Missing children prop with ReactNode type")
            
            # Check for Navbar import
            if not re.search(r"import.*Navbar.*from", content):
                file_errors.append("Missing Navbar import")
            
            # Check for Navbar usage
            if not re.search(r"<Navbar\s*/?>", content):
                file_errors.append("Navbar component not used in Layout")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_navbar_component(self):
        """Validate Navbar component"""
        validation_name = "Navbar Component"
        navbar_file = self.base_path / "src" / "components" / "Navbar.tsx"
        
        if not navbar_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/components/Navbar.tsx")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(navbar_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for Navbar component export
            if not re.search(r"export\s+(const|function)\s+Navbar", content):
                file_errors.append("Missing Navbar component export")
            
            # Check for React Router Link import
            if not re.search(r"import.*Link.*from\s+['\"]react-router-dom['\"]", content):
                file_errors.append("Missing Link import from react-router-dom")
            
            # Check for ROUTES import
            if not re.search(r"import.*ROUTES.*from.*routes", content):
                self.warnings.append(f"{validation_name}: Should import ROUTES from router/routes")
            
            # Check for Link usage
            if not re.search(r"<Link\s+to=", content):
                file_errors.append("No Link components found - should link to entity views")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_sidebar_component(self):
        """Validate Sidebar component (if needed)"""
        validation_name = "Sidebar Component"
        sidebar_file = self.base_path / "src" / "components" / "Sidebar.tsx"
        
        # Sidebar only required if more than 3 entities
        if len(self.entities) <= 3:
            self.validation_results[validation_name] = True
            return
        
        if not sidebar_file.exists():
            self.errors.append(f"{validation_name}: File not found - src/components/Sidebar.tsx (required for {len(self.entities)} entities)")
            self.validation_results[validation_name] = False
            return
        
        file_errors = []
        
        try:
            with open(sidebar_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for React import
            if not re.search(r"import.*React.*from\s+['\"]react['\"]", content):
                file_errors.append("Missing React import")
            
            # Check for Sidebar component export
            if not re.search(r"export\s+(const|function)\s+Sidebar", content):
                file_errors.append("Missing Sidebar component export")
            
            # Check for React Router imports (Link, useLocation)
            if not re.search(r"import.*Link.*from\s+['\"]react-router-dom['\"]", content):
                file_errors.append("Missing Link import from react-router-dom")
            
            if not re.search(r"import.*useLocation.*from\s+['\"]react-router-dom['\"]", content):
                self.warnings.append(f"{validation_name}: Should use useLocation for active route highlighting")
        
        except Exception as e:
            file_errors.append(f"Error reading file: {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_barrel_exports(self):
        """Validate barrel exports are updated"""
        validation_name = "Barrel Exports"
        file_errors = []
        
        # Check views/index.ts
        views_index = self.base_path / "src" / "views" / "index.ts"
        if not views_index.exists():
            file_errors.append("Missing src/views/index.ts")
        else:
            try:
                with open(views_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Home export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/Home['\"]", content):
                    file_errors.append("views/index.ts: Missing export for Home")
                
                # Check for NotFound export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/NotFound['\"]", content):
                    file_errors.append("views/index.ts: Missing export for NotFound")
                
                # Check that entity views are still exported
                for entity_view in self.entity_views:
                    export_pattern = rf"export\s+\*\s+from\s+['\"]\./{entity_view}['\"]"
                    if not re.search(export_pattern, content):
                        self.warnings.append(f"Barrel Exports: views/index.ts should export {entity_view}")
            
            except Exception as e:
                file_errors.append(f"views/index.ts: Error reading file - {e}")
        
        # Check components/index.ts
        components_index = self.base_path / "src" / "components" / "index.ts"
        if not components_index.exists():
            file_errors.append("Missing src/components/index.ts")
        else:
            try:
                with open(components_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Layout export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/Layout['\"]", content):
                    file_errors.append("components/index.ts: Missing export for Layout")
                
                # Check for Navbar export
                if not re.search(r"export\s+\*\s+from\s+['\"]\.\/Navbar['\"]", content):
                    file_errors.append("components/index.ts: Missing export for Navbar")
                
                # Check for Sidebar export (if needed)
                if len(self.entities) > 3:
                    if not re.search(r"export\s+\*\s+from\s+['\"]\.\/Sidebar['\"]", content):
                        file_errors.append("components/index.ts: Missing export for Sidebar")
            
            except Exception as e:
                file_errors.append(f"components/index.ts: Error reading file - {e}")
        
        if file_errors:
            for error in file_errors:
                self.errors.append(f"{validation_name}: {error}")
            self.validation_results[validation_name] = False
        else:
            self.validation_results[validation_name] = True
    
    def validate_no_duplicate_views(self):
        """Validate no duplicate entity views were created"""
        validation_name = "No Duplicate Views"
        
        views_path = self.base_path / "src" / "views"
        if not views_path.exists():
            self.validation_results[validation_name] = True
            return
        
        # Count occurrences of each view file
        view_files = {}
        for view_file in views_path.glob("*.tsx"):
            view_name = view_file.stem
            if view_name not in view_files:
                view_files[view_name] = 0
            view_files[view_name] += 1
        
        duplicates = []
        for view_name, count in view_files.items():
            if count > 1:
                duplicates.append(f"{view_name}.tsx appears {count} times")
        
        if duplicates:
            for dup in duplicates:
                self.errors.append(f"{validation_name}: {dup}")
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
        self.validate_home_view()
        self.validate_notfound_view()
        self.validate_route_definitions()
        self.validate_router_setup()
        self.validate_layout_component()
        self.validate_navbar_component()
        self.validate_sidebar_component()
        self.validate_barrel_exports()
        self.validate_no_duplicate_views()
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
            print_info(f"Validated routing for {len(self.entity_views)} entity views")
            return True

def main():
    if len(sys.argv) != 3:
        print_error("Usage: python3 stage_4_validator.py <erd.json> <openapi.json>")
        print_info("Example: python3 validators/stage_4_validator.py output/erd.json output/openapi.json")
        sys.exit(1)
    
    erd_path = sys.argv[1]
    openapi_path = sys.argv[2]
    
    if not os.path.exists(erd_path):
        print_error(f"ERD file not found: {erd_path}")
        sys.exit(1)
    
    if not os.path.exists(openapi_path):
        print_error(f"OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    validator = Stage4Validator(erd_path, openapi_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()