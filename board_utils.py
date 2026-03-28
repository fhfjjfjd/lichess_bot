import chess
from logger import log

def moves_to_board(moves_str, initial_fen=None, variant="standard"):
    # Nếu initial_fen là "startpos" hoặc None, dùng FEN mặc định
    if not initial_fen or initial_fen == "startpos":
        initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    if variant == "chess960" or (initial_fen != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        board = chess.Board(initial_fen, chess960=True)
    else:
        board = chess.Board(initial_fen)
    
    if moves_str:
        for m in moves_str.split():
            try:
                board.push_uci(m)
            except:
                pass
    return board

def get_phase(board):
    pieces = len(board.piece_map())
    if pieces >= 28:
        return "opening"
    elif pieces >= 14:
        return "middlegame"
    else:
        return "endgame"

def is_capture(board, move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        return board.is_capture(move)
    except:
        return False

def gives_check(board, move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        board.push(move)
        result = board.is_check()
        board.pop()
        return result
    except:
        return False

def is_endgame_draw(board):
    pieces = board.piece_map()
    if len(pieces) <= 3:
        return True
    if board.is_stalemate():
        return True
    if board.is_insufficient_material():
        return True
    if board.can_claim_fifty_moves():
        return True
    if board.can_claim_threefold_repetition():
        return True
    return False

def material_count(board):
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
              chess.ROOK: 5, chess.QUEEN: 9}
    white = sum(values.get(p.piece_type, 0) for p in board.piece_map().values() if p.color == chess.WHITE)
    black = sum(values.get(p.piece_type, 0) for p in board.piece_map().values() if p.color == chess.BLACK)
    return white, black

def board_summary(board, moves_str=""):
    phase = get_phase(board)
    w_mat, b_mat = material_count(board)
    move_count = len(moves_str.split()) if moves_str else 0
    in_check = board.is_check()
    legal = board.legal_moves.count()
    return {
        "phase": phase,
        "white_material": w_mat,
        "black_material": b_mat,
        "move_count": move_count,
        "in_check": in_check,
        "legal_moves": legal,
        "is_game_over": board.is_game_over(),
        "fen": board.fen()
    }

def format_move(board, move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        san = board.san(move)
        tags = []
        if is_capture(board, move_uci):
            tags.append("ăn quân")
        if gives_check(board, move_uci):
            tags.append("chiếu")
        extra = f" ({', '.join(tags)})" if tags else ""
        return f"{move_uci} [{san}]{extra}"
    except:
        return move_uci
