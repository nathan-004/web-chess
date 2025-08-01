
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const moveSound = new Audio("/static/audios/move-self.mp3");
const captureSound = new Audio("/static/audios/capture.mp3");
const checkSound = new Audio("/static/audios/move-check.mp3");

const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("messageInput");
const messageList = document.getElementById("messagesList");

// ---------------------------------------------------------------------------
// Utils Functions
// ---------------------------------------------------------------------------

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

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
}

function playSound(audio) {
    audio.currentTime = 0;
    audio.play();
}

function addMessages(messages) {
    // messages : liste de messages
    messages.forEach(msg => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");

        const senderElement = document.createElement("div");
        senderElement.classList.add("message-sender");
        senderElement.textContent = msg.sender;

        const contentElement = document.createElement("div");
        contentElement.classList.add("message-content");
        contentElement.textContent = msg.content;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);
        messageList.appendChild(messageElement);
    });

    messageList.scrollTop = messageList.scrollHeight;
}

async function updateMessages(reset=false) {
    const messages = await getMessages(reset);

    if (reset) {
        messageList.innerHTML = "";
    }

    addMessages(messages);
}

function updateEvaluationBar(eval) {
    const leftDist = Math.abs(eval - 1) / 2;  // pour les blancs
    const rightDist = Math.abs(eval + 1) / 2; // pour les noirs

    const total = leftDist + rightDist;

    const leftFlex = leftDist / total;
    const rightFlex = rightDist / total;

    document.getElementById("whiteBar").style.flex = leftFlex;
    document.getElementById("blackBar").style.flex = rightFlex;
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
            id: id
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
            id: id
        })
    });

    if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
    }

    const data = await response.json();
    return data.turn;
}

// ---------------------------------------------------------------------------
// Messages Functions -> Server
// ---------------------------------------------------------------------------

async function getMessages(reset=false) {
    console.log(reset);
    const response = await fetch('/get_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            reset: reset
        })
    });

    if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
    }

    const data = await response.json();
    return data.messages;
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
    console.log(valid);

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
// Form Listeners
// ---------------------------------------------------------------------------

messageForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const message = messageInput.value;
    if (!message) return;

    const response = await fetch("/send_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, id }),
    });

    messageInput.value = "";
})

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

    updateMessages(true);

    return Chessboard('board', config);
}

function main() {
    let intervalID = setInterval(async function () {
        const boardFEN = await getBoard();

        if (boardFEN.board != board.fen()) {
            board.position(boardFEN.board);
        }
        if (boardFEN.board_state != currentStatus) {
            if (boardFEN.board_state == "check") {
                playSound(checkSound);
            }
            changeTextById("status", boardFEN.board_state);
            currentStatus = boardFEN.board_state;
        }

        const whiteTime = formatTime(boardFEN.white_time);
        const blackTime = formatTime(boardFEN.black_time);
        if (playerOrientation == "white") {
            changeTextById("currentPlayerTime", whiteTime);
            changeTextById("secondPlayerTime", blackTime);
        }
        else {
            changeTextById("currentPlayerTime", blackTime);
            changeTextById("secondPlayerTime", whiteTime);
        }

        updateMessages();
        updateEvaluationBar(boardFEN.evaluation);

        // Vérif fin partie
        if (boardFEN.end) {
            //clearInterval(intervalID);
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