CREATE DATABASE verbum;

USE verbum;

-- Tabela Autor
CREATE TABLE Autor (
	idAutor INT PRIMARY KEY AUTO_INCREMENT,
    nomeAutor VARCHAR(100) NOT NULL
);

-- Tabela Editora
CREATE TABLE Editora (
	idEditora INT PRIMARY KEY AUTO_INCREMENT,
    nomeEditora VARCHAR(100) NOT NULL
);

-- Tabela de Livros
CREATE TABLE Livro (
  idLivro INT PRIMARY KEY AUTO_INCREMENT,
  idAutor INT NOT NULL,
  idEditora INT NOT NULL,
  imagemCapa VARCHAR(255),
  titulo VARCHAR(255) NOT NULL, 
  descricao text not null,
  anoPublicacao YEAR NOT NULL,
  quantidade INT NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  FOREIGN KEY (idAutor) REFERENCES Autor(idAutor),
  FOREIGN KEY (idEditora) REFERENCES Editora(idEditora)
);

-- Tabela de Usuários
CREATE TABLE Usuario (
  idUsuario INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  senha VARCHAR(255) NOT NULL
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

-- Tabela de Reservas 
CREATE TABLE Reserva (
  idReserva INT PRIMARY KEY AUTO_INCREMENT,
  idLivro INT NOT NULL,
  idUsuario INT NOT NULL,
  status ENUM('em_espera', 'reservado', 'cancelado') NOT NULL DEFAULT 'em_espera',
  dataReserva DATE NOT NULL,
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
  SET quantidade = quantidade - 1 
  WHERE idLivro = NEW.idLivro;
  update reserva 
  set status = 'reservado', 
  posicaoespera = 0
  where idLivro = new.idLivro and idUsuario = new.idUsuario;
END//

-- Trigger para atualizar a quantidade de livros ao fazer devoluções
CREATE TRIGGER atualizar_quantidade_livros_devolucao
AFTER UPDATE ON Emprestimo
FOR EACH ROW
BEGIN
  IF NEW.dataDevolucao IS NOT NULL AND OLD.dataDevolucao IS NULL THEN
    UPDATE Livro
    SET quantidade = quantidade + 1
    WHERE idLivro = NEW.idLivro;
  END IF;
END//

DELIMITER ;