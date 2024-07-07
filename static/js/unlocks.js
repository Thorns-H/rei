function att_unlocks() {
    window.open("https://www.att.com.mx/desbloqueo", "_self");
}
function telcel_unlocks() {
    window.open("https://www.telcel.com/personas/politicas-y-codigos/desbloquear-equipos", "_self");
}
function movistar_unlocks() {
    window.open("https://www.movistar.com.mx/atencion-al-cliente/informacion/codigo-de-liberacion", "_self");
}

let currentUsername = '';
let currentDomain = '';

function generateTempEmail() {
    fetch('/generate_temp_email')
        .then(response => response.json())
        .then(data => {
            currentUsername = data.username;
            currentDomain = data.domain;
            document.getElementById('tempEmail').innerText = data.email_address;
            checkInbox();
        });
}

function checkInbox() {
    if (currentUsername && currentDomain) {
        fetch(`/check_inbox/${currentUsername}/${currentDomain}`)
            .then(response => response.json())
            .then(emails => {
                let inbox = document.getElementById('inbox');
                inbox.innerHTML = '';
                if (emails.length > 0) {
                    emails.forEach(email => {
                        let card = document.createElement('div');
                        card.className = 'card mb-3';
                        card.innerHTML = `
                            <div class="card-body">
                                <h5 class="card-title">${email.subject}</h5>
                                <p class="card-text"><strong>De:</strong> ${email.from}</p>
                                <button class="btn btn-primary" onclick="viewEmailContent(${email.id})">Ver contenido</button>
                            </div>
                        `;
                        inbox.appendChild(card);
                    });
                } else {
                    inbox.innerHTML = '<div class="alert alert-info">No hay correos nuevos.</div>';
                }
                let refreshButton = document.createElement('button');
                refreshButton.className = 'btn btn-primary mt-3';
                refreshButton.innerText = 'Refrescar Bandeja de Entrada';
                refreshButton.onclick = checkInbox;
                inbox.appendChild(refreshButton);
            });
    }
}

function viewEmailContent(mailId) {
    fetch(`/check_inbox/${currentUsername}/${currentDomain}`)
        .then(response => response.json())
        .then(emails => {
            const email = emails.find(e => e.id === mailId);
            if (email) {
                fetch(`/read_email/${currentUsername}/${currentDomain}/${mailId}`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('emailModalTitle').innerText = email.subject;
                        document.getElementById('emailModalBody').innerText = data.textBody || 'No hay contenido disponible.';
                        $('#emailModal').modal('show');
                    });
            }
        });
}
