DROP SCHEMA IF EXISTS us CASCADE;
CREATE SCHEMA us;

CREATE TABLE us.states (
  state_abbr CHAR(2),
  state TEXT,
  PRIMARY KEY (state_abbr)
);

CREATE TABLE us.cities AS (
  city_name TEXT,
  state_abbr CHAR(2),
  county_name TEXT
  FOREIGN KEY state_abbr REFERENCES us.states (state_abbr),
  PRIMARY KEY (state_abbr, city_name, county_name)
);

CREATE TABLE us.zip_codes AS (
  zip_code CHAR(5),
  city_name TEXT,
  state_abbr CHAR(2),
  FOREIGN KEY (city_name, state_abbr) REFERENCES us.cities (city_name, state_abbr),
  PRIMARY KEY (zip_code)
);

CREATE TABLE us.zip_code_points AS (
  location POINT,
  zip_code,
  FOREIGN KEY zip_code REFERENCES us.zip_codes (zip_code),
  PRIMARY KEY (location, zip_code)
);


-- states
INSERT INTO us.states
SELECT DISTINCT
  state_abbr,
  state
FROM
  temp_zip.us
;

-- cities
INSERT INTO us.cities
SELECT DISTINCT
  city_name,
  state_abbr,
  county_name
FROM
  temp_zip.us
;

-- zip_codes
INSERT INTO us.zip_codes
SELECT DISTINCT
  zip_code,
  city_name,
  state_abbr
FROM
  temp_us.zip_codes
;

-- zip_code_points 
INSERT INTO us.zip_code_points
SELECT
  POINT(longitude, latitude) as location,
  zip_code
FROM
  temp_us.zip_codes
;


CREATE INDEX ON us.zip_codes (location) USING GIST(location);
