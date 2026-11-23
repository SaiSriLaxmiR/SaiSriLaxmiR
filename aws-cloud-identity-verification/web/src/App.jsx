import { useEffect, useMemo, useState } from "react";
import {
  apiReady,
  createLivenessSession,
  enrollUser,
  getHistory,
  getLivenessResult,
  verifyUser,
} from "./api";
import CameraCapture from "./components/CameraCapture";

const navItems = ["Dashboard", "Enroll", "Verify", "History"];

function MetricCard({ label, value, hint }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{hint}</small>
    </article>
  );
}

function VerificationBadge({ verified }) {
  return (
    <span className={`status ${verified ? "success" : "danger"}`}>
      {verified ? "Verified" : "Rejected"}
    </span>
  );
}

function EmptyState({ children }) {
  return <div className="empty-state">{children}</div>;
}

export default function App() {
  const [active, setActive] = useState("Dashboard");
  const [userId, setUserId] = useState("demo-user");
  const [referenceImage, setReferenceImage] = useState(null);
  const [probeImage, setProbeImage] = useState(null);
  const [sessionId, setSessionId] = useState("");
  const [liveness, setLiveness] = useState(null);
  const [verification, setVerification] = useState(null);
  const [history, setHistory] = useState([]);
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const configured = apiReady();

  const stats = useMemo(() => {
    const total = history.length;
    const passed = history.filter((item) => item.verified).length;
    const average =
      total === 0
        ? 0
        : history.reduce(
            (sum, item) => sum + Number(item.similarity || 0),
            0,
          ) / total;
    return {
      total,
      passed,
      passRate: total ? Math.round((passed / total) * 100) : 0,
      average: average ? average.toFixed(1) : "—",
    };
  }, [history]);

  async function run(message, fn) {
    setBusy(true);
    setNotice(message);
    try {
      const value = await fn();
      setNotice("Completed successfully");
      return value;
    } catch (error) {
      setNotice(error.message);
      throw error;
    } finally {
      setBusy(false);
    }
  }

  async function refreshHistory() {
    if (!configured || !userId.trim()) return;
    try {
      const data = await getHistory(userId.trim());
      setHistory(data.items || []);
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    if (active === "Dashboard" || active === "History") {
      refreshHistory();
    }
  }, [active, userId]);

  async function handleEnroll() {
    if (!referenceImage) {
      setNotice("Add a reference image first.");
      return;
    }
    try {
      await run("Creating encrypted enrollment...", () =>
        enrollUser(userId.trim(), referenceImage.base64),
      );
      setActive("Verify");
    } catch {
      // Notice is already set by run().
    }
  }

  async function handleCreateLiveness() {
    try {
      const data = await run("Creating liveness session...", () =>
        createLivenessSession(),
      );
      setSessionId(data.session_id);
      setLiveness(null);
    } catch {
      // Notice is already set by run().
    }
  }

  async function handleCheckLiveness() {
    if (!sessionId) {
      setNotice("Create or enter a liveness session first.");
      return;
    }
    try {
      const data = await run("Checking liveness...", () =>
        getLivenessResult(sessionId),
      );
      setLiveness(data);
    } catch {
      // Notice is already set by run().
    }
  }

  async function handleVerify() {
    if (!probeImage) {
      setNotice("Add a verification image first.");
      return;
    }
    if (!sessionId) {
      setNotice("A completed liveness session is required.");
      return;
    }
    try {
      const data = await run("Comparing identity...", () =>
        verifyUser(userId.trim(), probeImage.base64, sessionId),
      );
      setVerification(data);
      await refreshHistory();
    } catch {
      // Notice is already set by run().
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <strong>Authra</strong>
            <span>Identity Cloud</span>
          </div>
        </div>

        <nav>
          {navItems.map((item) => (
            <button
              key={item}
              className={active === item ? "nav-item active" : "nav-item"}
              onClick={() => setActive(item)}
            >
              <span className="nav-dot" />
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-foot">
          <span className={configured ? "status success" : "status warning"}>
            {configured ? "AWS connected" : "API not configured"}
          </span>
          <small>Consent-based verification only</small>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <span className="micro-label">AUTHRA IDENTITY CLOUD</span>
            <h1>{active}</h1>
          </div>
          <div className="user-control">
            <label htmlFor="user-id">User ID</label>
            <input
              id="user-id"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
            />
          </div>
        </header>

        {!configured && (
          <section className="config-banner">
            <strong>Backend not connected yet.</strong>
            <span>
              Add your deployed API Gateway URL to
              <code> web/.env </code>
              as <code>VITE_API_BASE_URL</code>.
            </span>
          </section>
        )}

        {notice && <div className="toast">{notice}</div>}

        {active === "Dashboard" && (
          <>
            <section className="hero-card">
              <div>
                <span className="micro-label">SERVERLESS IDENTITY VERIFICATION</span>
                <h2>Verify people, not passwords.</h2>
                <p>
                  Authra combines face enrollment, liveness validation,
                  encrypted storage, and AWS-native verification in one
                  lightweight workflow.
                </p>
                <div className="hero-actions">
                  <button onClick={() => setActive("Enroll")}>
                    Enroll identity
                  </button>
                  <button
                    className="button-secondary"
                    onClick={() => setActive("Verify")}
                  >
                    Run verification
                  </button>
                </div>
              </div>
              <div className="security-visual">
                <div className="scan-ring">
                  <div className="scan-face">◎</div>
                </div>
                <span>Rekognition + Liveness</span>
              </div>
            </section>

            <section className="metrics-grid">
              <MetricCard
                label="Verification attempts"
                value={stats.total}
                hint="Recent records"
              />
              <MetricCard
                label="Pass rate"
                value={`${stats.passRate}%`}
                hint="Verified attempts"
              />
              <MetricCard
                label="Avg. face similarity"
                value={stats.average === "—" ? "—" : `${stats.average}%`}
                hint="Rekognition score"
              />
              <MetricCard
                label="Security"
                value="Encrypted"
                hint="S3 + DynamoDB"
              />
            </section>

            <section className="two-column">
              <article className="surface">
                <div className="section-head">
                  <div>
                    <span className="micro-label">RECENT ACTIVITY</span>
                    <h3>Verification history</h3>
                  </div>
                  <button
                    className="text-button"
                    onClick={() => setActive("History")}
                  >
                    View all
                  </button>
                </div>
                {history.length ? (
                  <div className="activity-list">
                    {history.slice(0, 5).map((item) => (
                      <div className="activity-row" key={item.record_id}>
                        <div>
                          <strong>{item.user_id}</strong>
                          <span>
                            {new Date(item.created_at).toLocaleString()}
                          </span>
                        </div>
                        <div className="activity-score">
                          <strong>{Number(item.similarity).toFixed(1)}%</strong>
                          <VerificationBadge verified={item.verified} />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState>
                    Run a verification to populate real activity.
                  </EmptyState>
                )}
              </article>

              <article className="surface">
                <span className="micro-label">SYSTEM DESIGN</span>
                <h3>AWS-native by default</h3>
                <div className="stack-list">
                  <div><b>API Gateway</b><span>REST entrypoint</span></div>
                  <div><b>Lambda</b><span>Serverless compute</span></div>
                  <div><b>Rekognition</b><span>Face + liveness</span></div>
                  <div><b>DynamoDB</b><span>Identity + history</span></div>
                  <div><b>S3</b><span>Encrypted reference images</span></div>
                  <div><b>CloudWatch</b><span>Operational metrics</span></div>
                </div>
              </article>
            </section>
          </>
        )}

        {active === "Enroll" && (
          <section className="flow-layout">
            <div className="flow-copy">
              <span className="micro-label">STEP 1 OF 3</span>
              <h2>Create an identity enrollment</h2>
              <p>
                Add one clear, consented reference image. Authra validates
                that exactly one face is present before storing the image
                in encrypted S3 and the enrollment metadata in DynamoDB.
              </p>
              <ul className="check-list">
                <li>Exactly one face</li>
                <li>Encrypted object storage</li>
                <li>Serverless enrollment API</li>
              </ul>
            </div>
            <div>
              <CameraCapture
                label="REFERENCE IMAGE"
                value={referenceImage}
                onChange={setReferenceImage}
              />
              <button
                className="primary-wide"
                disabled={!configured || busy || !referenceImage}
                onClick={handleEnroll}
              >
                {busy ? "Enrolling..." : "Create enrollment"}
              </button>
            </div>
          </section>
        )}

        {active === "Verify" && (
          <section className="verification-layout">
            <article className="surface">
              <span className="micro-label">STEP 2</span>
              <h3>Liveness session</h3>
              <p>
                Create a Rekognition Face Liveness session before identity
                matching.
              </p>
              <button
                disabled={!configured || busy}
                onClick={handleCreateLiveness}
              >
                Create liveness session
              </button>
              <label className="field">
                Session ID
                <input
                  value={sessionId}
                  onChange={(event) => setSessionId(event.target.value)}
                  placeholder="Session ID"
                />
              </label>
              <button
                className="button-secondary"
                disabled={!configured || busy || !sessionId}
                onClick={handleCheckLiveness}
              >
                Check liveness
              </button>
              {liveness && (
                <div className="result-card compact">
                  <VerificationBadge verified={liveness.passed} />
                  <strong>{liveness.confidence}% confidence</strong>
                  <span>{liveness.status}</span>
                </div>
              )}
            </article>

            <article className="surface">
              <span className="micro-label">STEP 3</span>
              <h3>Verify identity</h3>
              <CameraCapture
                label="LIVE / PROBE IMAGE"
                value={probeImage}
                onChange={setProbeImage}
              />
              <button
                className="primary-wide"
                disabled={!configured || busy || !probeImage || !sessionId}
                onClick={handleVerify}
              >
                {busy ? "Verifying..." : "Verify identity"}
              </button>
            </article>

            <article className="surface result-surface">
              <span className="micro-label">RESULT</span>
              {verification ? (
                <div className="verification-result">
                  <div
                    className={
                      verification.verified
                        ? "result-orb verified"
                        : "result-orb rejected"
                    }
                  >
                    {verification.verified ? "✓" : "×"}
                  </div>
                  <h2>
                    {verification.verified
                      ? "Identity verified"
                      : "Verification rejected"}
                  </h2>
                  <p>
                    Face similarity:{" "}
                    <strong>{verification.similarity}%</strong>
                  </p>
                  <p>
                    Liveness confidence:{" "}
                    <strong>
                      {verification.liveness?.confidence || 0}%
                    </strong>
                  </p>
                </div>
              ) : (
                <EmptyState>
                  Your verification result will appear here.
                </EmptyState>
              )}
            </article>
          </section>
        )}

        {active === "History" && (
          <section className="surface">
            <div className="section-head">
              <div>
                <span className="micro-label">AUDIT TRAIL</span>
                <h3>Verification history</h3>
              </div>
              <button className="button-secondary" onClick={refreshHistory}>
                Refresh
              </button>
            </div>

            {history.length ? (
              <div className="history-table">
                <div className="history-row history-header">
                  <span>Date</span>
                  <span>User</span>
                  <span>Similarity</span>
                  <span>Liveness</span>
                  <span>Status</span>
                </div>
                {history.map((item) => (
                  <div className="history-row" key={item.record_id}>
                    <span>{new Date(item.created_at).toLocaleString()}</span>
                    <span>{item.user_id}</span>
                    <span>{Number(item.similarity).toFixed(1)}%</span>
                    <span>{Number(item.liveness_confidence).toFixed(1)}%</span>
                    <span>
                      <VerificationBadge verified={item.verified} />
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState>
                No verification records yet for this user.
              </EmptyState>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
