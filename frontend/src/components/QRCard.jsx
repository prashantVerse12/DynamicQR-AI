import { useState } from "react";
import { getQrDetails, updateQr } from "../api/api";
import ContentEditor from "./ContentEditor";
import { createDefaultForm, parseFormContent } from "./formDefinitionUtils";
import SecurityBadge from "./SecurityBadge";

function getErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (detail?.message) {
    const reasons = detail.ai_report?.reasons;
    return reasons?.length ? `${detail.message} ${reasons.join(". ")}.` : detail.message;
  }
  if (!error.response) return "Backend unavailable. Make sure the FastAPI server is running on port 8000.";
  if (error.response.status === 422) return "The content did not pass backend validation.";
  return fallback;
}

function QRCard({ qr, onChanged }) {
  const initialType = qr.content_type || "URL";
  const [contentType, setContentType] = useState(initialType);
  const [content, setContent] = useState(
    initialType === "FORM" ? parseFormContent(qr.content) || createDefaultForm() : qr.content || "",
  );
  const [details, setDetails] = useState(qr);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");

  const refreshDetails = async () => {
    setError("");
    setLoading("details");
    try {
      const response = await getQrDetails(qr.qr_id);
      setDetails(response.data);
      const nextType = response.data.content_type || "URL";
      setContentType(nextType);
      setContent(nextType === "FORM"
        ? parseFormContent(response.data.content)
        : response.data.content || "");
      onChanged?.(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load QR details."));
    } finally {
      setLoading("");
    }
  };

  const updateContent = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading("update");
    try {
      const response = await updateQr(qr.qr_id, { contentType, content });
      const updated = {
        ...details,
        ...response.data,
        content: response.data.content,
        content_type: response.data.content_type || contentType,
      };
      setDetails(updated);
      setMessage("Update successful.");
      onChanged?.(updated);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "QR update failed."));
    } finally {
      setLoading("");
    }
  };

  return (
    <article className="bg-white shadow-xl rounded-xl p-5">
      <div className="flex justify-between gap-4 items-start">
        <div>
          <h3 className="font-bold text-lg break-all">QR ID: {qr.qr_id}</h3>
          <SecurityBadge status={details.ai_status} riskScore={details.risk_score} />
        </div>
        <span className={`rounded px-2 py-1 text-sm ${details.active ? "bg-green-100 text-green-800" : "bg-gray-200 text-gray-700"}`}>
          {details.active ? "Active" : "Inactive"}
        </span>
      </div>
      {qr.qr_image && <img src={qr.qr_image} alt={`QR code ${qr.qr_id}`} className="w-40 border p-2 mx-auto mt-4" />}
      <p className="mt-4 break-words"><b>Content type:</b> {details.content_type || "URL"}</p>
      <p className="break-words"><b>Version:</b> {details.version ?? "Version unavailable"}</p>
      <p className="break-words">
        <b>{(details.content_type || "URL") === "URL" ? "Destination" : (details.content_type || "URL") === "TEXT" ? "Text content" : "Form definition"}:</b>{" "}
        {(details.content_type || "URL") === "FORM"
          ? (parseFormContent(details.content) ? "Structured form" : "Malformed form definition")
          : details.content}
      </p>
      <p><b>Scans:</b> {details.scans ?? 0}</p>
      <a href={qr.qr_link} target="_blank" rel="noreferrer" className="text-blue-600 underline break-all">
        Open dynamic QR link
      </a>
      <form onSubmit={updateContent} className="mt-4">
        <ContentEditor
          contentType={contentType}
          content={content}
          onTypeChange={setContentType}
          onContentChange={setContent}
          disabled={loading !== ""}
        />
        <button type="submit" disabled={loading !== ""} className="bg-green-600 text-white p-3 w-full mt-3 rounded disabled:opacity-50">
          {loading === "update" ? "Updating..." : "Update Same QR"}
        </button>
      </form>
      <button onClick={refreshDetails} disabled={loading !== ""} className="bg-blue-600 text-white p-3 w-full mt-3 rounded disabled:opacity-50">
        {loading === "details" ? "Loading..." : "Refresh Analytics"}
      </button>
      {message && <p className="bg-green-100 text-green-800 rounded p-3 mt-3">{message}</p>}
      {error && <p className="bg-red-100 text-red-800 rounded p-3 mt-3">{error}</p>}
    </article>
  );
}

export default QRCard;
