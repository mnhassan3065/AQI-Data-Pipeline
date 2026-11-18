-- Template only: projectinitdb.sh substitutes these placeholders from .env
-- and escapes them before sending the SQL to MySQL.
CREATE USER IF NOT EXISTS %(user)s@'localhost' IDENTIFIED WITH caching_sha2_password BY %(password)s;
-- ALTER makes re-runs sync the password from .env even if the user exists.
ALTER USER %(user)s@'localhost' IDENTIFIED WITH caching_sha2_password BY %(password)s;
CREATE DATABASE IF NOT EXISTS %(database)s;
GRANT ALL PRIVILEGES ON %(database)s.* TO %(user)s@'localhost';
FLUSH PRIVILEGES;
