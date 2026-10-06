import { useState } from "react";
import { QrCode } from "lucide-react";
import {
  createQr,
  getQrDetails,
  updateQr,
} from "./api/api";

function getErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (detail?.message) {
    const reasons = detail.ai_report?.reasons;
    return reasons?.length
      ? `${detail.message} ${reasons.join(". ")}.`
      : detail.message;
  }

  if (!error.response) {
    return "Backend unavailable. Make sure the FastAPI server is running on port 8000.";
  }

  if (error.response.status === 422) {
    return "Enter a valid HTTP or HTTPS URL.";
  }

  return fallback;
}

function App() {
  const [url, setUrl] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [qr, setQr] = useState(null);
  const [details, setDetails] = useState(null);
  const [updateResult, setUpdateResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");

  const createQR = async () => {
    setError("");
    setUpdateResult(null);
    setLoading("create");

    try {
      const response = await createQr(url);
      setQr(response.data);
      setDetails({
        qr_id: response.data.qr_id,
        content: url,
        scans: 0,
        active: true,
        risk_score: response.data.AI?.risk_score,
        ai_status: response.data.AI?.status,
        qr_image: response.data.qr_image,
      });
      setNewUrl("");
    } catch (requestError) {
      setError(getErrorMessage(requestError, "QR creation failed."));
    } finally {
      setLoading("");
    }
  };

  const updateQR = async () => {
    if (!qr) {
      return;
    }

    setError("");
    setUpdateResult(null);
    setLoading("update");

    try {
      const response = await updateQr(qr.qr_id, newUrl);
      setUpdateResult(response.data);
      setDetails((current) => ({
        ...current,
        content: response.data.destination_url,
        risk_score: response.data.risk_score,
        ai_status: response.data.ai_status,
      }));
    } catch (requestError) {
      setError(getErrorMessage(requestError, "QR update failed."));
    } finally {
      setLoading("");
    }
  };

  const getAnalytics = async () => {
    if (!qr) {
      return;
    }

    setError("");
    setLoading("details");

    try {
      const response = await getQrDetails(qr.qr_id);
      setDetails(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load QR details."));
    } finally {
      setLoading("");
    }
  };

  const qrId = qr?.qr_id || details?.qr_id;

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white shadow-xl rounded-xl p-8 w-full max-w-[550px]">
        <div className="flex gap-3 items-center mb-5">
          <QrCode size={35} />
          <h1 className="text-3xl font-bold">Dynamic QR AI</h1>
        </div>

        <section>
          <h2 className="font-bold text-xl">Create QR</h2>
          <input
            className="border p-3 w-full rounded mt-3"
            placeholder="Enter destination URL"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
          />
          <button
            onClick={createQR}
            disabled={!url.trim() || loading !== ""}
            className="bg-black text-white w-full p-3 mt-4 rounded disabled:opacity-50"
          >
            {loading === "create" ? "Creating..." : "Generate QR"}
          </button>
        </section>

        {error && (
          <div className="bg-red-100 text-red-800 rounded p-3 mt-5">
            {error}
          </div>
        )}

        {qr && (
          <div className="mt-6">
            <section className="border rounded p-4">
              <h2 className="font-bold text-xl">QR information</h2>
              <img
                src={qr.qr_image}
                alt="Generated QR code"
                className="w-48 mx-auto border p-2 mt-4"
              />
              <p className="mt-3 break-words">
                <b>QR ID:</b> {qrId}
              </p>
              <p className="break-words">
                <b>Current destination:</b> {details?.content || url}
              </p>
              <a
                href={qr.qr_link}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 underline break-all"
              >
                Open dynamic QR link
              </a>
              <p className="mt-2">
                <b>AI status:</b> {details?.ai_status || qr.AI?.status || "Unknown"}
              </p>
              <p>
                <b>Risk score:</b> {details?.risk_score ?? qr.AI?.risk_score ?? "Unknown"}
              </p>
              <p>
                <b>Scans:</b> {details?.scans ?? 0}
              </p>
              <p>
                <b>Active:</b> {details?.active === false ? "No" : "Yes"}
              </p>
            </section>

            <section className="border rounded p-4 mt-5">
              <h2 className="font-bold text-xl">Update existing QR</h2>
              <p className="text-sm mt-1">
                The QR ID, image, link, and scan count will remain unchanged.
              </p>
              <input
                className="border p-3 w-full mt-3 rounded"
                placeholder="New destination URL"
                value={newUrl}
                onChange={(event) => setNewUrl(event.target.value)}
              />
              <button
                onClick={updateQR}
                disabled={!newUrl.trim() || loading !== ""}
                className="bg-green-600 text-white p-3 w-full mt-3 rounded disabled:opacity-50"
              >
                {loading === "update" ? "Updating..." : "Update Same QR"}
              </button>
              {updateResult && (
                <div className="bg-green-100 text-green-800 rounded p-3 mt-4">
                  <p>Update successful ✅</p>
                  <p>Destination: {updateResult.destination_url}</p>
                  <p>AI status: {updateResult.ai_status}</p>
                  <p>Risk score: {updateResult.risk_score}</p>
                  <p>QR ID unchanged: {updateResult.qr_id === qrId ? "Yes" : "No"}</p>
                </div>
              )}
            </section>

            <button
              onClick={getAnalytics}
              disabled={loading !== ""}
              className="bg-blue-600 text-white p-3 w-full mt-4 rounded disabled:opacity-50"
            >
              {loading === "details" ? "Loading..." : "Refresh Analytics"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
