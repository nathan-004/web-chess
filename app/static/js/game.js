
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
            body: JSON.stringify({ source, "id": id, "orientation": playerOrientation })
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

async function movePiece(source, destination) {
    // Déplace la pièce si coups correct et retourne True
    // Sinon retourne False
    try {
        const response = await fetch('/move', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source, destination, "id": id })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data.valid;

    } catch (error) {
        console.error("Erreur lors du coups :", error);
    }
}

async function getBoard() {
    const response = await fetch('/get_current_board', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id  // Assure-toi que la variable `id` existe dans le contexte
        })
    });

    if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
    }

    const data = await response.json();
    return data.board;
}


// ---------------------------------------------------------------------------
// Events Functions
// ---------------------------------------------------------------------------

function onDragStart(source, piece, position, orientation) {
    getMoves(source).then(legalMoves => {
        highlightPossibleMoves(legalMoves);
    });
}

function onDrop(source, target, piece, newPos, oldPos, orientation) {
    movePiece(source, target).then(valid => {
        if (!valid) {
            board.position(oldPos);
        }
    });
}

// ---------------------------------------------------------------------------
// Config chessboard
// ---------------------------------------------------------------------------

async function initBoard() {
    const boardFEN = await getBoard();
    
    const config = {
        draggable: true,
        position: boardFEN,
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        orientation: "white",
    };

    return Chessboard('board', config);
}

function main() {
    setInterval(async function () {
        const boardFEN = await getBoard();
        console.log(boardFEN);
        if (boardFEN != board.fen()) {
            board.position(boardFEN);
        }
    }, 500);
}

initBoard().then(instance => {
    board = instance;
    if (board.orientation() != playerOrientation) {
        board.flip();
    }
    main();
});