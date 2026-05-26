from typing import Any

class FrontendCodeGenerator:
    """
    Frontend SPA Component Generator.
    Converts a compiled UISchema into a functional React component structure with TailwindCSS / custom styling bindings.
    """

    def generate(self, schema: Any) -> str:
        lines = []
        lines.append(f"// ========================================================")
        lines.append(f"// REACT SPA FRONTEND FOR {schema.app_name.upper()}")
        lines.append(f"// Theme: {schema.ui_schema.pages[0].layout if schema.ui_schema.pages else 'Glassmorphism Theme'}")
        lines.append(f"// Generated At: {schema.generated_at}")
        lines.append(f"// ========================================================\n")
        
        lines.append("import React, { useState, useEffect } from 'react';")
        lines.append("import { Activity, Shield, CreditCard, User, Layers, ArrowRight } from 'lucide-react';")
        
        # 1. State Hub
        lines.append("\nexport default function App() {")
        lines.append("  const [activeTab, setActiveTab] = useState('/');")
        lines.append("  const [userRole, setUserRole] = useState('user'); // user, premium, admin")
        lines.append("  const [token, setToken] = useState(null);")
        
        # 2. Add sub-states for entities
        for table in schema.db_schema.tables:
            if table.name == "user":
                continue
            lines.append(f"  const [{table.name}s, set{table.name.capitalize()}s] = useState([]);")

        lines.append("\n  // Render dynamic page matching active route")
        lines.append("  const renderPage = () => {")
        lines.append("    switch (activeTab) {")

        # 3. Compile page components
        for page in schema.ui_schema.pages:
            lines.append(f"      case '{page.path}':")
            lines.append(f"        return <{page.name.replace(' ', '')}Page ")
            lines.append(f"          role={{userRole}} ")
            
            # Pass down entities states
            for table in schema.db_schema.tables:
                if table.name == "user":
                    continue
                lines.append(f"          {table.name}s={{{table.name}s}} ")
                lines.append(f"          set{table.name.capitalize()}s={{set{table.name.capitalize()}s}} ")
                
            lines.append("        />;")

        lines.append("      default:")
        lines.append("        return <div className=\"p-8 text-white\">Page Not Found</div>;")
        lines.append("    }")
        lines.append("  };")

        # Layout return
        lines.append("""
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Dynamic Glassmorphic Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-teal-400 flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(99,102,241,0.4)]">
              AC
            </div>
            <span className="font-extrabold text-xl bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
              {appName}
            </span>
          </div>

          <nav className="flex items-center gap-6">
            {pagesList}
          </nav>

          <div className="flex items-center gap-4 bg-slate-850 p-1.5 rounded-xl border border-slate-850">
            <span className="text-xs text-slate-400 pl-2">Role:</span>
            <select 
              value={userRole} 
              onChange={(e) => setUserRole(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2.5 py-1 text-white focus:outline-none"
            >
              <option value="user">User (Basic)</option>
              <option value="premium">Premium Pro</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
        </div>
      </header>

      {/* Main Sandbox Canvas */}
      <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
        {renderPage()}
      </main>
    </div>
  );
}
""".replace("{appName}", schema.app_name).replace("{pagesList}", "\n".join([
            f"            <button onClick={() => setActiveTab('" + p.path + "')} className={`text-sm font-semibold transition-all px-3 py-1.5 rounded-lg ${activeTab === '" + p.path + "' ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20' : 'text-slate-400 hover:text-slate-200'}`}>{p.name}</button>"
            for p in schema.ui_schema.pages
        ])))

        # 4. Write Individual Page Component boilerplates
        for page in schema.ui_schema.pages:
            pg_comp_name = page.name.replace(' ', '')
            lines.append(f"\n// ========================================================")
            lines.append(f"// PAGE COMPONENT: {page.name}")
            lines.append(f"// Path: {page.path}")
            lines.append(f"// Components: {page.components}")
            lines.append(f"// Protected: {page.protected} | Roles: {page.allowed_roles}")
            lines.append(f"// ========================================================")
            lines.append(f"function {pg_comp_name}Page({{ role, ...props }}) {{")
            
            # Auth lock check inside React
            if page.protected and page.allowed_roles:
                lines.append(f"  if (!{page.allowed_roles}.includes(role)) {{")
                lines.append("    return (")
                lines.append("      <div className=\"p-8 text-center bg-red-950/20 border border-red-500/20 rounded-2xl max-w-lg mx-auto mt-12\">")
                lines.append("        <Shield className=\"w-12 h-12 text-red-500 mx-auto mb-4\" />")
                lines.append("        <h3 className=\"text-lg font-bold text-white mb-2\">Access Restricted</h3>")
                lines.append(f"        <p className=\"text-sm text-slate-400\">Your active role '<b>{{role}}</b>' does not have permission to view this panel. Requires one of: {page.allowed_roles}</p>")
                lines.append("      </div>")
                lines.append("    );")
                lines.append("  }")

            # Body of component
            lines.append("\n  return (")
            lines.append("    <div className=\"space-y-6 animate-fade-in\">")
            lines.append("      <div className=\"flex items-center justify-between border-b border-slate-800 pb-4\">")
            lines.append("        <div>")
            lines.append(f"          <h1 className=\"text-2xl font-black bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent\">{page.name}</h1>")
            lines.append(f"          <p className=\"text-sm text-slate-400\">Interactive dashboard components for {page.name.lower()}</p>")
            lines.append("        </div>")
            lines.append("      </div>")

            # Page Layout Render
            lines.append("      <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">")
            lines.append("        {/* Left Section (Widgets) */}")
            lines.append("        <div className=\"md:col-span-2 space-y-6\">")
            
            # Draw widgets
            for component in page.components:
                if component in ["Navbar", "Footer"]:
                    continue
                lines.append(f"          <div className=\"bg-slate-900/40 backdrop-blur-md border border-slate-800/80 rounded-2xl p-6 shadow-xl\">")
                lines.append(f"            <h3 className=\"text-sm font-bold text-slate-400 uppercase tracking-wider mb-4\">Widget: {component}</h3>")
                lines.append(f"            <div className=\"text-xs text-slate-500 p-4 bg-slate-950/60 rounded-xl border border-slate-900\">")
                lines.append(f"              {component} interface simulated node successfully loaded.")
                lines.append(f"            </div>")
                lines.append(f"          </div>")
                
            lines.append("        </div>")
            
            # Right Section (Sidebar details)
            lines.append("        {/* Right Section (Layout Info) */}")
            lines.append("        <div className=\"space-y-6\">")
            lines.append("          <div className=\"bg-gradient-to-br from-indigo-900/10 to-teal-900/5 backdrop-blur-md border border-slate-800/80 rounded-2xl p-6\">")
            lines.append("            <h4 className=\"font-bold text-white mb-3\">Layout Meta</h4>")
            lines.append("            <ul className=\"text-xs space-y-2.5 text-slate-400\">")
            lines.append(f"              <li><b>Layout Mode:</b> {page.layout}</li>")
            lines.append(f"              <li><b>Auth Required:</b> {str(page.protected)}</li>")
            lines.append(f"              <li><b>Allowed Roles:</b> {', '.join(page.allowed_roles) if page.allowed_roles else 'Anyone'}</li>")
            lines.append("            </ul>")
            lines.append("          </div>")
            lines.append("        </div>")
            
            lines.append("      </div>")
            lines.append("    </div>")
            lines.append("  );")
            lines.append("}")

        return "\n".join(lines)
