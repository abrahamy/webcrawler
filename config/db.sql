----------------------------------------------
--# Enable hstore extension on the database --#
----------------------------------------------
CREATE EXTENSION IF NOT EXISTS hstore;

-----------------------------------------------------------
--# create a user with read-only access to the database --#
-----------------------------------------------------------
CREATE ROLE IF NOT EXISTS cmsl WITH LOGIN ENCRYPTED PASSWORD 'cmslpass';
GRANT CONNECT ON DATABASE webcrawler TO cmsl;
GRANT USAGE ON SCHEMA public TO cmsl;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cmsl;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO cmsl;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO cmsl;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO cmsl;