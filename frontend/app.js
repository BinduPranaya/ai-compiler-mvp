/* ==========================================================================
   AI COMPILER MVP - INTERACTIVE CONTROLLER
   Manages presets, compiles pipelines, triggers logs, and drives simulator database.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Bindings
    const standardPresetsList = document.getElementById("standard-presets");
    const edgePresetsList = document.getElementById("edge-presets");
    const promptInput = document.getElementById("prompt-input");
    const compileBtn = document.getElementById("compile-btn");
    
    // Nodes
    const nodeIntent = document.getElementById("node-intent");
    const nodeDesign = document.getElementById("node-design");
    const nodeSchema = document.getElementById("node-schema");
    const nodeValidation = document.getElementById("node-validation");
    const nodeReady = document.getElementById("node-ready");
    const nodes = [nodeIntent, nodeDesign, nodeSchema, nodeValidation, nodeReady];

    // Metrics
    const metricsPanel = document.getElementById("metrics-panel");
    const valTime = document.getElementById("val-time");
    const valStatus = document.getElementById("val-status");
    const valRepairs = document.getElementById("val-repairs");
    const repairsCard = document.getElementById("repairs-card");

    // Viewports
    const resultsPanel = document.getElementById("results-panel");
    const sandboxPanel = document.getElementById("sandbox-panel");
    const logStream = document.getElementById("log-stream");
    const blueprintCode = document.getElementById("blueprint-code");
    const erdSyntax = document.getElementById("erd-syntax");

    // Code exports
    const sqlExportCode = document.getElementById("sql-export-code");
    const fastapiExportCode = document.getElementById("fastapi-export-code");
    const reactExportCode = document.getElementById("react-export-code");

    // Sandbox form
    const requestMethod = document.getElementById("request-method");
    const requestPath = document.getElementById("request-path");
    const requestBody = document.getElementById("request-body");
    const reqBodyEditorWrap = document.getElementById("req-body-editor-wrap");
    const apiRequestForm = document.getElementById("api-request-form");
    const apiResponseConsole = document.getElementById("api-response-console");
    const dbTablesInspector = document.getElementById("db-tables-inspector");
    const refreshDbBtn = document.getElementById("refresh-db-btn");
    const sandboxRole = document.getElementById("sandbox-role");

    // App state
    let activeBlueprint = null;

    // Load initial presets
    fetchPresets();

    // Event listener: Preset selection
    function fetchPresets() {
        fetch("/api/test-cases")
            .then(res => res.json())
            .then(data => {
                standardPresetsList.innerHTML = "";
                edgePresetsList.innerHTML = "";
                
                data.forEach(preset => {
                    const btn = document.createElement("button");
                    btn.className = "preset-item";
                    btn.innerText = preset.name;
                    btn.onclick = () => {
                        // Mark active class
                        document.querySelectorAll(".preset-item").forEach(b => b.classList.remove("active"));
                        btn.classList.add("active");
                        promptInput.value = preset.prompt;
                    };
                    
                    if (preset.category === "Edge Case") {
                        edgePresetsList.appendChild(btn);
                    } else {
                        standardPresetsList.appendChild(btn);
                    }
                });
            })
            .catch(err => console.error("Error loading test presets: ", err));
    }

    // Toggle POST request body editor
    requestMethod.addEventListener("change", () => {
        if (requestMethod.value === "POST") {
            reqBodyEditorWrap.style.display = "flex";
        } else {
            reqBodyEditorWrap.style.display = "none";
        }
    });

    // Handle compile click
    compileBtn.addEventListener("click", () => {
        const text = promptInput.value.trim();
        if (!text) {
            alert("Please input or select a natural language description first.");
            return;
        }

        // 1. Reset state indicators
        compileBtn.disabled = true;
        compileBtn.innerText = "Compiling...";
        resultsPanel.style.display = "none";
        sandboxPanel.style.display = "none";
        metricsPanel.style.display = "none";
        
        nodes.forEach(node => {
            node.className = "pipeline-node";
            node.querySelector(".node-status").innerText = "Idle";
        });

        // 2. Fetch compile API
        fetch("/api/compile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text })
        })
        .then(res => res.json())
        .then(data => {
            animateCompilation(data);
        })
        .catch(err => {
            compileBtn.disabled = false;
            compileBtn.innerHTML = '<span class="btn-text">Compile Blueprint</span><span class="btn-icon">🚀</span>';
            alert("Compiler crashed. Ensure server is running: python run.py");
        });
    });

    // Animate stage flows
    function animateCompilation(data) {
        let delay = 0;

        // Stage 1: Intent Extractor
        setTimeout(() => {
            nodeIntent.classList.add("active");
            nodeIntent.querySelector(".node-status").innerText = "Running";
        }, delay);
        delay += 1000;

        setTimeout(() => {
            nodeIntent.classList.remove("active");
            nodeIntent.classList.add("passed");
            nodeIntent.querySelector(".node-status").innerText = "Pass";
        }, delay);

        // Stage 2: System Design
        delay += 200;
        setTimeout(() => {
            nodeDesign.classList.add("active");
            nodeDesign.querySelector(".node-status").innerText = "Running";
        }, delay);
        delay += 900;

        setTimeout(() => {
            nodeDesign.classList.remove("active");
            nodeDesign.classList.add("passed");
            nodeDesign.querySelector(".node-status").innerText = "Pass";
        }, delay);

        // Stage 3: Schema Generation
        delay += 200;
        setTimeout(() => {
            nodeSchema.classList.add("active");
            nodeSchema.querySelector(".node-status").innerText = "Running";
        }, delay);
        delay += 1200;

        setTimeout(() => {
            nodeSchema.classList.remove("active");
            nodeSchema.classList.add("passed");
            nodeSchema.querySelector(".node-status").innerText = "Pass";
        }, delay);

        // Stage 4: Validation & Repair
        delay += 200;
        setTimeout(() => {
            nodeValidation.classList.add("active");
            nodeValidation.querySelector(".node-status").innerText = "Checking";
        }, delay);
        delay += 1100;

        setTimeout(() => {
            nodeValidation.classList.remove("active");
            
            const validationStatus = data.validation.status;
            const repairs = data.repairs_made;
            
            if (repairs && repairs.length > 0) {
                // Self-healing occurred!
                nodeValidation.classList.add("healed");
                nodeValidation.querySelector(".node-status").innerText = "Healed";
            } else if (validationStatus === "PASSED") {
                nodeValidation.classList.add("passed");
                nodeValidation.querySelector(".node-status").innerText = "Pass";
            } else {
                nodeValidation.classList.add("failed");
                nodeValidation.querySelector(".node-status").innerText = "Fail";
            }
        }, delay);

        // Stage 5: Ready
        delay += 300;
        setTimeout(() => {
            nodeReady.classList.add("active");
            nodeReady.querySelector(".node-status").innerText = "Deploying";
        }, delay);
        delay += 700;

        setTimeout(() => {
            nodeReady.classList.remove("active");
            nodeReady.classList.add("passed");
            nodeReady.querySelector(".node-status").innerText = "Active";

            // Enable compile button
            compileBtn.disabled = false;
            compileBtn.innerHTML = '<span class="btn-text">Compile Blueprint</span><span class="btn-icon">🚀</span>';
            
            // Show result panes
            loadCompilerBlueprints(data);
        }, delay);
    }

    // Fills views
    function loadCompilerBlueprints(data) {
        activeBlueprint = data;

        // Fills metrics
        metricsPanel.style.display = "grid";
        valTime.innerText = `${data.metrics.compilation_time_ms} ms`;
        valStatus.innerText = data.validation.status;
        valRepairs.innerText = data.repairs_made.length;

        if (data.validation.status === "PASSED") {
            valStatus.style.color = "var(--success)";
        } else {
            valStatus.style.color = "var(--danger)";
        }

        if (data.repairs_made.length > 0) {
            valRepairs.style.color = "var(--warning)";
            repairsCard.style.borderColor = "var(--warning)";
        } else {
            valRepairs.style.color = "var(--text-main)";
            repairsCard.style.borderColor = "var(--panel-border)";
        }

        // Fills tabs
        resultsPanel.style.display = "flex";
        blueprintCode.innerText = JSON.stringify(data.schema, null, 2);
        erdSyntax.innerText = data.generated_code.mermaid;

        // Fills code exporters
        sqlExportCode.innerText = data.generated_code.db_ddl;
        fastapiExportCode.innerText = data.generated_code.backend;
        reactExportCode.innerText = data.generated_code.frontend;

        // Fills terminal logs stream
        logStream.innerHTML = "";
        data.logs.forEach(log => {
            const entry = document.createElement("div");
            entry.className = "log-entry";
            entry.innerText = `[AI-COMPILER] ${log}`;
            logStream.appendChild(entry);
        });

        // Initialize sandbox details
        if (data.schema) {
            sandboxPanel.style.display = "flex";
            
            // Auto populate logical path endpoint
            const firstTable = data.schema.db_schema.tables.find(t => t.name !== "user");
            if (firstTable) {
                const pathName = firstTable.name === "category" ? "categories" : `${firstTable.name}s`;
                requestPath.value = `/api/${pathName}`;
            } else {
                requestPath.value = "/api/users";
            }
            
            // Redraw database tables
            refreshVirtualDB();
        }
    }

    // Tab Switches
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });

    // Code Exporter Tab Switches
    document.querySelectorAll(".code-tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".code-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".code-tab-content").forEach(c => c.classList.remove("active"));
            
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-code");
            document.getElementById(targetId).classList.add("active");
        });
    });

    // Execute Sandbox request
    apiRequestForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const method = requestMethod.value;
        const path = requestPath.value.trim();
        const role = sandboxRole.value;
        let payload = null;

        if (method === "POST" && requestBody.value.trim()) {
            try {
                payload = JSON.parse(requestBody.value.trim());
            } catch (err) {
                alert("Invalid JSON request body format.");
                return;
            }
        }

        apiResponseConsole.innerText = "Executing simulated route...";

        fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                method: method,
                path: path,
                body: payload,
                user_role: role
            })
        })
        .then(res => res.json())
        .then(data => {
            apiResponseConsole.innerText = JSON.stringify(data.response, null, 2);
            renderDatabaseInspector(data.db_state);
        })
        .catch(err => {
            apiResponseConsole.innerText = "Error executing simulation.";
        });
    });

    // Refresh sandbox DB
    refreshDbBtn.addEventListener("click", refreshVirtualDB);

    function refreshVirtualDB() {
        fetch("/api/db-state")
            .then(res => res.json())
            .then(data => {
                renderDatabaseInspector(data);
            })
            .catch(err => console.error("Error refreshing database state: ", err));
    }

    function renderDatabaseInspector(dbState) {
        dbTablesInspector.innerHTML = "";
        
        if (!dbState || Object.keys(dbState).length === 0) {
            dbTablesInspector.innerHTML = '<div class="text-xs text-slate-500">Database is empty. Compile a system.</div>';
            return;
        }

        Object.keys(dbState).forEach(tblName => {
            const items = dbState[tblName];
            
            const card = document.createElement("div");
            card.className = "db-table-card";
            
            card.innerHTML = `
                <div class="db-table-card-header">
                    <span class="table-name-badge">Collection: "${tblName}"</span>
                    <span class="table-count">${items.length} records</span>
                </div>
                <div class="table-columns-header">Rows inside virtual storage:</div>
                <div class="table-rows-wrapper" id="rows-${tblName}"></div>
            `;
            
            const rowsWrapper = card.querySelector(`#rows-${tblName}`);
            if (items.length === 0) {
                rowsWrapper.innerHTML = '<span class="text-xs text-slate-600 pl-2">No rows present.</span>';
            } else {
                items.forEach(row => {
                    const rowDiv = document.createElement("div");
                    rowDiv.className = "table-row-item";
                    rowDiv.innerText = JSON.stringify(row);
                    rowsWrapper.appendChild(rowDiv);
                });
            }
            
            dbTablesInspector.appendChild(card);
        });
    }
});
