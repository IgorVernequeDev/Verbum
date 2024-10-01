CREATE DATABASE VERBUM;

USE VERBUM;

-- Tabela Autor
CREATE TABLE Autor (
	idAutor INT PRIMARY KEY AUTO_INCREMENT,
    nomeAutor VARCHAR(255) NOT NULL
);

-- Tabela Editora
CREATE TABLE Editora (
	idEditora INT PRIMARY KEY AUTO_INCREMENT,
    nomeEditora VARCHAR(255) NOT NULL
);

-- Tabela de Livros
CREATE TABLE Livro (
  idLivro INT PRIMARY KEY AUTO_INCREMENT,
  idAutor INT NOT NULL,
  idEditora INT NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  anoPublicacao YEAR NOT NULL,
  quantidade INT NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  status ENUM('disponivel', 'reservado') NOT NULL DEFAULT 'disponivel',
  FOREIGN KEY (idAutor) REFERENCES Autor(idAutor),
  FOREIGN KEY (idEditora) REFERENCES Editora(idEditora)
);

-- Tabela de Usuários
CREATE TABLE Usuario (
  idUsuario INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  nivelUsuario ENUM
);

-- Tabela de Empréstimos
CREATE TABLE Emprestimo (
  idEmprestimo INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  dataEmprestimo DATE NOT NULL,
  dataDevolucao DATE,
  FOREIGN KEY (idLivro) REFERENCES Livro(idLivro),
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
);

-- Tabela de Reservas de Usuários
CREATE TABLE ReservaUsuario (
  idReserva INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  status ENUM('em_espera', 'reservado') NOT NULL DEFAULT 'em_espera',
  dataReserva DATE NOT NULL,
  FOREIGN KEY (idLivro) REFERENCES Livro(idLivro),
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
);

-- Tabela de Lista de Espera
CREATE TABLE ListaEspera (
  idEspera INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  posicaoEspera INT NOT NULL,
  FOREIGN KEY (idLivro) REFERENCES Livro(idLivro),
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
);

-- Trigger para atualizar a quantidade de livros ao fazer empréstimos
DELIMITER //

CREATE TRIGGER atualiza_quantidade
AFTER INSERT ON Emprestimo
FOR EACH ROW 
BEGIN
  UPDATE Livro 
  SET quantidade = quantidade - 1, 
      status = IF(quantidade - 1 = 0, 'reservado', 'disponivel')
  WHERE idLivro = NEW.idLivro;
END//

-- Trigger para atualizar a quantidade de livros ao fazer devoluções
CREATE TRIGGER atualizar_quantidade_livros_devolucao
AFTER UPDATE ON Emprestimo
FOR EACH ROW
BEGIN
  IF NEW.dataDevolucao IS NOT NULL AND OLD.dataDevolucao IS NULL THEN
    UPDATE Livro
    SET quantidade = quantidade + 1,
        status = IF(quantidade + 1 > 0, 'disponivel', status)
    WHERE idLivro = NEW.idLivro;
  END IF;
END//

-- Trigger para gerenciar a lista de espera
CREATE TRIGGER atualiza_lista_espera
AFTER UPDATE ON Emprestimo
FOR EACH ROW
BEGIN
  IF NEW.dataDevolucao IS NOT NULL AND OLD.dataDevolucao IS NULL THEN
    -- Seleciona o próximo usuário na lista de espera
    INSERT INTO ReservaUsuario (idLivro, idUsuario, status, dataReserva)
    SELECT NEW.idLivro, idUsuario, 'reservado', CURDATE()
    FROM ListaEspera 
    WHERE idLivro = NEW.idLivro
    ORDER BY posicaoEspera 
    LIMIT 1;

    -- Remove o usuário da lista de espera após a reserva
    DELETE FROM ListaEspera 
    WHERE idLivro = NEW.idLivro 
    AND idUsuario = (SELECT idUsuario FROM ReservaUsuario 
                     WHERE idLivro = NEW.idLivro 
                     ORDER BY idReserva DESC LIMIT 1);
  END IF;
END//emprestimo


DELIMITER ;

ALTER TABLE Livro ADD imagemCapa LONGBLOB;
