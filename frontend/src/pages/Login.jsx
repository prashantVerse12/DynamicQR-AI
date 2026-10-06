import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginUser, setToken } from "../api/api";

function getErrorMessage(error, fallback) {
  if (!error.response) {
    return "Backend unavailable. Make sure the FastAPI server is running on port 8000.";
  }
  return error.response.data?.detail || fallback;
}

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await loginUser(email, password);
      setToken(response.data.access_token);
      navigate(location.state?.from || "/dashboard", { replace: true });
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Login failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <form onSubmit={submit} className="bg-white shadow-xl rounded-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6">Sign in to Dynamic QR AI</h1>
        {error && <p className="bg-red-100 text-red-800 rounded p-3 mb-4">{error}</p>}
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
          {loading ? "Signing in..." : "Login"}
        </button>
        <p className="mt-4 text-center">
          Need an account? <Link className="text-blue-600 underline" to="/register">Register</Link>
        </p>
      </form>
    </div>
  );
}

export default Login;
