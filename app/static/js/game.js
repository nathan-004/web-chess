
// ---------------------------------------------------------------------------
// Style Functions
// ---------------------------------------------------------------------------

function highlightPossibleMoves(squares) {
    // Enlève les anciens coups possibles
    document.querySelectorAll("." + CSS.square).forEach(square => {
        square.classList.remove(CSS.highlightMove1);
    });

    // Ajoute les nouveaux
    squares.forEach(sq => {
        const squareEl = document.querySelector(`.square-${sq}`);
        if (squareEl) {
            squareEl.classList.add(CSS.highlightMove1);
        }
    });
}

// ---------------------------------------------------------------------------
// Chess Util Functions -> Server
// ---------------------------------------------------------------------------

async function getMoves(source) {
    try {
        const response = await fetch('/get_moves', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data.moves;

    } catch (error) {
        console.error("Erreur lors de la récupération des coups :", error);
    }
}

function onDragStart(source, piece, position, orientation) {
    getMoves(source).then(legalMoves => {
        highlightPossibleMoves(legalMoves);
    });
}

var config = {
    draggable: true,
    position: 'start',
    pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
    onDragStart: onDragStart,
}

const board = Chessboard('board', config);