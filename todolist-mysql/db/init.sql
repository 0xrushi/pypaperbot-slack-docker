create database db_tasks;
use db_tasks;
create table tasks (
    id INT(10) NOT NULL AUTO_INCREMENT,
    title VARCHAR(10) NOT NULL,
    PRIMARY KEY (id)
);
