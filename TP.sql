CREATE DATABASE lab_db;
use lab_db;

CREATE TABLE Users (
    ID_u INT PRIMARY KEY,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    filiere VARCHAR(100)
);

CREATE TABLE Avis (
    ID_enseignant INT PRIMARY KEY,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    specialite VARCHAR(100)
);

CREATE TABLE Activites (
    ID_module INT PRIMARY KEY,
    institule VARCHAR(100),
    ID_enseignant INT REFERENCES ENSEIGNANT(ID_enseignant)
);

CREATE TABLE Question (
    id_note INT PRIMARY KEY,
    ID_etudiant INT REFERENCES ETUDIANT(ID_etudiant),
    ID_module INT REFERENCES MODULE(ID_module),
    note FLOAT
);

CREATE TABLE Responsable(
    id_note INT PRIMARY KEY,
    ID_etudiant INT REFERENCES ETUDIANT(ID_etudiant),
    ID_module INT REFERENCES MODULE(ID_module),
    note FLOAT
);

CREATE TABLE Reponsable(
    id_note INT PRIMARY KEY,
    ID_etudiant INT REFERENCES ETUDIANT(ID_etudiant),
    ID_module INT REFERENCES MODULE(ID_module),
    note FLOAT
);

INSERT INTO ETUDIANT (ID_etudiant, nom, prenom, filiere) VALUES
(1, 'NDIAYE', 'PAUL', 'Informatique 2'),
(2, 'KAMGA', 'Alice', 'informatique 3'),
(3, 'TCHOUA', 'MARC', 'Reseaux 4'),
(4, 'MBARGA', 'sarah', 'Informatique 2');

INSERT INTO ENSEIGNANT (ID_enseignant, nom, prenom, specialite) VALUES
(1, 'DUPONT', 'ALAIN', 'BASE DE DONNEES'),
(2, 'Martin', 'lucien', 'Reseaux'),
(3, 'NGONO', 'ROSANE', 'PROGRAMMATION');

INSERT INTO MODULE (ID_module, institule, ID_enseignant) VALUES
(1, 'SQL avance', 1),
(2, 'Reseaux TCP/IP', 2),
(3, 'JAVA', 3);

INSERT INTO NOTE (id_note, ID_etudiant, ID_module, note) VALUES
(1, 1, 1, 14),
(2, 1, 3, 12),
(3, 2, 1, 16),
(4, 2, 3, 15),
(5, 3, 2, 10),
(6, 4, 1, 09);

