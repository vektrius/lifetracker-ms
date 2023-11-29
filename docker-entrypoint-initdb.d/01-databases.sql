CREATE DATABASE IF NOT EXISTS `lifetracker_auth`;
CREATE DATABASE IF NOT EXISTS `lifetracker_transactions`;

GRANT ALL PRIVILEGES ON *.* TO 'lifetracker'@'%';