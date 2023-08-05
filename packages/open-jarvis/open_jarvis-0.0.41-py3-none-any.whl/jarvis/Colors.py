#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#


class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    RESET = '\033[0m'

    BOLD = '\u001b[1m'
    LIGHT = '\u001b[2m'
    UNDERLINED = '\u001b[4m'
    BLINKING = '\u001b[5m'
    # BLINKING = '\u001b[6m' # also works as blinking
    REVERSED = '\u001b[7m'
    INVISIBLE = '\u001b[8m'
    STRIKE_THROUGH = '\u001b[9m'
    DOUBLE_UNDERLINED = '\u001b[21m'

    WARNING = YELLOW
    ERROR = RED

# more at:
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
