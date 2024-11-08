function reservarLivro() {
    const botaoReservar = document.getElementById('reservaLivro');

    if (botaoReservar.textContent === 'RESERVAR') {
        botaoReservar.textContent = 'RESERVADO';
    } else if (botaoReservar.textContent === 'RESERVADO') {
        const confirmacao = confirm('Deseja tirar a reserva desse livro?');
        if (confirmacao) {
            botaoReservar.textContent = 'RESERVAR';
        }
    }
}

function confirmarExclusao(element) {
    const idLivro = element.getAttribute('data-id');  // Recupera o idLivro do botão
    const confirmacao = confirm('Deseja excluir esse livro?');
    if (confirmacao) {
        const confirmacao2 = confirm('Tem certeza disso? Você irá perder TODO O REGISTRO FEITO PARA ESSE LIVRO!');
        if (confirmacao2) {
            window.location.href = '/excluir/' + idLivro;
        }
    }
}

function entrar() {
    const email = document.getElementById('email').value
    const senha = document.getElementById('senha').value

    if (email == "" || senha == "") {
        alert('Por favor, preencha todos os campos!')
    }
}

function avaliacao() {
    const estrela1 = document.getElementById('1')
    const estrela2 = document.getElementById('2')
    const estrela3 = document.getElementById('3')
    const estrela4 = document.getElementById('4')
    const estrela5 = document.getElementById('5')

    const texto = document.getElementsByTagName('h3')

    if (estrela1) {
        texto.textContent = '⭐'
    }
    if (estrela2) {
        texto.textContent = '⭐⭐'
    }


}