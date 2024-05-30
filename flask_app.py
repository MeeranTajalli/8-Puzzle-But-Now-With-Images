from flask import Flask, request, jsonify, send_from_directory
import os
from PIL import Image
import time
from puzzle_solver import Solver, Puzzle, Node

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        image = Image.open(filepath)
        pieces = divide_image(image)
        return jsonify({"pieces": pieces})

def divide_image(image):
    piece_size = min(image.size) // 3  # Ensure the image is a square
    resized_image = image.resize((piece_size * 3, piece_size * 3))
    pieces = []
    for i in range(3):
        for j in range(3):
            box = (j * piece_size, i * piece_size, (j + 1) * piece_size, (i + 1) * piece_size)
            piece = resized_image.crop(box)
            piece_path = f"piece_{i}_{j}.png"
            full_piece_path = os.path.join(UPLOAD_FOLDER, piece_path)
            piece.save(full_piece_path)
            pieces.append(f"/uploads/{piece_path}")
    pieces[-1] = 0  # Set the last piece as the empty tile
    return pieces

@app.route('/shuffle', methods=['POST'])
def shuffle_puzzle():
    data = request.get_json()
    pieces = data['pieces']
    board = [
        [pieces[0], pieces[1], pieces[2]],
        [pieces[3], pieces[4], pieces[5]],
        [pieces[6], pieces[7], pieces[8]]
    ]
    puzzle = Puzzle(board).shuffle()
    shuffled_board = [[piece for piece in row] for row in puzzle.board]
    return jsonify({"shuffled_board": shuffled_board})

@app.route('/solve', methods=['POST'])
def solve_puzzle():
    data = request.get_json()
    board = data['board']
    goal = [f"/uploads/piece_{i}_{j}.png" for i in range(3) for j in range(3)]
    goal[-1] = 0  # Ensure the last piece is the empty tile in the goal state

    print("Board:", board)
    print("Goal:", goal)

    puzzle = Puzzle(board)
    if puzzle.solved:
        return jsonify({"message": "Already in solved state"}), 200

    solver = Solver(puzzle, goal)
    start_time = time.time()
    path = solver.solve()

    if path is None:
        return jsonify({"error": "No solution found"}), 404

    try:
        moves = []
        for node in path:
            if isinstance(node, Node):
                moves.append((node.action, node.puzzle.board))
            else:
                print(f"Unexpected element in path: {node}")
                return jsonify({"error": "Invalid path element"}), 500
    except AttributeError as e:
        print(f"Error processing path elements: {str(e)}")
        return jsonify({"error": "Error processing path elements"}), 500

    return jsonify({
        "moves": moves,
        "timeTaken": time.time() - start_time,
        "steps": len(moves)
    })

if __name__ == "__main__":
    app.run(debug=True)
