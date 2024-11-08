function reservarLivro() {
    const botaoReservar = document.getElementById('reservaLivro');

    if (botaoReservar.textContent === 'RESERVAR') {
        botaoReservar.innerHTML = `<i class="bi bi-book-half me-2 fs-5"></i>RESERVADO`;
    } else if (botaoReservar.textContent === 'RESERVADO') {
        const confirmacao = confirm('Deseja tirar a reserva desse livro?');
        if (confirmacao) {
            botaoReservar.innerHTML = `<i class="bi bi-book-half me-2 fs-5"></i>RESERVAR`;
        }
    }

    const idLivro = "{{ livro.idLivro }}";

    console.log("ID do Livro:", idLivro);

    fetch('/reservar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idLivro: idLivro })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`Reserva realizada com sucesso! Posição na lista de espera: ${data.posicao}`);
        } else {
            alert(`Erro ao reservar: ${data.message}`);
        }
    })
    .catch(error => console.error('Erro:', error));
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