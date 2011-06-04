CREATE TABLE source (
  sourceid SERIAL UNIQUE,
  sourcename TEXT
);
CREATE TABLE location (
  locid SERIAL UNIQUE,
  sourceid INTEGER REFERENCES source(sourceid),
  lat NUMERIC NOT NULL,
  lng NUMERIC NOT NULL,
  locname TEXT
);
CREATE TABLE geodata (
  geodataid SERIAL UNIQUE,
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

