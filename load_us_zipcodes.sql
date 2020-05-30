BEGIN;

DROP SCHEMA IF EXISTS us CASCADE;
CREATE SCHEMA us;

CREATE TABLE us.states (
  state_abbr CHAR(2),
  state TEXT,
  PRIMARY KEY (state_abbr)
);

CREATE TABLE us.cities (
  city_id SERIAL,
  city_name TEXT,
  state_abbr CHAR(2),
  county_name TEXT,
  FOREIGN KEY (state_abbr) REFERENCES us.states (state_abbr),
  PRIMARY KEY (city_id),
  UNIQUE (city_name, state_abbr, county_name)
);

CREATE TABLE us.zip_codes (
  zip_code CHAR(5),
  city_id INT,
  location POINT,
  FOREIGN KEY (city_id) REFERENCES us.cities (city_id),
  PRIMARY KEY (zip_code, city_id)
);
COMMENT ON COLUMN us.zip_codes.location is '[longitude,latitude]';

-- states
INSERT INTO us.states
SELECT DISTINCT
  state_abbr,
  state
FROM
  temp_zip.us
;

-- cities
INSERT INTO us.cities (city_name, state_abbr, county_name)
SELECT DISTINCT
  city,
  state_abbr,
  county_area
FROM
  temp_zip.us
WHERE
  state_abbr IS NOT NULL
  AND county_area IS NOT NULL
;

-- zip_codes
INSERT INTO us.zip_codes (zip_code, city_id, location)
WITH distinct_points AS (
  SELECT DISTINCT
    a.zipcode,
    b.city_id,
    longitude,
    latitude
  FROM
    temp_zip.us a
    JOIN us.cities b
      ON a.city = b.city_name
      AND a.state_abbr = b.state_abbr
      AND a.county_area = b.county_name
  WHERE
    longitude IS NOT NULL
    AND latitude IS NOT NULL
  )
SELECT
  zipcode,
  city_id,
  POINT(longitude, latitude)
FROM
  distinct_points a
;

CREATE INDEX ON us.zip_codes USING GIST(location);
CREATE EXTENSION if not exists "uuid-ossp";

COMMIT;
