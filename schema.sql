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

CREATE INDEX ON geotimespace(locid);
CREATE INDEX ON geotimespace(date);
CREATE INDEX ON geovalue(geotsid);


GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO apache;
GRANT ALL ON ALL TABLES IN SCHEMA public TO apache;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO apache;
