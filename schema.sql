CREATE TYPE SOURCE AS ENUM('sat','ground');

CREATE TABLE location (
  locid SERIAL UNIQUE,
  sourceid SOURCE NOT NULL,
  lat NUMERIC NOT NULL,
  lng NUMERIC NOT NULL,
  stationid INT UNIQUE,
  locname TEXT
);

CREATE TABLE geotimespace (
  geotsid SERIAL UNIQUE,
  date DATE,
  locid INTEGER REFERENCES location(locid)
--  solarradiation DOUBLE PRECISION,
--  tempmax DOUBLE PRECISION,
--  tempmin DOUBLE PRECISION,
--  tempmedian DOUBLE PRECISION,
--  rain DOUBLE PRECISION,
--  wind DOUBLE PRECISION,
--  dewpoint DOUBLE PRECISION,
--  humidity DOUBLE PRECISION
);

CREATE TABLE geofield (
  fieldid SERIAL UNIQUE NOT NULL,
  fieldname VARCHAR(30) UNIQUE NOT NULL
);

INSERT INTO geofield(fieldname) VALUES ('solarradiation');
INSERT INTO geofield(fieldname) VALUES ('tempmax');
INSERT INTO geofield(fieldname) VALUES ('tempmin');
INSERT INTO geofield(fieldname) VALUES ('tempmedian');
INSERT INTO geofield(fieldname) VALUES ('rain');
INSERT INTO geofield(fieldname) VALUES ('wind');
INSERT INTO geofield(fieldname) VALUES ('dewpoint');
INSERT INTO geofield(fieldname) VALUES ('humidity');

CREATE TABLE geovalue (
  geovalueid SERIAL UNIQUE,
  geotsid INTEGER REFERENCES geotimespace(geotsid),
  geofieldid INTEGER REFERENCES geofield(fieldid),
  geoval DOUBLE PRECISION
);

GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO apache;
GRANT ALL ON ALL TABLES IN SCHEMA public TO apache;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO apache;
