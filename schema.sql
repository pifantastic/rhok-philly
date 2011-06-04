CREATE TYPE SOURCE AS ENUM('sat','ground');

CREATE TABLE location (
  locid SERIAL UNIQUE,
  sourceid SOURCE NOT NULL,
  lat NUMERIC NOT NULL,
  lng NUMERIC NOT NULL,
  stationid INT UNIQUE,
  locname TEXT
);
CREATE TABLE geodata (
  geodataid SERIAL UNIQUE,
  date DATE,
  locid INTEGER REFERENCES location(locid),
  solarradiation DOUBLE PRECISION,
  tempmax DOUBLE PRECISION,
  tempmin DOUBLE PRECISION,
  tempmedian DOUBLE PRECISION,
  rain DOUBLE PRECISION,
  wind DOUBLE PRECISION,
  dewpoint DOUBLE PRECISION,
  humidity DOUBLE PRECISION
);

