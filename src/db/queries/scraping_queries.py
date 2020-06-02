QUERY_SEARCH_STRING = """
SELECT
    a.zipcode,
    a.longitude,
    a.latitude
FROM
    us.zip_codes a
WHERE
    a.zipcode NOT IN %s
    AND NOT EXISTS (
        SELECT
            1
        FROM
            delivery.service_lookups sl
        WHERE
            sl.service_name = %s
            AND sl.zipcode = a.zipcode
    )
    LIMIT 1
"""
