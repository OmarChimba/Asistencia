const PAGE_SIZE = 50

function StatusPill({ ingreso, salida }) {
  if (!ingreso) return <span className="pill pill-red">Sin registro</span>
  if (!salida)  return <span className="pill pill-orange">En sede</span>
  return <span className="pill pill-green">Completo</span>
}

const fmt = t => t ? t.substring(0, 5) : '—'

export default function AttendanceTable({ title, data, search, onSearch, page, onPageChange }) {
  const totalPages = Math.ceil(data.length / PAGE_SIZE) || 1
  const pageData   = data.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="table-wrap">
      <div className="table-header">
        <h3>{title}</h3>
        <input
          className="search-input"
          type="text"
          placeholder="Buscar empleado..."
          value={search}
          onChange={e => onSearch(e.target.value)}
        />
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Ingreso</th>
              <th>Salida</th>
            </tr>
          </thead>
          <tbody>
            {pageData.length === 0 ? (
              <tr>
                <td colSpan={4} className="empty">No se encontraron registros</td>
              </tr>
            ) : (
              pageData.map((r, i) => (
                <tr key={i}>
                  <td>{r.codigo}</td>
                  <td>{r.apellido_nombre}</td>
                  <td>{fmt(r.ingreso)}</td>
                  <td>{fmt(r.salida)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <span>Pág. {page} de {totalPages} ({data.length} registros)</span>
      <div className="pagination-btns">
        <button disabled={page <= 1} onClick={() => onPageChange(p => p - 1)}>← Ant.</button>
        <button disabled={page >= totalPages} onClick={() => onPageChange(p => p + 1)}>Sig. →</button>
      </div>
      </div>
    </div>
  )
}
