// ══════════════════════════════════════════════════════════════
//  Configuración del sistema — fuente de verdad del frontend
// ══════════════════════════════════════════════════════════════

// ── Etiquetas legibles para los códigos de grupo ───────────────
export const GRUPO_LABELS = {
  COSE:  'Cosecha',
  CHAN:  'Chantilin',
  ALFON: 'San Alfonso',
  SEBA:  'San Sebastián',
  FELI:  'San Felipe',
}

// ── Usuarios del sistema ───────────────────────────────────────
// grupos:   códigos exactos del campo "grupo" que devuelve la API
// is_admin: true  → ve todos los grupos + filtro
//           false → solo ve sus grupos asignados
export const USERS = [
  {
    email:    'luis.toctaguano@nintanga.com.ec',
    nombre:   'Luis Toctaguano',
    grupos:   ['COSE', 'CHAN'],
    is_admin: false,
  },
  {
    email:    'nelson.garcia@nintanga.com.ec',
    nombre:   'Nelson García',
    grupos:   ['ALFON'],
    is_admin: false,
  },
  {
    email:    'jhonatan.curicho@nintanga.com.ec',
    nombre:   'Jhonatan Curicho',
    grupos:   ['SEBA'],
    is_admin: false,
  },
  {
    email:    'milton.quimbiamba@nintanga.com.ec',
    nombre:   'Milton Quimbiamba',
    grupos:   ['FELI'],
    is_admin: false,
  },
  {
    email:    'pchimba@provefrut.com',
    nombre:   'Omar Chimba',
    grupos:   [],
    is_admin: true,
  },
  {
    email:    'msangucho@provefrut.com',
    nombre:   'Miguel Sangucho',
    grupos:   [],
    is_admin: true,
  },
]

// ── Helper: obtener etiqueta de un código ──────────────────────
export const getGrupoLabel = (codigo) =>
  GRUPO_LABELS[codigo] ?? codigo

// ── Helper: obtener grupos de un usuario por email ─────────────
export const getUsuario = (email) =>
  USERS.find(u => u.email === email) ?? null
