import { useCallback, useEffect, useState } from "react";
import { listIncidents } from "../api/incidents";
import { extractErrorMessage } from "../api/client";
import IncidentFilters from "../components/IncidentFilters";
import IncidentForm from "../components/IncidentForm";
import IncidentList from "../components/IncidentList";
import Navbar from "../components/Navbar";
import Pagination from "../components/Pagination";
import SeverityChart from "../components/SeverityChart";

const CHART_SAMPLE_LIMIT = 100;

export default function IncidentsPage() {
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const [pageData, setPageData] = useState({ items: [], total: 0, total_pages: 0 });
  const [chartIncidents, setChartIncidents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [pageResult, chartResult] = await Promise.all([
        listIncidents({ page, limit: 10, severity, status }),
        listIncidents({ page: 1, limit: CHART_SAMPLE_LIMIT, severity, status }),
      ]);
      setPageData(pageResult);
      setChartIncidents(chartResult.items);
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível carregar os incidentes."));
    } finally {
      setLoading(false);
    }
  }, [page, severity, status]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  function handleFilterChange({ severity: nextSeverity, status: nextStatus }) {
    setSeverity(nextSeverity);
    setStatus(nextStatus);
    setPage(1);
  }

  function handleCreated() {
    setShowForm(false);
    setPage(1);
    fetchIncidents();
  }

  return (
    <div className="app-shell">
      <Navbar />

      <main className="content">
        <SeverityChart incidents={chartIncidents} />

        <section className="incidents-section">
          <div className="incidents-header">
            <h2>Incidentes ({pageData.total})</h2>
            <button type="button" onClick={() => setShowForm((v) => !v)}>
              {showForm ? "Cancelar" : "+ Novo incidente"}
            </button>
          </div>

          {showForm && <IncidentForm onCreated={handleCreated} />}

          <IncidentFilters severity={severity} status={status} onChange={handleFilterChange} />

          {error && <p className="error-message">{error}</p>}
          {loading ? (
            <p className="centered-message">Carregando...</p>
          ) : (
            <>
              <IncidentList incidents={pageData.items} />
              <Pagination page={pageData.page || page} totalPages={pageData.total_pages} onPageChange={setPage} />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
