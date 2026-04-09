export default function GroupFilter({ user, allGrupos, activeGroup, onGroupChange, viewCount }) {
  // Administrador: dropdown con todos los grupos
  if (user.is_admin) {
    return (
      <div className="admin-filter-bar">
        <label htmlFor="filtro-grupo">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          Filtrar por grupo:
        </label>
        <select
          id="filtro-grupo"
          className="filter-select"
          value={activeGroup || ''}
          onChange={e => onGroupChange(e.target.value || null)}
        >
          <option value="">— Todos los Grupos —</option>
          {allGrupos.map(g => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
        <span className="filter-count">{viewCount} registros</span>
      </div>
    )
  }

  // Usuario con un solo grupo: sin tabs
  if (user.grupos.length <= 1) return null

  // Usuario con múltiples grupos: tabs
  return (
    <div className="tabs">
      {user.grupos.map(g => (
        <button
          key={g}
          className={`tab-btn ${activeGroup === g ? 'active' : ''}`}
          onClick={() => onGroupChange(g)}
        >
          {g.charAt(0).toUpperCase() + g.slice(1)}
        </button>
      ))}
    </div>
  )
}
