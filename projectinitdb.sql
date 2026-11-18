-- Template only: projectinitdb.sh substitutes these placeholders from .env
-- and escapes them before sending the SQL to MySQL.
CREATE USER IF NOT EXISTS %(user)s@'localhost' IDENTIFIED WITH caching_sha2_password BY %(password)s;
CREATE DATABASE IF NOT EXISTS %(database)s;
GRANT ALL PRIVILEGES ON %(database)s.* TO %(user)s@'localhost';
FLUSH PRIVILEGES;
