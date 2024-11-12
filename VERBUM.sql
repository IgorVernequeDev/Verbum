CREATE DATABASE verbum;

USE verbum;

-- Tabela Autorusuario
CREATE TABLE Autores (
	idAutor INT PRIMARY KEY AUTO_INCREMENT,
    nomeAutor VARCHAR(100) NOT NULL
);

-- Tabela Editora
CREATE TABLE Editoras (
	idEditora INT PRIMARY KEY AUTO_INCREMENT,
    nomeEditora VARCHAR(100) NOT NULL
);

-- Tabela de Livros
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

-- Tabela de Usuários
CREATE TABLE Usuarios (
  idUsuario INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  serie VARCHAR(50) NOT NULL,
  senha VARCHAR(255) NOT NULL
);

-- Tabela de Empréstimos
CREATE TABLE Emprestimos (
  idEmprestimo INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  dataEmprestimo DATE NOT NULL,
  dataDevolucao DATE,
  FOREIGN KEY (idLivro) REFERENCES Livros(idLivro),
  FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario)
);

-- Tabela de Reservas 
CREATE TABLE reservas (
    idReserva INT AUTO_INCREMENT PRIMARY KEY,
    idLivro INT,
    idUsuario INT,
    posicaoEspera INT,
    dataReserva DATETIME,
    FOREIGN KEY (idLivro) REFERENCES livros(idLivro),
    FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
);

DELIMITER //

CREATE TRIGGER atualiza_quantidade
AFTER INSERT ON Emprestimos
FOR EACH ROW 
BEGIN
  UPDATE Livro
  SET quantidade = quantidade - 1 
  WHERE idLivro = NEW.idLivro;
  update reserva 
  set status = 'reservado', 
  posicaoespera = 0
  where idLivro = new.idLivro and idUsuario = new.idUsuario;
END//

-- Trigger para atualizar a quantidade de livros ao fazer devoluções
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