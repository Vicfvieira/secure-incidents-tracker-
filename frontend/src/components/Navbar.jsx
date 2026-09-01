import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <span className="navbar-title">🛡️ Secure Incidents Tracker</span>
      {user && (
        <div className="navbar-user">
          <span>
            {user.full_name} <span className="role-tag">{user.role}</span>
          </span>
          <button type="button" onClick={logout} className="btn-secondary">
            Sair
          </button>
        </div>
      )}
    </header>
  );
}
