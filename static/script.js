function toggleUserMenu() {
    const buttonsUser = document.getElementById('usuarioInterface');
    const buttonsNotifications = document.getElementById('notificacoesInterface');

    // Se o menu do usuário estiver visível, escondê-lo. Caso contrário, mostrá-lo e esconder as notificações.
    if (buttonsUser.style.display === 'block') {
        buttonsUser.style.display = 'none';
    } else {
        buttonsUser.style.display = 'block';
        buttonsNotifications.style.display = 'none'; // Esconde as notificações se elas estiverem visíveis
    }
}

function toggleNotifications() {
    const buttonsNotifications = document.getElementById('notificacoesInterface');
    const buttonsUser = document.getElementById('usuarioInterface');

    // Se as notificações estiverem visíveis, escondê-las. Caso contrário, mostrá-las e esconder o menu do usuário.
    if (buttonsNotifications.style.display === 'block') {
        buttonsNotifications.style.display = 'none';
    } else {
        buttonsNotifications.style.display = 'block';
        buttonsUser.style.display = 'none'; // Esconde o menu do usuário se ele estiver visível
    }
}

// Certifique-se de que o estado inicial de ambas as divs seja escondido
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('usuarioInterface').style.display = 'none';
    document.getElementById('notificacoesInterface').style.display = 'none';
});

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
