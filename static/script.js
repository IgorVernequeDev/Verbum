function reservarLivro() {
    const botaoReservar = document.getElementById('reservaLivro');
    const idLivro = "{{ livro.idLivro }}";

    if (botaoReservar.textContent === 'RESERVAR') {
        botaoReservar.textContent = 'RESERVADO';
    } else if (botaoReservar.textContent === 'RESERVADO') {
        const confirmacao = confirm('Deseja tirar a reserva desse livro?');
        if (confirmacao) {
            botaoReservar.textContent = 'RESERVAR';
        }
    
        fetch(`/reservar/${idLivro}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Você foi adicionado à lista de espera!');
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            alert('Erro ao reservar o livro: ' + error);
        });
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