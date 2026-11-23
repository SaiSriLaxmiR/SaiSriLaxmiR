import { useEffect, useRef, useState } from "react";

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const value = String(reader.result || "");
      resolve(value.split(",", 2)[1] || "");
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export default function CameraCapture({
  label,
  value,
  onChange,
}) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  async function startCamera() {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch {
      setError("Camera access was not available. Upload an image instead.");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOn(false);
  }

  async function capture() {
    const video = videoRef.current;
    if (!video?.videoWidth) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const blob = await new Promise((resolve) =>
      canvas.toBlob(resolve, "image/jpeg", 0.9),
    );
    if (!blob) return;

    onChange({
      base64: await blobToBase64(blob),
      preview: URL.createObjectURL(blob),
      source: "camera",
    });
    stopCamera();
  }

  async function upload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    onChange({
      base64: await blobToBase64(file),
      preview: URL.createObjectURL(file),
      source: "upload",
    });
  }

  return (
    <div className="capture-card">
      <div className="capture-head">
        <div>
          <span className="micro-label">{label}</span>
          <strong>
            {value ? "Image ready" : "Add a clear face image"}
          </strong>
        </div>
        {value && <span className="status success">Ready</span>}
      </div>

      <div className="capture-frame">
        {cameraOn ? (
          <video ref={videoRef} autoPlay playsInline muted />
        ) : value ? (
          <img src={value.preview} alt="Selected face preview" />
        ) : (
          <div className="capture-empty">
            <div className="face-outline">◉</div>
            <p>Center one face in the frame</p>
          </div>
        )}
      </div>

      <div className="capture-actions">
        {cameraOn ? (
          <>
            <button type="button" onClick={capture}>
              Capture photo
            </button>
            <button
              type="button"
              className="button-secondary"
              onClick={stopCamera}
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            <button type="button" onClick={startCamera}>
              Use camera
            </button>
            <label className="file-button">
              Upload image
              <input
                type="file"
                accept="image/*"
                onChange={upload}
                hidden
              />
            </label>
          </>
        )}
      </div>
      {error && <p className="inline-error">{error}</p>}
    </div>
  );
}
