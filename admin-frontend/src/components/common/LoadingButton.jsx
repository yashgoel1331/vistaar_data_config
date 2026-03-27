export default function LoadingButton({ children, loading, className = '', ...rest }) {
  return (
    <button
      disabled={loading}
      className={`px-4 py-2 text-sm rounded text-white disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...rest}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
