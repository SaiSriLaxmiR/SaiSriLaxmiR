import { useMemo, useState } from "react";

async function toBase64(file) {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function request(baseUrl, path, options = {}) {
  const response = await fetch(`${baseUrl.replace(/\/$/, "")}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed: ${response.status}`);
  }
  return data;
}

function Result({ data }) {
  if (!data) return null;
  return (
    <pre className="result" aria-live="polite">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

export default function App() {
  const [baseUrl, setBaseUrl] = useState(
    import.meta.env.VITE_API_BASE_URL || "",
  );
  const [userId, setUserId] = useState("demo-user");
  const [referenceImage, setReferenceImage] = useState(null);
  const [probeImage, setProbeImage] = useState(null);
  const [sessionId, setSessionId] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const ready = useMemo(() => Boolean(baseUrl.trim()), [baseUrl]);

  async function run(label, fn) {
    setBusy(true);
    setStatus(label);
    setResult(null);
    try {
      setResult(await fn());
      setStatus("Done");
    } catch (error) {
      setResult({ error: error.message });
      setStatus("Request failed");
    } finally {
      setBusy(false);
    }
  }

  async function enroll() {
    if (!referenceImage) throw new Error("Choose a reference image");
    const imageBase64 = await toBase64(referenceImage);
    return request(baseUrl, "/enroll", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        image_base64: imageBase64,
      }),
    });
  }

  async function createLiveness() {
    const data = await request(baseUrl, "/liveness/session", {
      method: "POST",
      body: JSON.stringify({}),
    });
    setSessionId(data.session_id);
    return data;
  }

  async function checkLiveness() {
    if (!sessionId) throw new Error("Enter a liveness session ID");
    return request(
      baseUrl,
      `/liveness/${encodeURIComponent(sessionId)}`,
    );
  }

  async function verify() {
    if (!probeImage) throw new Error("Choose a probe image");
    if (!sessionId) throw new Error("Enter a completed liveness session ID");

    const imageBase64 = await toBase64(probeImage);
    return request(baseUrl, "/verify", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        image_base64: imageBase64,
        liveness_session_id: sessionId,
      }),
    });
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="brand-mark">K</div>
        <div>
          <p className="eyebrow">AWS SERVERLESS IDENTITY VERIFICATION</p>
          <h1>Kavira</h1>
          <p className="subtitle">
            Consent-based face enrollment, liveness validation, and
            identity verification through a serverless AWS backend.
          </p>
        </div>
      </section>

      <section className="panel config-panel">
        <label>
          API base URL
          <input
            value={baseUrl}
            onChange={(event) => setBaseUrl(event.target.value)}
            placeholder="https://...execute-api...amazonaws.com/prod"
          />
        </label>
        <label>
          User ID
          <input
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
          />
        </label>
      </section>

      <section className="grid">
        <article className="panel">
          <span className="step">01</span>
          <h2>Enroll</h2>
          <p>Register one consented reference face for the user.</p>
          <input
            type="file"
            accept="image/*"
            onChange={(event) =>
              setReferenceImage(event.target.files?.[0] || null)
            }
          />
          <button
            disabled={!ready || busy}
            onClick={() => run("Enrolling...", enroll)}
          >
            Enroll reference
          </button>
        </article>

        <article className="panel">
          <span className="step">02</span>
          <h2>Liveness</h2>
          <p>
            Create a Face Liveness session, then use its ID after the
            supported AWS client flow completes.
          </p>
          <button
            disabled={!ready || busy}
            onClick={() => run("Creating session...", createLiveness)}
          >
            Create session
          </button>
          <input
            value={sessionId}
            onChange={(event) => setSessionId(event.target.value)}
            placeholder="Liveness session ID"
          />
          <button
            className="secondary"
            disabled={!ready || busy || !sessionId}
            onClick={() => run("Checking liveness...", checkLiveness)}
          >
            Check result
          </button>
        </article>

        <article className="panel">
          <span className="step">03</span>
          <h2>Verify</h2>
          <p>
            Compare a live probe image with the enrolled reference after
            liveness succeeds.
          </p>
          <input
            type="file"
            accept="image/*"
            onChange={(event) =>
              setProbeImage(event.target.files?.[0] || null)
            }
          />
          <button
            disabled={!ready || busy}
            onClick={() => run("Verifying...", verify)}
          >
            Verify identity
          </button>
        </article>
      </section>

      <section className="panel output-panel">
        <div>
          <p className="eyebrow">API RESPONSE</p>
          <h2>{status || "Ready"}</h2>
        </div>
        <Result data={result} />
      </section>

      <footer>
        Kavira is a portfolio project for consent-based identity verification.
        It is not intended for covert identification or surveillance.
      </footer>
    </main>
  );
}
