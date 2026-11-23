const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || ""
).replace(/\/$/, "");

async function request(path, options = {}) {
  if (!API_BASE_URL) {
    throw new Error(
      "VITE_API_BASE_URL is not configured. Deploy the AWS backend and add the API URL to web/.env."
    );
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      data.error || `Request failed with status ${response.status}`,
    );
  }
  return data;
}

export function apiReady() {
  return Boolean(API_BASE_URL);
}

export function enrollUser(userId, imageBase64) {
  return request("/enroll", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      image_base64: imageBase64,
    }),
  });
}

export function createLivenessSession() {
  return request("/liveness/session", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function getLivenessResult(sessionId) {
  return request(
    `/liveness/${encodeURIComponent(sessionId)}`,
  );
}

export function verifyUser(
  userId,
  imageBase64,
  livenessSessionId,
) {
  return request("/verify", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      image_base64: imageBase64,
      liveness_session_id: livenessSessionId,
    }),
  });
}

export function getHistory(userId) {
  return request(
    `/history/${encodeURIComponent(userId)}?limit=20`,
  );
}
