import { useMemo, useRef, useState } from "react";
import { runBenchmark } from "./api";

const defaultPipelines = [
  {
    id: "stack-a",
    name: "Swift",
    vad: "WebRTC VAD",
    asr: "Deepgram",
    llm: "GPT",
    selected: true,
  },
  {
    id: "stack-b",
    name: "Clear",
    vad: "Silero VAD",
    asr: "Whisper",
    llm: "Bedrock",
    selected: true,
  },
  {
    id: "stack-c",
    name: "Nova",
    vad: "AWS VAD",
    asr: "Transcribe",
    llm: "Claude",
    selected: true,
  },
];

function Metric({ label, value, helper }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{helper}</small>
    </article>
  );
}

function ResultCard({ result, rank }) {
  const m = result.metrics;
  return (
    <article className="result-card">
      <div className="result-head">
        <div>
          <span className="rank">#{rank}</span>
          <h3>{result.pipeline.name}</h3>
          <p>
            {result.pipeline.vad} · {result.pipeline.asr} · {result.pipeline.llm}
          </p>
        </div>
        <span className={m.task_success ? "pill success" : "pill danger"}>
          {m.task_success ? "Task passed" : "Task failed"}
        </span>
      </div>

      <div className="mini-grid">
        <Metric
          label="Transcript"
          value={`${m.transcript_accuracy}%`}
          helper="accuracy"
        />
        <Metric
          label="Response"
          value={`${m.response_latency_ms} ms`}
          helper="latency"
        />
        <Metric
          label="Turn end"
          value={`${m.end_of_turn_ms} ms`}
          helper="detection"
        />
        <Metric
          label="Cost"
          value={`$${m.estimated_cost_usd}`}
          helper="per run"
        />
      </div>

      <div className="diagnostic">
        <div>
          <span className="section-label">AURI DIAGNOSTIC</span>
          <strong>{result.diagnostic.stage.toUpperCase()}</strong>
        </div>
        <p>{result.diagnostic.summary}</p>
        <small>{result.diagnostic.recommendation}</small>
      </div>
    </article>
  );
}

