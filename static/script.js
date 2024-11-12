function reservarLivro() {
    // Passando o idLivro corretamente para o JavaScript
    const idLivro = {{ livro.idLivro }} ;  // Não precisa de aspas se for um número
    const idUsuario = session['idUsuario'];  // Também assume que idUsuario é numérico

    // Enviar a requisição para a rota de reserva
    fetch(`/reservar/${idLivro}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            idUsuario: idUsuario  // Envia o ID do usuário que está reservando
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Livro reservado com sucesso e adicionado à lista de espera!');
            window.location.href = `/listaespera/${idLivro}`;  // Redireciona para a lista de espera do livro
        } else {
            alert('Erro ao reservar o livro.');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao tentar realizar a reserva.');
    });
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