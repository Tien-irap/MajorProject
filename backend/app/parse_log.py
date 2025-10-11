#parse_log
import re
import chess
import chess.svg

# Parse UCI log lines to get latest PV
def parse_uci_log(log):
    pattern = r"info depth (\d+).*?score (cp|mate) (-?\d+).*?pv (.+)"
    matches = re.findall(pattern, log)

    if matches:
        latest = matches[-1]
        depth = int(latest[0])
        score_type = latest[1]
        score_value = int(latest[2])
        pv_moves = latest[3].split()

        return {
            "depth": depth,
            "score_type": score_type,
            "score_value": score_value,
            "pv_moves": pv_moves
        }
    else:
        return None