import { useState } from 'react';

export default function useApiAction() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const run = async (fn) => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await fn();
      const d = res.data;
      const msg = d?.message || d?.ok ? JSON.stringify(d, null, 2) : JSON.stringify(d, null, 2);
      setStatus({ type: 'success', message: msg });
      return d;
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.message || err.message;
      setStatus({ type: 'error', message: msg });
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clear = () => setStatus(null);

  return { loading, status, run, clear };
}
