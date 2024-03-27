from sqlalchemy import text

METRIC1_QUERY = text("""
    SELECT
        d.department,
        j.job,
        SUM(CASE WHEN EXTRACT(MONTH FROM TO_TIMESTAMP(e.datetime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')) BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS Q1,
        SUM(CASE WHEN EXTRACT(MONTH FROM TO_TIMESTAMP(e.datetime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')) BETWEEN 4 AND 6 THEN 1 ELSE 0 END) AS Q2,
        SUM(CASE WHEN EXTRACT(MONTH FROM TO_TIMESTAMP(e.datetime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')) BETWEEN 7 AND 9 THEN 1 ELSE 0 END) AS Q3,
        SUM(CASE WHEN EXTRACT(MONTH FROM TO_TIMESTAMP(e.datetime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')) BETWEEN 10 AND 12 THEN 1 ELSE 0 END) AS Q4
    FROM
        hired_employees e
    JOIN
        jobs j ON e.job_id = j.id
    JOIN
        departments d ON e.department_id = d.id
    WHERE
        SUBSTRING(e.datetime, 1, 4) = '2021'
    GROUP BY
        d.department, j.job
    ORDER BY
        d.department, j.job;
    """)

METRIC2_QUERY = text("""
    WITH department_stats AS (
        SELECT
            d.id AS department_id,
            d.department,
            COUNT(e.id) AS num_employees_hired
        FROM
            departments d
        LEFT JOIN
            hired_employees e ON d.id = e.department_id AND EXTRACT(YEAR FROM TO_TIMESTAMP(e.datetime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')) = 2021
        GROUP BY
            d.id, d.department
    ),
    mean_num_employees AS (
        SELECT
            AVG(num_employees_hired) AS mean_num_employees
        FROM
            department_stats
    )
    SELECT
        department_id as id,
        department as department,
        num_employees_hired as hired
    FROM
        department_stats
    CROSS JOIN
        mean_num_employees
    WHERE
        num_employees_hired > mean_num_employees
    ORDER BY
        num_employees_hired DESC;
""")