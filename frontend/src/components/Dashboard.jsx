import { useState, useEffect, useMemo } from 'react'
import { getAsistencia } from '../api'
import StatsCards from './StatsCards'
import AttendanceTable from './AttendanceTable'
import GroupFilter from './GroupFilter'

function formatDate(d) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}

export default function Dashboard({ user, onLogout }) {
  const [allData,      setAllData]      = useState([])
  const [activeGroup,  setActiveGroup]  = useState(null)
  const [search,       setSearch]       = useState('')
  const [page,         setPage]         = useState(1)
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState(null)

  useEffect(() => {
    getAsistencia()
      .then(data => {
        setAllData(data)
        if (!user.is_admin && user.grupos.length > 0) {
          setActiveGroup(user.grupos[0])
        }
      })
      .catch(e => setError(e.response?.data?.detail || 'Error al cargar los datos.'))
      .finally(() => setLoading(false))
  }, [])

  // Registros del grupo/filtro activo
  const viewData = useMemo(() => {
    if (user.is_admin) {
      return activeGroup
        ? allData.filter(r => r.grupo === activeGroup)
        : allData
    }
    if (!activeGroup) return allData
    return allData.filter(r => r._tab === activeGroup)
  }, [allData, activeGroup, user.is_admin])

  // Búsqueda sobre viewData
  const filtered = useMemo(() => {
    if (!search) return viewData
    const q = search.toLowerCase()
    return viewData
      .filter(r =>
        r.apellido_nombre.toLowerCase().includes(q) ||
        String(r.codigo).includes(q)
      )
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  }, [viewData, search])

  // Grupos únicos para el dropdown admin
  const allGrupos = useMemo(() =>
    [...new Set(allData.map(r => r.grupo))].sort(),
    [allData]
  )

  const handleGroupChange = (g) => {
    setActiveGroup(g)
    setSearch('')
    setPage(1)
  }

  const handleSearch = (q) => {
    setSearch(q)
    setPage(1)
  }

  // Título de la tabla
  const tableTitle = useMemo(() => {
    if (user.is_admin) {
      return activeGroup ? `Registros — ${activeGroup}` : 'Registros — Todos los grupos'
    }
    const sample = viewData[0]
    return sample
      ? `Registros — ${sample.nombre} (${sample.grupo})`
      : (activeGroup || 'Registros')
  }, [user.is_admin, activeGroup, viewData])

  const dateLabel = allData[0] ? formatDate(allData[0].fecha) : ''

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        <span>Cargando datos...</span>
      </div>
    )
  }

  return (
    <div className="report-page">
      {/* Info bar */}
      <div className="info-bar">
        <div className="info-bar-left">
          <span className="user-chip">
            <i className="bx bxs-user" style={{fontSize: '15px'}} />
            {user.nombre}
          </span>
          {user.is_admin && <span className="admin-chip">Administrador</span>}
          {dateLabel && (
            <span className="badge">
              <span className="dot" />
              {dateLabel}
            </span>
          )}
        </div>
        <button className="btn-logout" onClick={onLogout}>
          <i className="bx bx-log-out" style={{fontSize: '16px'}} />
          Cerrar sesión
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Filtro de grupo */}
      <GroupFilter
        user={user}
        allGrupos={allGrupos}
        activeGroup={activeGroup}
        onGroupChange={handleGroupChange}
        viewCount={viewData.length}
      />

      {/* Estadísticas */}
      <StatsCards data={viewData} />

      {/* Tabla */}
      <AttendanceTable
        title={tableTitle}
        data={filtered}
        search={search}
        onSearch={handleSearch}
        page={page}
        onPageChange={setPage}
      />
    </div>
  )
}
