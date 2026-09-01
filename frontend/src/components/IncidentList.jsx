import SeverityBadge from "./SeverityBadge";

export default function IncidentList({ incidents }) {
  if (incidents.length === 0) {
    return <p className="centered-message">Nenhum incidente encontrado.</p>;
  }

  return (
    <table className="incident-table">
      <thead>
        <tr>
          <th>Título</th>
          <th>Tipo</th>
          <th>Severidade</th>
          <th>Status</th>
          <th>Criado em</th>
        </tr>
      </thead>
      <tbody>
        {incidents.map((incident) => (
          <tr key={incident.id}>
            <td>{incident.title}</td>
            <td>{incident.type}</td>
            <td>
              <SeverityBadge severity={incident.severity} />
            </td>
            <td>{incident.status}</td>
            <td>{new Date(incident.created_at).toLocaleString("pt-BR")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
