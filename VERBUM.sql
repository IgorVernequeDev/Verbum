CREATE DATABASE verbum;

USE verbum;

CREATE TABLE Autores (
	idAutor INT PRIMARY KEY AUTO_INCREMENT,
    nomeAutor VARCHAR(100) NOT NULL
);

CREATE TABLE Editoras (
	idEditora INT PRIMARY KEY AUTO_INCREMENT,
    nomeEditora VARCHAR(100) NOT NULL
);

CREATE TABLE Livros (
  idLivro INT PRIMARY KEY AUTO_INCREMENT,
  idAutor INT NOT NULL,
  idEditora INT NOT NULL,
  imagemCapa VARCHAR(255),
  titulo VARCHAR(255) NOT NULL, 
  descricao text not null,
  anoPublicacao INT NOT NULL,
  quantidade INT NOT NULL,
  numero_paginas INT NOT NULL,
  genero VARCHAR(50) NOT NULL,
  FOREIGN KEY (idAutor) REFERENCES Autores(idAutor),
  FOREIGN KEY (idEditora) REFERENCES Editoras(idEditora)
);

CREATE TABLE Usuarios (
  idUsuario INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  serie VARCHAR(50) NOT NULL,
  senha VARCHAR(255) NOT NULL
);

CREATE TABLE Emprestimos (
  idEmprestimo INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  dataEmprestimo DATE NOT NULL,
  dataDevolucao DATE,
  FOREIGN KEY (idLivro) REFERENCES Livros(idLivro),
  FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario)
);

CREATE TABLE ListaEspera (
    idListaEspera INT AUTO_INCREMENT PRIMARY KEY,
    idLivro INT,
    idUsuario INT,
    dataReserva DATETIME,
    status TINYINT default 1,
    FOREIGN KEY (idLivro) REFERENCES Livros(idLivro),
    FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario)
);

DELIMITER //

CREATE TRIGGER atualiza_quantidade
AFTER INSERT ON Emprestimos
FOR EACH ROW 
BEGIN
  UPDATE Livros
  SET quantidade = quantidade - 1 
  WHERE idLivro = NEW.idLivro;
  UPDATE ListaEspera
  SET status = 'reservado'
  WHERE idLivro = NEW.idLivro AND idUsuario = NEW.idUsuario;
END//

CREATE TRIGGER atualizar_quantidade_livros_devolucao
AFTER UPDATE ON Emprestimos
FOR EACH ROW
BEGIN
  IF NEW.dataDevolucao IS NOT NULL AND OLD.dataDevolucao IS NULL THEN
    UPDATE Livros
    SET quantidade = quantidade + 1
    WHERE idLivro = NEW.idLivro;
  END IF;
END//

DELIMITER ;

-- Criação da VIEW para formatar a Lista de Espera
CREATE VIEW ListaEsperaDetalhada AS
SELECT 
    le.idListaEspera,
    le.idLivro,
    l.titulo AS tituloLivro,
    le.idUsuario,
    u.nome AS nomeUsuario,
    DATE_FORMAT(CAST(le.dataReserva AS DATETIME), '%d/%m/%Y %H:%i:%s') AS dataReservaFormatada
FROM ListaEspera le
JOIN Livros l ON le.idLivro = l.idLivro
JOIN Usuarios u ON le.idUsuario = u.idUsuario;
