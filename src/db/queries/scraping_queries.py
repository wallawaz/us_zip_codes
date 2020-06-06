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

QUERY_RANDOM_ZIPCODE = """
SELECT
    location[0] as longitude,
    location[1] as latitude,
    zip_code
FROM
    us.zip_codes
ORDER BY
    RANDOM()
LIMIT 1
"""
