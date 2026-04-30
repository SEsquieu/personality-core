import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, BrainCircuit, FlaskConical, Gauge, Play, Plus, Settings2, SlidersHorizontal, Trash2 } from "lucide-react";
import "./styles.css";

type CoreDefinition = {
  id: string;
  name: string;
  description: string;
  trait_deltas: Record<string, number>;
  default_strength: number;
  rules: string[];
  boundaries: Record<string, boolean>;
};

type CoreRef = { id: string; strength: number };

type Personality = {
  id: string;
  name: string;
  description: string;
  cores: CoreRef[];
};

type ResolvedStack = {
  resolved_traits: Record<string, number>;
  active_cores: Array<{ id: string; name: string; strength: number }>;
  core_trace: Array<{ id: string; name: string; strength: number; trait_effects: Record<string, number> }>;
  conflicts: Array<{ cores: string[]; reason: string; resolution: string }>;
};

type RunResult = {
  content?: string;
  warnings?: string[];
  debug?: {
    mode: string;
    resolved: ResolvedStack;
    evaluation: {
      core_match: number;
      core_scores: Record<string, number>;
      issues: string[];
    };
    model_response: {
      done_reason: string | null;
    };
    compiled_prompt: string;
  };
};

type CompareResult = RunResult & { personality: string; error?: string };

const DEMOS = {
  retry_loop: "Explain why retries hide real errors.",
  angry_customer: "A customer is angry because their export failed twice. Draft the response.",
  code_review: "Review this pattern: a retry loop mutates shared state and swallows the original exception.",
  startup_pitch: "Pressure-test my idea for an AI-powered meeting notes app.",
  debugging: "Explain why mutating shared state inside a retry loop is dangerous."
};

const DEFAULT_PERSONALITIES = ["professional_support", "deadpan_debugger", "patient_tutor", "startup_cofounder", "chaos_goblin"];
const DEFAULT_STACK: CoreRef[] = [
  { id: "technical_core", strength: 0.95 },
  { id: "sarcasm_core", strength: 0.65 },
  { id: "low_verbosity_core", strength: 0.75 },
  { id: "stability_core", strength: 0.85 }
];

