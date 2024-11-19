function reservarLivro() {
    const botaoReservar = document.getElementById('reservaLivro');
    const idLivro = "{{ livro.idLivro }}";

    console.log("ID do Livro:", idLivro);

    if (botaoReservar.textContent.trim() === 'RESERVAR') {
        botaoReservar.innerHTML = `<i class="bi bi-book-half me-2 fs-5"></i>RESERVADO`;
    } else if (botaoReservar.textContent.trim() === 'RESERVADO') {
        const confirmacao = confirm('Deseja tirar a reserva desse livro?');
        if (confirmacao) {
            botaoReservar.innerHTML = `<i class="bi bi-book-half me-2 fs-5"></i>RESERVAR`;
        }
    }

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
    const idLivro = element.getAttribute('data-id');
    const confirmacao = confirm('Deseja excluir esse livro?');
    if (confirmacao) {
        const confirmacao2 = confirm('Tem certeza disso? Você irá perder TODO O REGISTRO FEITO PARA ESSE LIVRO!');
        if (confirmacao2) {
            window.location.href = '/excluir/' + idLivro;
        }
    }
}

function entrar() {
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;

    if (email === "" || senha === "") {
        alert('Por favor, preencha todos os campos!');
    }
}

function avaliacao() {
    const texto = document.getElementsByTagName('h3')[0];  // Supondo que há um único h3 a ser atualizado.

    // Alterando o texto com base nas estrelas selecionadas
    if (document.getElementById('1').checked) {
        texto.textContent = '⭐';
    }
    if (document.getElementById('2').checked) {
        texto.textContent = '⭐⭐';
    }
    if (document.getElementById('3').checked) {
        texto.textContent = '⭐⭐⭐';
    }
    if (document.getElementById('4').checked) {
        texto.textContent = '⭐⭐⭐⭐';
    }
    if (document.getElementById('5').checked) {
        texto.textContent = '⭐⭐⭐⭐⭐';
    }
}
