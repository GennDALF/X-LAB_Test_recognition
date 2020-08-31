-- this is an example query, to check set your own table name and datetime interval
-- if using only dates in timestamps don't forget that it means YYYY-MM-DDT00:00:00.000Z

SELECT to_char(datetime, 'YYYY-MM-DD') as "Date",
	   action_result as "Action result",
       count(1) as "Number of calls",
       sum(speech_duration) as "Total duration",
       p.name as "Project name",
       s.name as "Server name"
FROM results
	INNER JOIN project as p
    	ON project_id = p.id
    INNER JOIN server as s
    	ON server_id = s.id
WHERE datetime BETWEEN '2020-08-30' and '2020-08-31'
GROUP BY "Date", action_result, p.name, s.name