function App() {
  const [mode, setMode] = useState<"stack" | "compare">("stack");
  const [cores, setCores] = useState<CoreDefinition[]>([]);
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [selectedPersonalities, setSelectedPersonalities] = useState<string[]>(DEFAULT_PERSONALITIES);
  const [stack, setStack] = useState<CoreRef[]>(DEFAULT_STACK);
  const [prompt, setPrompt] = useState(DEMOS.retry_loop);
  const [model, setModel] = useState("ollama/gemma4:e4b");
  const [maxTokens, setMaxTokens] = useState(360);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [compareResults, setCompareResults] = useState<CompareResult[]>([]);
  const [activeCompare, setActiveCompare] = useState("professional_support");
  const [resolved, setResolved] = useState<ResolvedStack | null>(null);
  const [compiledPrompt, setCompiledPrompt] = useState("");
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    void loadCatalog();
  }, []);

  async function loadCatalog() {
    try {
      const [coreRes, personaRes] = await Promise.all([fetch("/v1/cores"), fetch("/v1/personalities")]);
      const coreJson = await coreRes.json();
      const personaJson = await personaRes.json();
      setCores(coreJson.data ?? []);
      setPersonalities(personaJson.data ?? []);
    } catch {
      setError("Backend is not reachable. Start `personality-core serve --host 127.0.0.1 --port 8787`.");
    }
  }

  const coreMap = useMemo(() => new Map(cores.map((core) => [core.id, core])), [cores]);
  const activeCompareResult = compareResults.find((result) => result.personality === activeCompare) ?? compareResults[0];
  const activeDebug = mode === "stack" ? runResult?.debug : activeCompareResult?.debug;
  const activeResolved = activeDebug?.resolved ?? resolved;

  async function postJson<T>(url: string, body: unknown): Promise<T> {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || response.statusText);
    }
    return response.json();
  }

  function stackPayload() {
    return {
      model,
      prompt,
      cores: stack,
      max_tokens: maxTokens,
      think: false
    };
  }

  async function resolveStack() {
    setLoading("resolve");
    setError("");
    try {
      const data = await postJson<{ resolved: ResolvedStack }>("/v1/stack/resolve", stackPayload());
      setResolved(data.resolved);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading("");
    }
  }

  async function compileStack() {
    setLoading("compile");
    setError("");
    try {
      const data = await postJson<{ resolved: ResolvedStack; compiled_prompt: string }>("/v1/stack/compile", stackPayload());
      setResolved(data.resolved);
      setCompiledPrompt(data.compiled_prompt);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading("");
    }
  }

  async function runStack() {
    setLoading("run");
    setError("");
    try {
      const data = await postJson<RunResult>("/v1/stack/run", stackPayload());
      setRunResult(data);
      setResolved(data.debug?.resolved ?? null);
      setCompiledPrompt(data.debug?.compiled_prompt ?? "");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading("");
    }
  }

  async function runCompare() {
    setLoading("compare");
    setError("");
    try {
      const data = await postJson<{ results: CompareResult[] }>("/v1/compare", {
        model,
        prompt,
        personalities: selectedPersonalities,
        max_tokens: maxTokens,
        think: false
      });
      setCompareResults(data.results ?? []);
      setActiveCompare((data.results?.[0]?.personality as string) ?? selectedPersonalities[0]);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading("");
    }
  }

  function loadPreset(persona: Personality) {
    setStack(persona.cores.map((core) => ({ id: core.id, strength: core.strength })));
    setResolved(null);
    setRunResult(null);
    setCompiledPrompt("");
  }

  function addCore(coreId: string) {
    if (!coreId || stack.some((item) => item.id === coreId)) return;
    const core = coreMap.get(coreId);
    setStack((current) => [...current, { id: coreId, strength: core?.default_strength ?? 0.5 }]);
  }

  return (
    <div className="app-shell">
      <aside className="core-panel">
        <div className="brand-row">
          <BrainCircuit size={26} />
          <div>
            <h1>Personality Core</h1>
            <p>Core stack workbench</p>
          </div>
        </div>

        <div className="mode-switch">
          <button className={mode === "stack" ? "active" : ""} onClick={() => setMode("stack")}>
            Stack Editor
          </button>
          <button className={mode === "compare" ? "active" : ""} onClick={() => setMode("compare")}>
            Compare
          </button>
        </div>

        <section className="control-section">
          <label>Model</label>
          <input value={model} onChange={(event) => setModel(event.target.value)} />
        </section>

        <section className="control-section">
          <label>Demo Prompt</label>
          <div className="demo-grid">
            {Object.entries(DEMOS).map(([key, value]) => (
              <button key={key} className={prompt === value ? "active" : ""} onClick={() => setPrompt(value)}>
                {key.replace("_", " ")}
              </button>
            ))}
          </div>
        </section>

        <section className="control-section">
          <label>Token Cap: {maxTokens}</label>
          <input type="range" min="120" max="1200" step="20" value={maxTokens} onChange={(event) => setMaxTokens(Number(event.target.value))} />
        </section>

        {mode === "stack" ? (
          <StackControls
            stack={stack}
            cores={cores}
            personalities={personalities}
            coreMap={coreMap}
            onLoadPreset={loadPreset}
            onAddCore={addCore}
            onRemoveCore={(coreId) => setStack((current) => current.filter((item) => item.id !== coreId))}
            onStrengthChange={(coreId, strength) =>
              setStack((current) => current.map((item) => (item.id === coreId ? { ...item, strength } : item)))
            }
          />
        ) : (
          <CompareControls personalities={personalities} selected={selectedPersonalities} onSelectedChange={setSelectedPersonalities} />
        )}
      </aside>

      <main className="workbench">
        <div className="topbar">
          <div>
            <h2>{mode === "stack" ? "Core Stack Editor" : "Compare Personality Stacks"}</h2>
            <p>
              {mode === "stack"
                ? "Tune installed cores, resolve the stack, compile the prompt, then run it in-chain."
                : "Same prompt, same model, different saved core stacks."}
            </p>
          </div>
          {mode === "stack" ? (
            <div className="button-row">
              <button className="secondary-button" onClick={resolveStack} disabled={loading !== "" || stack.length === 0}>
                <SlidersHorizontal size={17} />
                Resolve
              </button>
              <button className="secondary-button" onClick={compileStack} disabled={loading !== "" || stack.length === 0}>
                <Settings2 size={17} />
                Compile
              </button>
              <button className="run-button" onClick={runStack} disabled={loading !== "" || stack.length === 0}>
                <Play size={18} />
                {loading === "run" ? "Running" : "Run Stack"}
              </button>
            </div>
          ) : (
            <button className="run-button" onClick={runCompare} disabled={loading !== "" || selectedPersonalities.length === 0}>
              <Play size={18} />
              {loading === "compare" ? "Running" : "Run Compare"}
            </button>
          )}
        </div>

        <textarea className="prompt-box" value={prompt} onChange={(event) => setPrompt(event.target.value)} />

        {error && (
          <div className="error-strip">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {mode === "stack" ? (
          <StackOutput result={runResult} compiledPrompt={compiledPrompt} />
        ) : (
          <CompareOutput
            results={compareResults}
            active={activeCompare}
            personalities={personalities}
            onActiveChange={setActiveCompare}
          />
        )}
      </main>

      <aside className="diagnostics">
        <div className="diag-header">
          <FlaskConical size={21} />
          <h2>Diagnostics</h2>
        </div>
        {!activeResolved && <p className="muted">Resolve or run a stack to inspect traits, scores, conflicts, and trace.</p>}
        {activeResolved && (
          <>
            <section className="diag-section">
              <h3>Resolved Traits</h3>
              {topTraits(activeResolved.resolved_traits).map(([trait, value]) => (
                <TraitBar key={trait} trait={trait} value={value} />
              ))}
            </section>

            {activeDebug?.evaluation && (
              <section className="diag-section">
                <h3>Core Scores</h3>
                {Object.entries(activeDebug.evaluation.core_scores).map(([core, value]) => (
                  <TraitBar key={core} trait={core.replace("_core", "")} value={value} />
                ))}
              </section>
            )}

            {activeResolved.conflicts.length > 0 && (
              <section className="diag-section">
                <h3>Conflicts</h3>
                {activeResolved.conflicts.map((conflict) => (
                  <div className="conflict-row" key={`${conflict.cores.join("-")}-${conflict.reason}`}>
                    <strong>{conflict.cores.join(" / ")}</strong>
                    <span>{conflict.reason}</span>
                  </div>
                ))}
              </section>
            )}

            <section className="diag-section">
              <h3>Core Trace</h3>
              {activeResolved.core_trace.map((trace) => (
                <details key={trace.id} open={trace.id === activeResolved.active_cores[0]?.id}>
                  <summary>{trace.name}</summary>
                  {Object.entries(trace.trait_effects).map(([trait, value]) => (
                    <div className="trace-row" key={trait}>
                      <span>{trait}</span>
                      <strong>{formatSigned(value)}</strong>
                    </div>
                  ))}
                </details>
              ))}
            </section>
          </>
        )}
      </aside>
    </div>
  );
}

function StackControls({
  stack,
  cores,
  personalities,
  coreMap,
  onLoadPreset,
  onAddCore,
  onRemoveCore,
  onStrengthChange
}: {
  stack: CoreRef[];
  cores: CoreDefinition[];
  personalities: Personality[];
  coreMap: Map<string, CoreDefinition>;
  onLoadPreset: (persona: Personality) => void;
  onAddCore: (coreId: string) => void;
  onRemoveCore: (coreId: string) => void;
  onStrengthChange: (coreId: string, strength: number) => void;
}) {
  const available = cores.filter((core) => !stack.some((item) => item.id === core.id));

  return (
    <>
      <section className="control-section">
        <label>Load Preset</label>
        <div className="preset-list">
          {personalities.map((persona) => (
            <button className="preset-button" key={persona.id} onClick={() => onLoadPreset(persona)}>
              {persona.name}
            </button>
          ))}
        </div>
      </section>

      <section className="control-section">
        <label>Installed Core Stack</label>
        <div className="module-list">
          {stack.map((ref) => {
            const core = coreMap.get(ref.id);
            return (
              <div className="core-module" key={ref.id}>
                <div className="module-head">
                  <strong>{core?.name ?? ref.id}</strong>
                  <button title="Remove core" onClick={() => onRemoveCore(ref.id)}>
                    <Trash2 size={15} />
                  </button>
                </div>
                <p>{core?.description}</p>
                <div className="slider-row">
                  <span>{ref.strength.toFixed(2)}</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={ref.strength}
                    onChange={(event) => onStrengthChange(ref.id, Number(event.target.value))}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="control-section">
        <label>Add Core</label>
        <select defaultValue="" onChange={(event) => {
          onAddCore(event.target.value);
          event.target.value = "";
        }}>
          <option value="">Choose a core</option>
          {available.map((core) => (
            <option value={core.id} key={core.id}>{core.name}</option>
          ))}
        </select>
      </section>
    </>
  );
}

function CompareControls({
  personalities,
  selected,
  onSelectedChange
}: {
  personalities: Personality[];
  selected: string[];
  onSelectedChange: (selected: string[]) => void;
}) {
  return (
    <section className="control-section">
      <label>Compare Presets</label>
      <div className="preset-list">
        {personalities.map((persona) => (
          <label key={persona.id} className="check-row">
            <input
              type="checkbox"
              checked={selected.includes(persona.id)}
              onChange={(event) => {
                onSelectedChange(
                  event.target.checked ? [...selected, persona.id] : selected.filter((id) => id !== persona.id)
                );
              }}
            />
            <span>{persona.name}</span>
          </label>
        ))}
      </div>
    </section>
  );
}

function StackOutput({ result, compiledPrompt }: { result: RunResult | null; compiledPrompt: string }) {
  return (
    <section className="output-surface stack-output">
      {!result?.content && !compiledPrompt && <div className="empty-state">Resolve, compile, or run the active core stack.</div>}
      {result?.warnings?.map((warning) => (
        <div className="warning-strip" key={warning}>
          <AlertTriangle size={17} />
          {warning}
        </div>
      ))}
      {result?.content && (
        <>
          <div className="output-header">
            <div>
              <h3>Stack Output</h3>
              <p>Generated by the active installed core stack.</p>
            </div>
            <div className="badge-row">
              <MetricBadge icon={<Gauge size={15} />} label="match" value={result.debug?.evaluation.core_match.toFixed(2) ?? "--"} />
              <MetricBadge icon={<Settings2 size={15} />} label="done" value={result.debug?.model_response.done_reason ?? "stop"} />
            </div>
          </div>
          <div className="response-text">{result.content}</div>
        </>
      )}
      {compiledPrompt && (
        <details className="compiled-prompt">
          <summary>Compiled Prompt</summary>
          <pre>{compiledPrompt}</pre>
        </details>
      )}
    </section>
  );
}

function CompareOutput({
  results,
  active,
  personalities,
  onActiveChange
}: {
  results: CompareResult[];
  active: string;
  personalities: Personality[];
  onActiveChange: (id: string) => void;
}) {
  const activeResult = results.find((result) => result.personality === active) ?? results[0];
  const activePreset = personalities.find((item) => item.id === activeResult?.personality);

  return (
    <>
      <div className="result-tabs">
        {results.map((result) => (
          <button
            key={result.personality}
            className={active === result.personality ? "active" : ""}
            onClick={() => onActiveChange(result.personality)}
          >
            {displayName(result.personality, personalities)}
            {result.debug && <span>{result.debug.evaluation.core_match.toFixed(2)}</span>}
          </button>
        ))}
      </div>

      <section className="output-surface">
        {!activeResult && <div className="empty-state">Run a comparison to inspect personality output.</div>}
        {activeResult?.error && <div className="empty-state">{activeResult.error}</div>}
        {activeResult?.content && (
          <>
            <div className="output-header">
              <div>
                <h3>{displayName(activeResult.personality, personalities)}</h3>
                <p>{activePreset?.description}</p>
              </div>
              <div className="badge-row">
                <MetricBadge icon={<Gauge size={15} />} label="match" value={activeResult.debug?.evaluation.core_match.toFixed(2) ?? "--"} />
                <MetricBadge icon={<Settings2 size={15} />} label="done" value={activeResult.debug?.model_response.done_reason ?? "stop"} />
              </div>
            </div>
            {(activeResult.warnings ?? []).map((warning) => (
              <div className="warning-strip" key={warning}>
                <AlertTriangle size={17} />
                {warning}
              </div>
            ))}
            <div className="response-text">{activeResult.content}</div>
          </>
        )}
      </section>
    </>
  );
}

function MetricBadge({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="metric-badge">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function TraitBar({ trait, value }: { trait: string; value: number }) {
  return (
    <div className="trait-row">
      <div className="trait-label">
        <span>{trait}</span>
        <strong>{value.toFixed(2)}</strong>
      </div>
      <div className="trait-track">
        <div style={{ width: `${Math.max(0, Math.min(1, value)) * 100}%` }} />
      </div>
    </div>
  );
}

function topTraits(traits: Record<string, number>) {
  return Object.entries(traits)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 9);
}

function displayName(id: string, personalities: Personality[]) {
  return personalities.find((item) => item.id === id)?.name ?? id.replace(/_/g, " ");
}

function formatSigned(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
}

function errorMessage(err: unknown) {
  return err instanceof Error ? err.message : "Request failed.";
}

createRoot(document.getElementById("root")!).render(<App />);
