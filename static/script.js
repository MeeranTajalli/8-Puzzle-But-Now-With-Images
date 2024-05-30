const speed = 1000;  // Lower value means faster animation, adjust as needed
let currentPieces = [];
let messageQueue = [];  // Array to store the last three messages

function displayBoard(board) {
    const container = document.getElementById('puzzle-container');
    container.innerHTML = '';  // Clear previous board
    board.forEach(row => {
        row.forEach(cell => {
            const cellDiv = document.createElement('div');
            if (cell !== 0) {
                cellDiv.style.backgroundImage = `url('${cell}')`;
                cellDiv.style.backgroundSize = 'cover';
                cellDiv.style.backgroundPosition = 'center';
            }
            cellDiv.className = cell === 0 ? 'empty' : '';
            container.appendChild(cellDiv);
        });
    });
}

function solvePuzzle() {
    const board = getBoard();
    console.log("Board to solve:", board);  // Debugging statement
    displayBoard(board);

    fetch('/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ board })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('No solution found');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            displayMessage(data.error);
            animateNoSolution(board);
            return;
        }
        if (data.message) {
            displayMessage(data.message);
            return;
        }
        displayMessage('Solution found!');
        displayMessage('Steps: ' + data.steps);
        displayMessage('Time: ' + data.timeTaken.toFixed(2) + ' seconds');
        animateSolution(data.moves);
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('Error solving the puzzle.');
        animateNoSolution(board);
    });
}

function shufflePuzzle() {
    fetch('/shuffle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pieces: currentPieces })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            displayMessage(data.error);
            return;
        }
        const shuffledBoard = data.shuffled_board;
        displayBoard(shuffledBoard);
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('Error shuffling the puzzle.');
    });
}

function uploadImage(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            displayMessage(data.error);
            return;
        }
        currentPieces = data.pieces;
        const board = [
            [currentPieces[0], currentPieces[1], currentPieces[2]],
            [currentPieces[3], currentPieces[4], currentPieces[5]],
            [currentPieces[6], currentPieces[7], currentPieces[8]]
        ];
        displayBoard(board);
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('Error uploading the image.');
    });
}

function animateSolution(moves) {
    moves.forEach((move, index) => {
        setTimeout(() => displayBoard(move[1]), speed * index);  // Adjust speed here
    });
}

function animateNoSolution(state) {
    for (let i = 0; i < 5; i++) {  // Flashes the last state five times
        setTimeout(() => {
            displayBoard(state);  // Show the state
            setTimeout(() => {
                const container = document.getElementById('puzzle-container');
                container.innerHTML = '';  // Clear the board
            }, speed / 2);  // Short display time
        }, speed * 3 * i);  // Adjust speed here
    }
}

function displayMessage(message, callback) {
    const container = document.getElementById('message-container');
    
    // Add the new message to the queue
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.textContent = message;
    messageQueue.push(messageDiv);

    // Keep only the last three messages
    if (messageQueue.length > 3) {
        messageQueue.shift();
    }

    // Clear the container and append the last three messages
    container.innerHTML = '';
    messageQueue.forEach(msgDiv => container.appendChild(msgDiv));

    setTimeout(() => {
        messageDiv.classList.add('fly-right');
        if (callback) {
            setTimeout(() => {
                callback();
            }, 1000);  // Time for the message to complete the animation
        }
    }, 100);  // Delay before starting the animation
}

function getBoard() {
    const container = document.getElementById('puzzle-container');
    const board = [];
    let row = [];
    container.childNodes.forEach((cell, index) => {
        row.push(cell.style.backgroundImage === '' ? 0 : cell.style.backgroundImage.slice(5, -2));
        if ((index + 1) % 3 === 0) {
            board.push(row);
            row = [];
        }
    });
    return board;
}

// Initial display (could be a shuffled board or a static example)
displayBoard([
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
]);