export default function App() {
  const [pipelines, setPipelines] = useState(defaultPipelines);
  const [reference, setReference] = useState(
    "I need to change the delivery address on my order.",
  );
  const [audioName, setAudioName] = useState("");
  const [results, setResults] = useState([]);
  const [running, setRunning] = useState(false);
  const [notice, setNotice] = useState("");
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef(null);

  const selected = useMemo(
    () => pipelines.filter((pipeline) => pipeline.selected),
    [pipelines],
  );

  const best = results[0];

  function togglePipeline(id) {
    setPipelines((current) =>
      current.map((pipeline) =>
        pipeline.id === id
          ? { ...pipeline, selected: !pipeline.selected }
          : pipeline,
      ),
    );
  }

  async function run() {
    if (!selected.length) {
      setNotice("Select at least one voice stack.");
      return;
    }

    setRunning(true);
    setNotice("Running benchmark...");
    try {
      const data = await runBenchmark({
        conversation_id: `auri-${Date.now()}`,
        transcript_reference: reference,
        pipelines: selected.map(({ selected: _, ...pipeline }) => pipeline),
      });
      setResults(data.results);
      setNotice("Benchmark complete");
    } catch (error) {
      setNotice(error.message);
    } finally {
      setRunning(false);
    }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (event) => chunks.push(event.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        setAudioName(`recording-${Math.round(blob.size / 1024)}kb.webm`);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      mediaRecorder.current = recorder;
      setRecording(true);
      setNotice("Recording sample...");
    } catch {
      setNotice("Microphone access was not available.");
    }
  }

  function stopRecording() {
    mediaRecorder.current?.stop();
    setRecording(false);
    setNotice("Audio sample captured");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">a</div>
          <div>
            <strong>Auri</strong>
            <span>Voice reliability</span>
          </div>
        </div>

        <nav>
          <button className="nav active">Overview</button>
          <button className="nav">Benchmarks</button>
          <button className="nav">Traces</button>
          <button className="nav">Stacks</button>
        </nav>

        <div className="sidebar-note">
          <span className="online-dot" />
          Demo workspace
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <span className="eyebrow">VOICE AI RELIABILITY</span>
            <h1>Hear what breaks before users do.</h1>
            <p>
              Compare voice stacks, trace conversation failures, and understand
              whether the problem came from speech recognition, turn detection,
              model reasoning, or tool execution.
            </p>
          </div>
          <button className="primary" onClick={run} disabled={running}>
            {running ? "Running..." : "Run benchmark"}
          </button>
        </header>

        {notice && <div className="notice">{notice}</div>}

        <section className="workspace-grid">
          <article className="panel input-panel">
            <span className="section-label">01 · TEST CONVERSATION</span>
            <h2>Add a voice sample</h2>
            <p>
              Upload a call or record a short sample. Auri runs the same input
              through each selected stack for an apples-to-apples comparison.
            </p>

            <div className="audio-box">
              <div className={recording ? "wave recording" : "wave"}>
                {Array.from({ length: 26 }).map((_, index) => (
                  <span key={index} style={{ height: `${16 + ((index * 13) % 42)}px` }} />
                ))}
              </div>
              <strong>{audioName || "No audio added yet"}</strong>
              <div className="audio-actions">
                <button
                  className="secondary"
                  onClick={recording ? stopRecording : startRecording}
                >
                  {recording ? "Stop recording" : "Use microphone"}
                </button>
                <label className="secondary file-label">
                  Upload audio
                  <input
                    hidden
                    type="file"
                    accept="audio/*"
                    onChange={(event) =>
                      setAudioName(event.target.files?.[0]?.name || "")
                    }
                  />
                </label>
              </div>
            </div>

            <label className="field">
              Expected user intent / reference transcript
              <textarea
                value={reference}
                onChange={(event) => setReference(event.target.value)}
              />
            </label>
          </article>

          <article className="panel">
            <span className="section-label">02 · VOICE STACKS</span>
            <h2>Choose what to compare</h2>
            <div className="pipeline-list">
              {pipelines.map((pipeline) => (
                <button
                  className={pipeline.selected ? "pipeline selected" : "pipeline"}
                  key={pipeline.id}
                  onClick={() => togglePipeline(pipeline.id)}
                >
                  <div>
                    <strong>{pipeline.name}</strong>
                    <span>
                      {pipeline.vad} · {pipeline.asr} · {pipeline.llm}
                    </span>
                  </div>
                  <span className="check">{pipeline.selected ? "✓" : "+"}</span>
                </button>
              ))}
            </div>
          </article>
        </section>

        <section className="overview-strip">
          <Metric
            label="Evaluation suite"
            value="240"
            helper="conversation scenarios"
          />
          <Metric
            label="Noise profiles"
            value="3"
            helper="clean · cafe · street"
          />
          <Metric
            label="Full benchmark"
            value="2,160"
            helper="stack-condition runs"
          />
          <Metric
            label="Reliability metrics"
            value="8+"
            helper="WER · p50/p95 · success · cost"
          />
        </section>

        <section className="results-section">
          <div className="section-heading">
            <div>
              <span className="section-label">BENCHMARK RESULTS</span>
              <h2>Which stack feels best?</h2>
            </div>
            {best && (
              <div className="winner">
                Best current stack <strong>{best.pipeline.name}</strong>
              </div>
            )}
          </div>

          {results.length ? (
            <div className="results-grid">
              {results.map((result, index) => (
                <ResultCard
                  key={result.pipeline.id}
                  result={result}
                  rank={index + 1}
                />
              ))}
            </div>
          ) : (
            <div className="empty">
              <div className="empty-icon">◌</div>
              <h3>No benchmark yet</h3>
              <p>
                Add a sample, choose your stacks, and run the first comparison.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
