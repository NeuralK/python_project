SELECT min(age) FROM untitled_table_4 GROUP BY age

SELECT COUNT(age), age FROM untitled_table_4 GROUP BY age

SELECT COUNT(age), age FROM untitled_table_4 GROUP BY age ORDER BY age  ASC
SELECT COUNT(age), age FROM untitled_table_4 WHERE age < 50 GROUP BY age ORDER BY age  ASC