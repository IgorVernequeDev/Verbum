# Verbum - Reserva de Livros

Sobre o Projeto

O Verbum é um sistema desenvolvido para facilitar a gestão de reservas e empréstimos de livros em bibliotecas escolares. Ele foi criado como parte do meu projeto final no curso técnico, utilizando tecnologias modernas para integrar funcionalidades eficientes e uma interface intuitiva.

Funcionalidades Principais

1. Cadastro e Gestão de Livros

Administradores podem cadastrar, editar e excluir livros no sistema.

Campos cadastrados incluem: título, autor, editora, data de publicação, categoria, número de páginas, descrição e capa do livro.

2. Reserva e Lista de Espera

Usuários podem reservar livros diretamente pelo sistema.

Assim que reservado, o usuário é adicionado à lista de espera automaticamente.

3. Interface Intuitiva e Responsiva

Design adaptado para computadores e dispositivos móveis.

Uso de imagens como botões e layout otimizado para melhor experiência do usuário.

4. Gestão de Reservas

Sistema de controle de reservas, permitindo que os administradores acompanhem o status de cada livro e as posições dos usuários na lista de espera.

Tecnologias Utilizadas

Python: Linguagem principal do back-end.

Flask: Framework para criação de aplicações web.

Jinja: Motor de template para renderização dinâmica de páginas.

MySQL: Banco de dados relacional para armazenamento eficiente das informações.

HTML/CSS/JavaScript: Tecnologias para o desenvolvimento do front-end responsivo.

Estrutura do Banco de Dados

Tabela Livros

idLivro: Identificador único do livro (INT).

titulo: Nome do livro (VARCHAR).

dataPublicacao: Data de publicação do livro (DATE).

quantidade: Quantidade de exemplares disponíveis (INT).

categoria: Categoria do livro (VARCHAR).

numero_paginas: Número de páginas (INT).

descricao: Resumo do livro (TEXT).

status: Status do livro (ENUM: 'disponivel', 'reservado').

Tabela Reservas

idReserva: Identificador da reserva (INT).

idLivro: Relacionamento com o livro reservado (INT).

idUsuario: Identificador do usuário que reservou (INT).

posicao: Posição na lista de espera (INT).

Tabela Usuarios

idUsuario: Identificador do usuário (INT).

nome: Nome completo do usuário (VARCHAR).

email: Endereço de e-mail do usuário (VARCHAR).

Como Executar o Projeto

1. Clone o Repositório

git clone https://github.com/seu-usuario/verbum.git

2. Configure o Banco de Dados

Certifique-se de que o MySQL está instalado e configurado.

Importe o arquivo verbum.sql para criar as tabelas necessárias:

mysql -u seu_usuario -p nome_do_banco < verbum.sql

Atualize as configurações de conexão ao banco de dados no arquivo config.py.

3. Execute o Projeto

Inicie o servidor Flask:

flask run

Acesse o sistema em http://127.0.0.1:5000.

Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

Agradecimentos

Este projeto não seria possível sem o apoio dos professores João Paulo Lepinsk e Rafael Ribas de Lima, além dos meus colegas que colaboraram durante o processo de desenvolvimento.

Desenvolvido por Igor de Almeida Verneque, Luiz Henrique Fernandes Yamasaki, Maria Luisa Marcondes Nunes e Davi Gabriel Carvalho Nunes Silva
