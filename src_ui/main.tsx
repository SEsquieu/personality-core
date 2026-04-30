import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, BrainCircuit, FlaskConical, Gauge, Play, Save, Settings2, Sparkles } from "lucide-react";
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

type Personality = {
  id: string;
  name: string;
  description: string;
  cores: Array<{ id: string; strength: number }>;
};

type CompareResult = {
  personality: string;
  content?: string;
  warnings?: string[];
  error?: string;
  debug?: {
    mode: string;
    resolved: {
      resolved_traits: Record<string, number>;
      active_cores: Array<{ id: string; name: string; strength: number }>;
      core_trace: Array<{ id: string; name: string; strength: number; trait_effects: Record<string, number> }>;
    };
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

const DEMOS = {
  retry_loop: "Explain why retries hide real errors.",
  angry_customer: "A customer is angry because their export failed twice. Draft the response.",
  code_review: "Review this pattern: a retry loop mutates shared state and swallows the original exception.",
  startup_pitch: "Pressure-test my idea for an AI-powered meeting notes app.",
  debugging: "Explain why mutating shared state inside a retry loop is dangerous."
};

const DEFAULT_PERSONALITIES = ["professional_support", "deadpan_debugger", "patient_tutor", "startup_cofounder", "chaos_goblin"];

function App() {
  const [cores, setCores] = useState<CoreDefinition[]>([]);
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [selected, setSelected] = useState<string[]>(DEFAULT_PERSONALITIES);
  const [prompt, setPrompt] = useState(DEMOS.retry_loop);
  const [model, setModel] = useState("ollama/gemma4:e4b");
  const [maxTokens, setMaxTokens] = useState(320);
  const [results, setResults] = useState<CompareResult[]>([]);
  const [activePersonality, setActivePersonality] = useState("professional_support");
  const [loading, setLoading] = useState(false);
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

  async function runCompare() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/v1/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          prompt,
          personalities: selected,
          max_tokens: maxTokens,
          think: false
        })
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || response.statusText);
      }
      const data = await response.json();
      setResults(data.results ?? []);
      setActivePersonality((data.results?.[0]?.personality as string) ?? selected[0]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Compare run failed.");
    } finally {
      setLoading(false);
    }
  }

  const activeResult = results.find((result) => result.personality === activePersonality) ?? results[0];
  const activePreset = personalities.find((item) => item.id === activePersonality) ?? personalities[0];
  const coreMap = useMemo(() => new Map(cores.map((core) => [core.id, core])), [cores]);

  return (
    <div className="app-shell">
      <aside className="core-panel">
        <div className="brand-row">
          <BrainCircuit size={26} />
          <div>
            <h1>Personality Core</h1>
            <p>Runtime workbench</p>
          </div>
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
          <label>Compare Presets</label>
          <div className="preset-list">
            {personalities.map((persona) => (
              <label key={persona.id} className="check-row">
                <input
                  type="checkbox"
                  checked={selected.includes(persona.id)}
                  onChange={(event) => {
                    setSelected((current) =>
                      event.target.checked ? [...current, persona.id] : current.filter((id) => id !== persona.id)
                    );
                  }}
                />
                <span>{persona.name}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="control-section">
          <label>Token Cap: {maxTokens}</label>
          <input type="range" min="120" max="900" step="20" value={maxTokens} onChange={(event) => setMaxTokens(Number(event.target.value))} />
        </section>
      </aside>

      <main className="workbench">
        <div className="topbar">
          <div>
            <h2>Compare Personality Stacks</h2>
            <p>Same prompt, same model, different installed cores.</p>
          </div>
          <button className="run-button" onClick={runCompare} disabled={loading || selected.length === 0}>
            <Play size={18} />
            {loading ? "Running" : "Run Compare"}
          </button>
        </div>

        <textarea className="prompt-box" value={prompt} onChange={(event) => setPrompt(event.target.value)} />

        {error && (
          <div className="error-strip">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        <div className="result-tabs">
          {results.map((result) => (
            <button
              key={result.personality}
              className={activePersonality === result.personality ? "active" : ""}
              onClick={() => setActivePersonality(result.personality)}
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
      </main>

      <aside className="diagnostics">
        <div className="diag-header">
          <FlaskConical size={21} />
          <h2>Diagnostics</h2>
        </div>
        {!activeResult?.debug && <p className="muted">Run compare to see resolved traits, core trace, and scoring.</p>}
        {activeResult?.debug && (
          <>
            <section className="diag-section">
              <h3>Resolved Traits</h3>
              {topTraits(activeResult.debug.resolved.resolved_traits).map(([trait, value]) => (
                <TraitBar key={trait} trait={trait} value={value} />
              ))}
            </section>

            <section className="diag-section">
              <h3>Core Scores</h3>
              {Object.entries(activeResult.debug.evaluation.core_scores).map(([core, value]) => (
                <TraitBar key={core} trait={core.replace("_core", "")} value={value} />
              ))}
            </section>

            <section className="diag-section">
              <h3>Core Trace</h3>
              {activeResult.debug.resolved.core_trace.map((trace) => (
                <details key={trace.id} open={trace.id === activeResult.debug?.resolved.active_cores[0]?.id}>
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

            <section className="diag-section">
              <h3>Installed Rules</h3>
              {(activePreset?.cores ?? []).map((ref) => {
                const core = coreMap.get(ref.id);
                return (
                  <details key={ref.id}>
                    <summary>{core?.name ?? ref.id}</summary>
                    <ul>
                      {(core?.rules ?? []).map((rule) => (
                        <li key={rule}>{rule}</li>
                      ))}
                    </ul>
                  </details>
                );
              })}
            </section>
          </>
        )}
      </aside>
    </div>
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

createRoot(document.getElementById("root")!).render(<App />);
