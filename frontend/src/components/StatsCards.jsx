export default function StatsCards({ data }) {
  const total       = data.length
  const conIngreso  = data.filter(r => r.ingreso).length
  const sinSalida   = data.filter(r => r.ingreso && !r.salida).length
  const sinRegistro = data.filter(r => !r.ingreso).length

  return (
    <div className="stats">
      <div className="stat-card">
        <div className="label">Total empleados</div>
        <div className="value">{total}</div>
      </div>
      <div className="stat-card green">
        <div className="label">Con ingreso</div>
        <div className="value">{conIngreso}</div>
      </div>
      <div className="stat-card orange">
        <div className="label">Sin salida</div>
        <div className="value">{sinSalida}</div>
      </div>
      <div className="stat-card red">
        <div className="label">Sin registro</div>
        <div className="value">{sinRegistro}</div>
      </div>
    </div>
  )
}
