SELECT * from untitled_table_4

INNER JOIN dni;

SELECT * from untitled_table_4
inner join dni
on untitled_table_4.id = dni.id;

---es lo mismo que esta escrito arriba pero sin el inner, funciona exactamente igual bro.---
SELECT * from untitled_table_4
 join dni
on untitled_table_4.id = dni.id;

---el order by de lo ordena de forma descendente y si cambias DESC por ASC es ascendente---
 ---del mas pequeño al grande---

SELECT * from untitled_table_4
 join dni
on untitled_table_4.id = dni.id
ORDER BY age DESC;

SELECT name, dni_number from untitled_table_4
 join dni
on untitled_table_4.id = dni.id
ORDER BY age DESC;

SELECT untitled_table_4.name, compania.name from compania
join untitled_table_4

on untitled_table_4.compania_dni = compania.compania_dni;

SELECT * FROM languages1
JOIN untitled_table_4 ON languages1.id = untitled_table_4.id
JOIN languages ON languages1.languages_id = languages.languages_id;

SELECT untitled_table_4.name, languages.name, untitled_table_4.age FROM languages1
JOIN untitled_table_4 ON languages1.id = untitled_table_4.id
JOIN languages ON languages1.languages_id = languages.languages_id;
