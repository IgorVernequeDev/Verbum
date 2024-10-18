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
