SELECT  name from untitled_table_4
UNION
SELECT  name from languages;


SELECT * from untitled_table_4
LEFT JOIN dni
on untitled_table_4.id = dni.id
UNION
SELECT * from untitled_table_4
RIGHT JOIN dni
on untitled_table_4.id = dni.id
;