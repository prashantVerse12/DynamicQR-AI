import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/api";

function getErrorMessage(error, fallback) {
  if (!error.response) {
    return "Backend unavailable. Make sure the FastAPI server is running on port 8000.";
  }
  return error.response.data?.detail || fallback;
}

function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await registerUser(email, password);
      setSuccess("Registration successful. Redirecting to login...");
      setTimeout(() => navigate("/login"), 700);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <form onSubmit={submit} className="bg-white shadow-xl rounded-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6">Create an account</h1>
        {error && <p className="bg-red-100 text-red-800 rounded p-3 mb-4">{error}</p>}
        {success && <p className="bg-green-100 text-green-800 rounded p-3 mb-4">{success}</p>}
        <label className="block font-semibold">
          Email
          <input
            type="email"
            required
            className="border p-3 w-full rounded mt-2"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="block font-semibold mt-4">
          Password
          <input
            type="password"
            required
            className="border p-3 w-full rounded mt-2"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="bg-black text-white w-full p-3 mt-6 rounded disabled:opacity-50"
        >
          {loading ? "Creating..." : "Register"}
        </button>
        <p className="mt-4 text-center">
          Already registered? <Link className="text-blue-600 underline" to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}

export default Register;
