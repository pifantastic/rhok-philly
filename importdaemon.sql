-- Tables related to files and importing

CREATE TABLE datasource (
	datsourceid SERIAL UNIQUE,
	sourcename TEXT UNIQUE,
	updinterval INTERVAL, -- Leave NULL for manual updates only
	lastupdate TIMESTAMP, -- Will initially be NULL, ideally never after
	sourcetype VARCHAR(10) NOT NULL,
	site TEXT,
	path TEXT,
	login VARCHAR(20),
	pass VARCHAR(20)
);

CREATE TABLE datafile (


);

CREATE FUNCTION source_is_current(INTEGER) RETURNS BOOLEAN AS '
	DECLARE
		sid ALIAS FOR $1;
		last TIMESTAMP;
		intv INTERVAL;
	BEGIN
		SELECT INTO last lastupdate FROM datasource WHERE datsourceid=sid;
		SELECT INTO intv updinterval FROM datasource WHERE datsourceid=sid;

		IF intv IS NULL THEN
			RETURN TRUE; -- We are always current if there is no interval
		END IF;
		IF last IS NULL THEN
			RETURN FALSE; -- Never updated!
		END IF;
		IF last + intv < now() THEN
			RETURN FALSE; -- Overdue!
		ELSE
			RETURN TRUE;
		END IF;
	END;
' LANGUAGE 'plpgsql';

