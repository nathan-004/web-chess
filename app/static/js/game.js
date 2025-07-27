
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const moveSound = new Audio("/static/audios/move-self.mp3");
const captureSound = new Audio("/static/audios/capture.mp3");

// ---------------------------------------------------------------------------
// Style Functions
// ---------------------------------------------------------------------------

function highlightPossibleMoves(squares) {
    // Enlève les anciens coups possibles
    document.querySelectorAll("." + CSS.square).forEach(square => {
        square.classList.remove(CSS.highlightMove);
        square.classList.remove(CSS.highlightMovePiece);
    });

    const position = board.position();

    // Ajoute les nouveaux
    squares.forEach(sq => {
        const squareEl = document.querySelector(`.square-${sq}`);
        if (squareEl) {
            if (position.hasOwnProperty(sq)) {
                squareEl.classList.add(CSS.highlightMovePiece);
            }
            else {
                squareEl.classList.add(CSS.highlightMove); // CSS depuis chessboard.js
            }
        }
    });
}

function changeTextById(elementID, text) {
    const element = document.getElementById(elementID);
    element.innerHTML = text;
    console.log(text);
}

function playSound(audio) {
    audio.currentTime = 0;
    audio.play();
}

// ---------------------------------------------------------------------------
// Chess Util Functions -> Server
// ---------------------------------------------------------------------------

// async function startSession() {
//    await fetch('/init_session', {
//            method: 'POST',
//            headers: {
//              'Content-Type': 'application/json'
//            },
//        });
//    console.log("Session initialisée");
// }

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
    return data;
}

async function getCurrentTurn() {
    const response = await fetch('/get_turn', {
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
    return data.turn;
}

// ---------------------------------------------------------------------------
// Events Functions
// ---------------------------------------------------------------------------

function onDragStart(source, piece, position, orientation) {
    if ((orientation === 'white' && piece.search(/^w/) === -1) || (orientation === 'black' && piece.search(/^b/) === -1)) {
        return false
    }
    getMoves(source).then(legalMoves => {
        highlightPossibleMoves(legalMoves);
    });
}

async function onDrop(source, target, piece, newPos, oldPos, orientation) {
    valid = await movePiece(source, target);

    if (!valid) {
        board.position(oldPos);
    }
    else {
        if (target in oldPos) {
            playSound(captureSound);
        }
        else {
            playSound(moveSound);
        }
    }
    const turn = await getCurrentTurn();
    changeTextById("turn", turn);
}

async function onChange (oldPos, newPos) {
    highlightPossibleMoves([]);
    console.log("test");
    const turn = await getCurrentTurn();
            
    changeTextById("turn", turn);
}

// ---------------------------------------------------------------------------
// Config chessboard
// ---------------------------------------------------------------------------

async function initBoard() {
    // await startSession();
    const boardFEN = await getBoard();
    const turn = await getCurrentTurn();
    
    const config = {
        draggable: true,
        position: boardFEN.board,
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onChange: onChange,
        orientation: "white",
    };

    changeTextById("turn", turn);
    if (playerOrientation == "white") {
        changeTextById("currentPlayer", boardFEN.players[0]);
        changeTextById("secondPlayer", boardFEN.players[1]);
    }
    else {
        changeTextById("currentPlayer", boardFEN.players[1]);
        changeTextById("secondPlayer", boardFEN.players[0]);
    }

    return Chessboard('board', config);
}

function main() {
    setInterval(async function () {
        const boardFEN = await getBoard();

        if (boardFEN.board != board.fen()) {
            board.position(boardFEN.board);
        }
        if (boardFEN.board_state != currentStatus) {
            changeTextById("status", boardFEN.board_state);
        }

    }, 500);
}

let currentStatus = "NaN";

initBoard().then(instance => {
    board = instance;
    currentPosition = board.fen();
    if (board.orientation() != playerOrientation) {
        board.flip();
    }
    $(window).on('resize', function () {
        board.resize();
    });
    main();
});