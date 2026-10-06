import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createQr, getMyQrs, logout } from "../api/api";
import QRCard from "../components/QRCard";

function getErrorMessage(error, fallback) {
  if (!error.response) return "Backend unavailable. Make sure the FastAPI server is running on port 8000.";
  return error.response.data?.detail || fallback;
}

function Dashboard() {
  const navigate = useNavigate();
  const [qrs, setQrs] = useState([]);
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");

  const loadQrs = useCallback(async () => {
    setError("");
    setLoading("list");
    try {
      const response = await getMyQrs();
      setQrs(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load your QR codes."));
    } finally {
      setLoading("");
    }
  }, []);

  useEffect(() => {
    const timerId = setTimeout(() => {
      loadQrs();
    }, 0);

    return () => clearTimeout(timerId);
  }, [loadQrs]);

  const createQR = async (event) => {
    event.preventDefault();
    setError("");
    setLoading("create");
    try {
      await createQr(url);
      setUrl("");
      await loadQrs();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "QR creation failed."));
    } finally {
      setLoading("");
    }
  };

  const signOut = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const updateQrInList = (updated) => {
    setQrs((current) => current.map((qr) => qr.qr_id === updated.qr_id ? { ...qr, ...updated } : qr));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <header className="max-w-6xl mx-auto flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dynamic QR AI Dashboard</h1>
        <button onClick={signOut} className="border border-black px-4 py-2 rounded">Logout</button>
      </header>
      <main className="max-w-6xl mx-auto">
        <form onSubmit={createQR} className="bg-white shadow-xl rounded-xl p-5 mb-6">
          <h2 className="font-bold text-xl">Create QR</h2>
          <div className="flex gap-3 mt-3 flex-col sm:flex-row">
            <input
              required
              type="url"
              placeholder="Enter destination URL"
              className="border p-3 rounded flex-1"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
            <button type="submit" disabled={loading !== ""} className="bg-black text-white px-5 py-3 rounded disabled:opacity-50">
              {loading === "create" ? "Creating..." : "Generate QR"}
            </button>
          </div>
        </form>
        {error && <p className="bg-red-100 text-red-800 rounded p-3 mb-6">{error}</p>}
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold text-2xl">Your QR codes ({qrs.length})</h2>
          {loading === "list" && <span>Loading...</span>}
        </div>
        {!loading && qrs.length === 0 && (
          <div className="bg-white shadow-xl rounded-xl p-8 text-center">
            <h3 className="font-bold text-xl">No QR codes yet</h3>
            <p className="mt-2">Create your first QR code above.</p>
          </div>
        )}
        <div className="grid gap-6 md:grid-cols-2">
          {qrs.map((qr) => (
            <QRCard key={qr.qr_id} qr={qr} onChanged={updateQrInList} />
          ))}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
