CREATE DATABASE IF NOT EXISTS `pocketbook`;
CREATE DATABASE IF NOT EXISTS `pocketbook_test`;

GRANT ALL ON pocketbook.* TO 'pocketbook'@'%';
GRANT ALL ON pocketbook_test.* TO 'pocketbook'@'%';
