CREATE DATABASE studydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'studyuser'@'localhost' IDENTIFIED BY 'study_pass123';
GRANT ALL PRIVILEGES ON studydb.* TO 'studyuser'@'localhost';
FLUSH PRIVILEGES;
	
