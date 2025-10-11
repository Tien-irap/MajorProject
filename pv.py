# pv
import chess
import chess.svg
import tempfile
import cairosvg
from PIL import Image

# Convert board to SVG and then embed to HTML
def render_board_from_pv_moves(pv_moves):
    board = chess.Board()
    for move in pv_moves:
        try:
            board.push_uci(move)
        except:
            break
    svg = chess.svg.board(board, size=400)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=f.name)
        return Image.open(f.name)