SELECT * FROM untitled_table_4 WHERE capibara IS NULL;

SELECT * FROM untitled_table_4 WHERE capibara IS NOT NULL;

SELECT * FROM untitled_table_4 WHERE capibara IS NOT NULL AND age = 98;
SELECT * FROM untitled_table_4 WHERE capibara IS NOT NULL OR age = 98;

SELECT ifnull(name, "guess") AS name, ifnull(age, 0) AS age FROM untitled_table_4;