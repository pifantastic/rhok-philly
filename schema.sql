CREATE TABLE source (
  sourceid SERIAL UNIQUE,
  sourcename TEXT
);
CREATE TABLE location (
  locid SERIAL UNIQUE,
  sourceid INTEGER REFERENCES source(sourceid),
  latit NUMERIC NOT NULL,
  longit NUMERIC NOT NULL,
  locname TEXT
);
CREATE TABLE geodata (
  geodatid SERIAL UNIQUE,
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

