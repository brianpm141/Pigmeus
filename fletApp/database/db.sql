// Definición del ENUM para los roles
Enum user_roles {
  "Básico"
  "Gerente"
  "Administrador"
}

Table passwords {
  id integer [primary key, increment]
  hash varchar(255) [not null]
}

Table departamentos {
  id integer [primary key, increment]
  nombre varchar(100) [unique, not null]
  code integer [not null]
  status integer [default: 1, note: "1=Activo, 0=Baja"]
  created_at timestamptz [default: `now()`]
}

Table usuarios {
  id integer [primary key, increment]
  username varchar(30) [unique, not null]
  pass_id integer [not null]
  nombre varchar(100) [not null]
  apellidos varchar(100) [not null]
  matricula varchar(50) [unique, not null]
  
  // Uso del ENUM aquí
  role user_roles [default: "Básico", not null]
  
  // Este campo es VITAL para filtrar todo por departamento
  departamento_id integer [not null]
  
  status integer [default: 1]
  created_at timestamptz [default: `now()`]
}

Table categorias {
  id integer [primary key, increment]
  nombre varchar(100) [not null]
  // Necesario aquí para filtrar qué categorías ve cada depto
  departamento_id integer [not null] 
  status integer [default: 1]
  created_at timestamptz [default: `now()`]
}

Table proyectos {
  id integer [primary key, increment]
  nombre varchar(100) [not null] // Agregado not null
  descripcion varchar(180) [null]
  estado integer [default: 0, note: "0=Pendiente, 1=Proceso, 2=Terminado"]
  responsable_id integer [null, note:"Si es null se marca para todo el departamento"]
  // El proyecto pertenece al departamento (independiente de quién lo cree)
  departamento_id integer [not null]
  status integer [default: 1]
  fecha_est timestamptz [null]
  fecha_mov timestamptz [null]
  created_at timestamptz [default: `now()`]
}

Table actividades {
  id integer [primary key, increment]
  descripcion varchar(255) [not null]
  
  horainicio timestamptz [not null]
  horacierre timestamptz [null]
  
  estado integer [default: 0, note: "0=Pendiente, 1=Completa"]
  tipo integer [not null, note: "0=General, 1=De Proyecto"]
  
  // El "dueño" de la actividad. De aquí sacamos el departamento.
  usuario_id integer [not null]
  
  categoria_id integer [not null]
  proyecto_id integer [null, note: "Nulo si es actividad general"]
  
  status integer [default: 1]
  created_at timestamptz [default: `now()`]
}

Table colaborador {
  id integer [primary key]
  actividad integer [not null]
  usuario integer [not null]
  status integer [default: 1]
  created_at timestamptz [default: `now()`]
}

Table pendientes {
  id integer [primary key]
  descripcion varchar(120) [not null]
  fecha_asignada timestamptz [null]
  fecha_completada timestamptz [null]
  estado integer [default: 0, note: "0=Pendiente, 1=Completa"]
  categoria integer [not null]
  usuario integer [not null]
  status integer [default: 1]
  created_at timestamptz [default: `now()`]
}

// --- RELACIONES ---

// 1 a 1 (Usuario - Password)
Ref: usuarios.pass_id - passwords.id

// Usuarios pertenecen a Departamentos
Ref: usuarios.departamento_id > departamentos.id

// Categorías pertenecen a Departamentos (Para filtrar listas desplegables)
Ref: categorias.departamento_id > departamentos.id

// Proyectos pertenecen a Departamentos
Ref: proyectos.departamento_id > departamentos.id
Ref: proyectos.responsable_id > usuarios.id

// Actividades
// Al eliminar departamento_id de aquí, la cascada de seguridad es:
// Actividad -> Usuario -> Departamento.
Ref: actividades.usuario_id > usuarios.id
Ref: actividades.categoria_id > categorias.id
Ref: actividades.proyecto_id > proyectos.id

Ref: colaborador.actividad > actividades.id
Ref: colaborador.usuario > usuarios.id

Ref: pendientes.usuario > usuarios.id
Ref: pendientes.categoria > categorias.id