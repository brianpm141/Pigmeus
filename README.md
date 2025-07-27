# RegistroSoporte
Un mini codigo para registrar actividades de atencion a cliente de forma rapida.

### Feo pero funcional

Permite registrar llamadas de soporte junto con el usuario que la atendio y poder exportarlo en formato excel.

## Registro de llamadas
 Permite registrar la hora y fecha exacta del registro de la llamada solo seleccionando el usuario que la recibio y la categoria

 ![error_141](Capturas/Reportes.png)

+ Registra las llamadas y se quedan pendientes
+ Se puede actualizar el estado de una llamada cuando se completa la atencion

## Registro de usuarios

![error_141](Capturas/usuarios_categorias.png)

+ Permite registrar los usuarios que dan atencion
+ Permite registrar las diversas categorias de llamadas

## Exportar a excel 

Permite exportar la informacion a tablas de exel con el mismo orden y formato 

![error_141](Capturas/excel.png)

# Como Ejecutar?

El archivo es un ejecutable basico, que a la hora de que se activa por primera vez genera un archivo sqlite para almacenar los datos historicos

![error_141](Capturas/archivos.png)

No necesita dependencias extras o python, solo estar en la misma carpeta donde esta el archivo de base de datos