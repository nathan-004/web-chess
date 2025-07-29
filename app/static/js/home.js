// ---------------------------------------------------------------------------
// Server checks
// ---------------------------------------------------------------------------

async function validUsername(username) {
    try {
        const response = await fetch('/is_valid_username', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "username": username })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Erreur lors de la vérification du nom d'utilisateur :", error);
    }
}


// ---------------------------------------------------------------------------
// Program Start
// ---------------------------------------------------------------------------

const usernameInput = document.getElementById("username");

usernameInput.addEventListener("input", async function (event) {
    const response = await validUsername(event.target.value);

    if (response.valid) {
        document.getElementById("usernameErrorMessage").innerHTML = "";
    }
    else {
        document.getElementById("usernameErrorMessage").innerHTML = response.message;
    }
});