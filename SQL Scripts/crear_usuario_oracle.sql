-- Primer bloque a ejecutar
alter session set "_ORACLE_SCRIPT"= true;

-- Segundo bloque a ejecutar 

create user user_django_adecar identified by "Adecar.321";

-- tercer bloque a ejecutar

grant "CONNECT" TO user_django_adecar;

-- Ahora vamos al usuario creado y vamos a editar usuario 


