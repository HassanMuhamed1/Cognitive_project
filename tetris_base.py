import random, time, pygame, sys, copy, os
from pygame.locals import *

##############################################################################
# SETTING UP GENERAL CONSTANTS
##############################################################################

# Board config
FPS          = 25
WINDOWWIDTH  = 650
WINDOWHEIGHT = 690
BOXSIZE      = 25
BOARDWIDTH   = 10
BOARDHEIGHT  = 25
BLANK        = '.'
XMARGIN      = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN    = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

# Timing config
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ     = 0.1

# Colors
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR     = BLUE
BGCOLOR         = BLACK
TEXTCOLOR       = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS          = (BLUE, GREEN, RED, YELLOW)
LIGHTCOLORS     = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS)

# Piece Templates
TEMPLATEWIDTH  = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

MANUAL_GAME = False # <<<< IMPORTANT: Set to False for GA

##############################################################################
# GENETIC ALGORITHM CONSTANTS AND SETTINGS
##############################################################################
GA_SEED = 42
POPULATION_SIZE = 12 # Min 12 (as requested)
NUM_GENERATIONS = 10 # Min 10 (as requested)
NUM_PLAYS_PER_EVALUATION = 300 # 300-500 for training
FINAL_RUN_PLAYS = 600

NUM_HEURISTIC_WEIGHTS = 5 # lines_cleared, sum_height, holes_created, bumpiness, contact_points
NUM_CHROMOSOME_FACTORS = NUM_HEURISTIC_WEIGHTS + 1 # +1 for lookahead_score_weight

MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.5 # How much a gene can change
TOURNAMENT_SIZE = 3

LOG_FILE = "tetris_ga_log.txt"
OPTIMAL_CHROMOSOME_FILE = "optimal_chromosome.txt"

VISUALIZE_GA_TRAINING = False # True to watch one game per generation (slow!)
VISUALIZE_FINAL_RUN = True    # True to watch the final run

##############################################################################
# CORE GAME LOGIC FUNCTIONS (From your original code)
##############################################################################

def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def terminate():
    pygame.quit()
    sys.exit()

def check_key_press(): # Used by show_text_screen
    check_quit() # Check for QUIT events even when waiting for a key
    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

def show_text_screen(text):
    # This function assumes global DISPLAYSURF, BIGFONT, BASICFONT, FPSCLOCK are initialized
    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key..." text.
    # Modified to only show "Press a key to continue" for specific screens
    if MANUAL_GAME or (not MANUAL_GAME and VISUALIZE_FINAL_RUN and "Score" in text):
        press_key_surf, press_key_rect = make_text_objs('Press a key to continue.', BASICFONT, TEXTCOLOR)
        press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
        DISPLAYSURF.blit(press_key_surf, press_key_rect)
        
        # Wait for a key press, but keep pygame responsive
        while check_key_press() is None:
            pygame.display.update()
            if FPSCLOCK: # Ensure FPSCLOCK is initialized
                 FPSCLOCK.tick()
    else: # If not showing "press key", just update display once for GA status messages etc.
        pygame.display.update()
        # time.sleep(0.1) # Optional short pause if needed, but can slow down GA display

def check_quit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) # Important to put other KEYUP events back

def calc_level_and_fall_freq(score, is_ga_simulation=False):
    level = int(score / 400) + 1 # Original scoring had 400 points per level
    fall_freq = 0.27 - (level * 0.02)

    # For GA, make pieces fall instantly unless visualizing
    if is_ga_simulation or (not MANUAL_GAME and not VISUALIZE_GA_TRAINING and not VISUALIZE_FINAL_RUN):
        fall_freq = 0.00
    elif not MANUAL_GAME and (VISUALIZE_GA_TRAINING or VISUALIZE_FINAL_RUN):
        fall_freq = 0.1 # Slower for visualization
    return level, fall_freq

def get_new_piece():
    shape = random.choice(list(PIECES.keys()))
    new_piece = {'shape': shape,
                 'rotation': random.randint(0, len(PIECES[shape]) - 1),
                 'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                 'y': -2, # Start it above the board
                 'color': random.randint(0, len(COLORS)-1)}
    return new_piece

def add_to_board(board, piece):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']

def get_blank_board():
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board

def is_on_board(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT

def is_valid_position(board, piece, adj_X=0, adj_Y=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece['y'] + adj_Y < 0
            if is_above_board or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not is_on_board(x + piece['x'] + adj_X, y + piece['y'] + adj_Y):
                return False
            if board[x + piece['x'] + adj_X][y + piece['y'] + adj_Y] != BLANK:
                return False
    return True

def is_complete_line(board, y):
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True

def remove_complete_lines(board):
    num_removed_lines = 0
    y = BOARDHEIGHT - 1
    while y >= 0:
        if is_complete_line(board, y):
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            num_removed_lines += 1
        else:
            y -= 1
    return num_removed_lines

def conv_to_pixels_coords(boxx, boxy):
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    if color == BLANK:
        return
    # DISPLAYSURF_to_use = DISPLAYSURF_SIM if (not MANUAL_GAME and (VISUALIZE_GA_TRAINING or VISUALIZE_FINAL_RUN) and DISPLAYSURF_SIM) else DISPLAYSURF
    # The above logic for DISPLAYSURF_to_use is tricky because draw_box is called by many functions.
    # It's simpler to ensure the correct DISPLAYSURF is active when calling the top-level draw functions.

    if pixelx is None and pixely is None:
        pixelx, pixely = conv_to_pixels_coords(boxx, boxy)
    
    active_display_surface = pygame.display.get_surface() # Get current active display
    if active_display_surface is None: return # Should not happen if pygame.init and set_mode were called

    pygame.draw.rect(active_display_surface, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(active_display_surface, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board): # Assumes DISPLAYSURF is set correctly before call
    active_display_surface = pygame.display.get_surface()
    pygame.draw.rect(active_display_surface, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)
    pygame.draw.rect(active_display_surface, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])

def draw_status(score, level): # Assumes DISPLAYSURF is set correctly
    active_display_surface = pygame.display.get_surface()
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 80)
    active_display_surface.blit(score_surf, score_rect)

    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 110)
    active_display_surface.blit(levelSurf, levelRect)

def draw_piece(piece, pixelx=None, pixely=None): # Assumes DISPLAYSURF is set correctly
    shape_to_draw = PIECES[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        pixelx, pixely = conv_to_pixels_coords(piece['x'], piece['y'])

    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))

def draw_next_piece(piece): # Assumes DISPLAYSURF is set correctly
    active_display_surface = pygame.display.get_surface()
    next_surf = BASICFONT.render('Next:', True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 150, 160)
    active_display_surface.blit(next_surf, next_rect)
    draw_piece(piece, pixelx=WINDOWWIDTH-150, pixely=160 + 20) # Adjusted y for spacing

##############################################################################
# GAME STATISTICS FUNCTIONS (From your original code - CRITICAL FOR GA)
##############################################################################

def calc_move_info(board, piece, x_piece_template_ref, r_idx, total_holes_bef, total_blocking_bloks_bef): # Renamed x to x_piece_template_ref
    """Calculate informations based on the current play.
    piece is a copy and will be modified (y position).
    x_piece_template_ref is the column for the piece's template origin (top-left of 5x5).
    r_idx is the rotation index.
    Returns: [isValid, sum_heights_after_drop, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]
    """
    # piece_sim = copy.deepcopy(piece) # The calling function rate_potential_move already sends a copy
    piece['rotation'] = r_idx
    piece['y'] = 0 # Start at top to simulate drop
    piece['x'] = x_piece_template_ref # x is the top-left of the template

    if not is_valid_position(board, piece): # Check if it's valid at the spawn point with new rotation/x
        return [False, 0, 0, 0, 0, 0, 0, 0] # Added more return values for consistency

    # Drop the piece
    while is_valid_position(board, piece, adj_Y=1):
        piece['y'] += 1

    # Create a hypothetical board
    new_board = get_blank_board()
    for x_b in range(BOARDWIDTH):
        for y_b in range(BOARDHEIGHT):
            new_board[x_b][y_b] = board[x_b][y_b] # Deep copy original board
    
    add_to_board(new_board, piece) # Add the piece in its final dropped position

    # Calculate removed lines on this new_board
    num_removed_lines = 0 # This will be calculated based on new_board *after* lines are removed
    
    # Store copy of new_board before removing lines to calculate features on it
    board_before_lines_removed = get_blank_board()
    for x_b in range(BOARDWIDTH):
        for y_b in range(BOARDHEIGHT):
            board_before_lines_removed[x_b][y_b] = new_board[x_b][y_b]
    
    num_removed_lines = remove_complete_lines(new_board) # new_board is modified here

    # Calculate features on the board *before* lines were removed, but *after* piece was added
    current_features = calculate_board_features(board_before_lines_removed)
    sum_heights_after_drop = current_features['sum_height'] # Using the new helper for consistency

    # Calculate holes and blocking blocks on the board *after* lines are removed
    total_blocking_blocks_after = 0
    total_holes_after = 0
    for x2 in range(0, BOARDWIDTH):
        # calc_heuristics is (total_holes_in_col, blocks_above_holes_in_col, sum_height_of_col)
        col_holes, col_blocking, _ = calc_heuristics(new_board, x2) # Use new_board (after line removal)
        total_holes_after += col_holes
        total_blocking_blocks_after += col_blocking

    newly_created_holes = total_holes_after - total_holes_bef
    # The definition of new_blocking_blocks might need refinement,
    # for now, it's the change in total blocking blocks.
    new_blocking_blocks = total_blocking_blocks_after - total_blocking_bloks_bef


    # Calculate the sides in contact using the original board (before piece was added)
    # and the piece in its final dropped position.
    piece_sides, floor_sides, wall_sides = calc_sides_in_contact(board, piece)


    return [True, sum_heights_after_drop, num_removed_lines, newly_created_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]

def calc_initial_move_info(board): # This was in your original code, may not be used by GA directly yet
    total_holes = 0
    total_blocking_bocks = 0
    for x2 in range(0, BOARDWIDTH):
        b = calc_heuristics(board, x2)
        total_holes += b[0]
        total_blocking_bocks += b[1]
    return total_holes, total_blocking_bocks

def calc_heuristics(board, x_col): # x_col is the specific column to analyze
    """Calculate heuristics for a single column x_col.
    Returns: (total_holes_in_col, blocks_above_holes_in_col, sum_height_of_col)
    """
    total_holes_in_col = 0
    local_holes_count = 0 # Renamed from locals_holes to avoid keyword clash if it were a local var
    blocks_above_holes_in_col = 0
    # is_hole_exist = False # Not used in the logic that follows
    height_of_col = 0 # sum_heights was misnamed, it's just height of this col

    for y in range(BOARDHEIGHT - 1, -1, -1): # Iterate from bottom up
        if board[x_col][y] == BLANK:
            local_holes_count += 1
        else: # Found a block
            height_of_col += (BOARDHEIGHT - y) # Add to height contribution
            if local_holes_count > 0: # If we just passed some holes
                total_holes_in_col += local_holes_count
                local_holes_count = 0 # Reset for next potential patch of holes
            
            # If there are any holes *below* this current block (meaning total_holes_in_col is > 0)
            # then this block is considered "above a hole".
            if total_holes_in_col > 0:
                blocks_above_holes_in_col += 1
                
    # If loop finishes and local_holes_count > 0, it means column is empty or has holes at the very top.
    # These are not typically counted as "holes" in Tetris heuristics unless they are *under* something.
    # However, your original logic would count them if local_holes_count was > 0 at the end and then a block was found.
    # The current loop structure correctly counts holes only when a block is found *above* them.

    return total_holes_in_col, blocks_above_holes_in_col, height_of_col

def calc_sides_in_contact(board, piece): # piece is already in its final resting place on 'board' (hypothetically)
    """Calculate sides in contact for the given piece at its current x,y,rotation
       against existing blocks on the 'board'.
    """
    piece_sides = 0 # Contacts with other pieces
    floor_sides = 0 # Contacts with the board floor
    wall_sides = 0  # Contacts with board walls

    shape_matrix = PIECES[piece['shape']][piece['rotation']]

    for p_x_template in range(TEMPLATEWIDTH):
        for p_y_template in range(TEMPLATEHEIGHT):
            if shape_matrix[p_y_template][p_x_template] != BLANK: # This is a block of the current piece
                # Board coordinates of this block of the piece
                b_x = piece['x'] + p_x_template
                b_y = piece['y'] + p_y_template

                # Check for wall contact
                if b_x == 0: # Left wall
                    wall_sides += 1
                if b_x == BOARDWIDTH - 1: # Right wall
                    wall_sides += 1
                
                # Check for floor contact
                if b_y == BOARDHEIGHT - 1:
                    floor_sides += 1
                
                # Check contact with other pieces (adjacently on the main board)
                # Check below
                if b_y + 1 < BOARDHEIGHT:
                    if board[b_x][b_y + 1] != BLANK:
                        piece_sides += 1
                # else: it's on the floor, already counted by floor_sides

                # Check left
                if b_x - 1 >= 0:
                    if board[b_x - 1][b_y] != BLANK:
                        piece_sides += 1
                # else: it's on the wall, already counted by wall_sides

                # Check right
                if b_x + 1 < BOARDWIDTH:
                    if board[b_x + 1][b_y] != BLANK:
                        piece_sides += 1
                # else: it's on the wall, already counted by wall_sides

                # Check above (less common for Tetris heuristics, but for completeness)
                # if b_y - 1 >= 0:
                #     if board[b_x][b_y - 1] != BLANK:
                #         piece_sides += 1
    return piece_sides, floor_sides, wall_sides


##############################################################################
# HEURISTIC CALCULATION HELPERS FOR GA (New for GA)
##############################################################################

def get_column_heights(board):
    heights = [0] * BOARDWIDTH
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT): # Scan from top down
            if board[x][y] != BLANK:
                heights[x] = BOARDHEIGHT - y
                break # Found highest block in this column
    return heights

def calculate_board_features(board_state):
    heights = get_column_heights(board_state)
    sum_height = sum(heights)
    
    bumpiness = 0
    for i in range(BOARDWIDTH - 1):
        bumpiness += abs(heights[i] - heights[i+1])
        
    total_holes_on_board = 0
    # Your calc_heuristics returns (total_holes_in_col, blocks_above_holes_in_col, sum_height_of_col)
    for x_col in range(BOARDWIDTH):
        col_holes, _, _ = calc_heuristics(board_state, x_col)
        total_holes_on_board += col_holes
            
    return {
        'sum_height': sum_height,
        'bumpiness': bumpiness,
        'total_holes': total_holes_on_board
    }

##############################################################################
# GA CORE: RATING FUNCTION FOR A SINGLE MOVE
##############################################################################

def rate_potential_move(board, current_piece_orig, next_piece_orig, column_to_try, chromosome_factors):
    best_rating_for_col = -float('inf')
    best_rotation_idx_for_col = 0

    w_lines_cleared, w_sum_height, w_holes_created, w_bumpiness, w_contact_points, w_lookahead_score = chromosome_factors

    current_piece_template_rotations = PIECES[current_piece_orig['shape']]

    # Holes on board BEFORE this current piece might be placed
    initial_board_features = calculate_board_features(board)
    initial_total_holes_on_board = initial_board_features['total_holes']
    # initial_total_blocking_blocks = sum(calc_heuristics(board, x)[1] for x in range(BOARDWIDTH)) # If needed

    for r_idx in range(len(current_piece_template_rotations)):
        current_piece_sim = copy.deepcopy(current_piece_orig) # Simulate with a copy

        # Call calc_move_info
        # It needs: board, piece_to_drop (it will modify y), x_pos_for_template, rotation_idx, total_holes_before, total_blocking_blocks_before
        move_stats = calc_move_info(board, current_piece_sim, column_to_try, r_idx, 
                                    initial_total_holes_on_board, 0) # Assuming 0 for initial blocking blocks for now

        if not move_stats[0]: # isValid was False
            total_rating_for_this_rotation = -float('inf')
        else:
            # Unpack move_stats:
            # [True, sum_heights_after_drop, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]
            sum_height_after_current_drop = move_stats[1] # This is sum_height *after drop, before line clear*
            lines_cleared_by_current = move_stats[2]
            newly_created_holes_by_current = move_stats[3] # This is new holes *after line clear*
            # new_blocking_blocks_by_current = move_stats[4] # Not used in current heuristic set directly
            contact_points_current = move_stats[5] + move_stats[6] # piece_sides + floor_sides

            # Board state *after* current piece is placed AND lines are cleared (for bumpiness and future lookahead)
            temp_board_after_current_land_and_clear = get_blank_board()
            for x_b in range(BOARDWIDTH): # Deep copy original board
                for y_b in range(BOARDHEIGHT):
                    temp_board_after_current_land_and_clear[x_b][y_b] = board[x_b][y_b]
            # current_piece_sim now has its final y from calc_move_info
            add_to_board(temp_board_after_current_land_and_clear, current_piece_sim) 
            remove_complete_lines(temp_board_after_current_land_and_clear) # Clear lines for accurate next state

            features_after_current_move_and_clear = calculate_board_features(temp_board_after_current_land_and_clear)
            # sum_height_after_current should ideally be after line clear.
            # calc_move_info returns sum_heights *before* line clear.
            # Let's use the features from the board *after* line clear for sum_height and bumpiness for consistency.
            sum_height_final_current = features_after_current_move_and_clear['sum_height']
            bumpiness_after_current = features_after_current_move_and_clear['bumpiness']
            # `newly_created_holes_by_current` from calc_move_info should be based on board after line clear, which is good.

            rating_current_placement = (
                lines_cleared_by_current * w_lines_cleared +
                sum_height_final_current * w_sum_height + # Use height after line clear
                newly_created_holes_by_current * w_holes_created +
                bumpiness_after_current * w_bumpiness +   # Use bumpiness after line clear
                contact_points_current * w_contact_points
            )

            # --- Lookahead for NEXT piece ---
            best_rating_for_next_piece = -float('inf')
            if next_piece_orig:
                # Board state for next piece is `temp_board_after_current_land_and_clear`
                holes_before_next_piece = features_after_current_move_and_clear['total_holes']
                # blocking_blocks_before_next_piece = sum(calc_heuristics(temp_board_after_current_land_and_clear, x)[1] for x in range(BOARDWIDTH))


                next_piece_template_rotations_lookahead = PIECES[next_piece_orig['shape']]
                for next_col_lookahead in range(BOARDWIDTH):
                    for next_r_idx_lookahead in range(len(next_piece_template_rotations_lookahead)):
                        next_piece_sim = copy.deepcopy(next_piece_orig)
                        
                        next_move_stats = calc_move_info(
                            temp_board_after_current_land_and_clear, # Board after current piece landed & cleared
                            next_piece_sim,
                            next_col_lookahead, next_r_idx_lookahead,
                            holes_before_next_piece, 0 # Initial blocking blocks for this sub-sim
                        )

                        if not next_move_stats[0]: # Invalid move for next piece
                            rating_this_next_placement = -float('inf')
                        else:
                            # [True, sum_heights_after_drop, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]
                            lines_cleared_by_next = next_move_stats[2]
                            newly_created_holes_by_next = next_move_stats[3]
                            contact_points_next = next_move_stats[5] + next_move_stats[6]

                            # Board after next piece lands and lines clear (for sum_height, bumpiness)
                            temp_board_after_next_land_and_clear = get_blank_board()
                            for x_b in range(BOARDWIDTH):
                                for y_b in range(BOARDHEIGHT):
                                    temp_board_after_next_land_and_clear[x_b][y_b] = temp_board_after_current_land_and_clear[x_b][y_b]
                            add_to_board(temp_board_after_next_land_and_clear, next_piece_sim)
                            remove_complete_lines(temp_board_after_next_land_and_clear)
                            
                            features_after_next_move_and_clear = calculate_board_features(temp_board_after_next_land_and_clear)
                            sum_height_final_next = features_after_next_move_and_clear['sum_height']
                            bumpiness_after_next = features_after_next_move_and_clear['bumpiness']

                            rating_this_next_placement = (
                                lines_cleared_by_next * w_lines_cleared +
                                sum_height_final_next * w_sum_height +
                                newly_created_holes_by_next * w_holes_created +
                                bumpiness_after_next * w_bumpiness +
                                contact_points_next * w_contact_points
                            )
                        
                        if rating_this_next_placement > best_rating_for_next_piece:
                            best_rating_for_next_piece = rating_this_next_placement
            
            if best_rating_for_next_piece == -float('inf'):
                best_rating_for_next_piece = 0 
            
            total_rating_for_this_rotation = rating_current_placement + (best_rating_for_next_piece * w_lookahead_score)

        if total_rating_for_this_rotation > best_rating_for_col:
            best_rating_for_col = total_rating_for_this_rotation
            best_rotation_idx_for_col = r_idx
            
    return best_rotation_idx_for_col, best_rating_for_col

##############################################################################
# GA FITNESS FUNCTION: SIMULATE A FULL GAME
##############################################################################
# Global Pygame variables for GA simulation display (if enabled)
FPSCLOCK_SIM, DISPLAYSURF_SIM, BASICFONT_SIM, BIGFONT_SIM = None, None, None, None

def simulate_game_for_fitness(chromosome, num_plays, game_seed, visualize=False):
    global FPSCLOCK_SIM, DISPLAYSURF_SIM, BASICFONT_SIM, BIGFONT_SIM # For visualization
    
    random.seed(game_seed) # Consistent piece sequence for this chromosome's evaluation
    
    if visualize:
        if not pygame.get_init(): pygame.init() # Ensure Pygame is initialized
        FPSCLOCK_SIM = pygame.time.Clock()
        DISPLAYSURF_SIM = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        # Ensure fonts are loaded if not already by main() for GA context
        try:
            BASICFONT_SIM = pygame.font.Font('freesansbold.ttf', 18)
            BIGFONT_SIM = pygame.font.Font('freesansbold.ttf', 100)
        except pygame.error as e:
            print(f"Error loading font in simulate_game_for_fitness: {e}")
            print("Make sure 'freesansbold.ttf' is in the same directory as the script.")
            terminate() # Cannot proceed without font for status
        pygame.display.set_caption('Tetris GA - Evaluation')
    
    board = get_blank_board()
    score = 0
    level = 1 # Fall frequency not directly used by AI, but for display
    
    falling_piece = get_new_piece()
    next_piece = get_new_piece()

    for play_count in range(num_plays):
        if falling_piece is None: # Previous piece led to new piece generation
            falling_piece = next_piece
            next_piece = get_new_piece()
            if not is_valid_position(board, falling_piece): # Game Over - cannot place new piece
                if visualize and DISPLAYSURF_SIM: pygame.display.quit() # Clean up this specific display
                return score 

        # AI's turn
        best_col_overall = -1
        best_rot_overall = 0 
        highest_rating_overall = -float('inf')

        possible_initial_placements = [] # Store (col, rot, rating)
        for col_try in range(BOARDWIDTH): 
            # Check if placing the piece (at any rotation) at this col_try is even possible
            # without immediate collision or going off board. This is a pre-filter.
            temp_piece = copy.deepcopy(falling_piece)
            temp_piece['x'] = col_try
            temp_piece['y'] = 0 # Check from top

            # Check if any rotation is valid at this column for initial placement
            can_place_at_col = False
            for r_test in range(len(PIECES[temp_piece['shape']])):
                temp_piece['rotation'] = r_test
                if is_valid_position(board, temp_piece):
                    can_place_at_col = True
                    break
            
            if not can_place_at_col:
                continue # Skip this column entirely if no rotation can even fit initially

            # If potentially placeable, rate it
            rot_for_col, rating_for_col = rate_potential_move(
                board, falling_piece, next_piece, col_try, chromosome
            )
            
            # Only consider moves that are actually valid (rating > -inf)
            if rating_for_col > -float('inf'):
                 possible_initial_placements.append({'col': col_try, 'rot': rot_for_col, 'rating': rating_for_col})

        if not possible_initial_placements: # No valid move found by the AI
            if visualize and DISPLAYSURF_SIM: pygame.display.quit()
            return score # Game Over

        # Choose the best from valid possibilities
        best_move = max(possible_initial_placements, key=lambda m: m['rating'])
        best_col_overall = best_move['col']
        best_rot_overall = best_move['rot']

        # Apply the chosen move
        falling_piece['rotation'] = best_rot_overall
        falling_piece['x'] = best_col_overall
        falling_piece['y'] = 0 # Start at top to drop it

        # This check should ideally be redundant if rate_potential_move works correctly
        if not is_valid_position(board, falling_piece):
            if visualize and DISPLAYSURF_SIM: pygame.display.quit()
            return score # Game Over if chosen spawn is invalid

        # Drop the piece fully
        while is_valid_position(board, falling_piece, adj_Y=1):
            falling_piece['y'] += 1
        
        add_to_board(board, falling_piece)
        num_removed_lines = remove_complete_lines(board)

        if num_removed_lines == 1: score += 40
        elif num_removed_lines == 2: score += 120
        elif num_removed_lines == 3: score += 300
        elif num_removed_lines == 4: score += 1200
        
        level, _ = calc_level_and_fall_freq(score, is_ga_simulation=not visualize)
        falling_piece = None # Signal to get the next piece in the next iteration

        if visualize and DISPLAYSURF_SIM:
            DISPLAYSURF_SIM.fill(BGCOLOR)
            # Use the global BASICFONT for draw_status, draw_next_piece when called from here
            # These draw functions will use pygame.display.get_surface() which is DISPLAYSURF_SIM
            draw_board(board) 
            draw_status(score, level) 
            if next_piece:
                draw_next_piece(next_piece)
            
            pygame.display.update()
            FPSCLOCK_SIM.tick(10) # Slowed down for visualization
            for event in pygame.event.get(QUIT): terminate()
            for event in pygame.event.get(KEYUP):
                if event.key == K_ESCAPE: terminate()

    if visualize and DISPLAYSURF_SIM: pygame.display.quit() # Quit the simulation display
    return score

##############################################################################
# GENETIC ALGORITHM OPERATORS
##############################################################################

def initialize_population(pop_size, num_factors):
    population = []
    for _ in range(pop_size):
        chromosome = [random.uniform(-2.0, 2.0) for _ in range(num_factors)]
        population.append(chromosome)
    return population

def selection(population, fitness_scores, tournament_size):
    selected_parents = []
    pop_with_fitness = list(zip(population, fitness_scores))

    for _ in range(len(population)):
        tournament = random.sample(pop_with_fitness, tournament_size)
        # Winner is the one with highest fitness score
        winner_chromo, _ = max(tournament, key=lambda x: x[1])
        selected_parents.append(copy.deepcopy(winner_chromo)) # Store a copy
    return selected_parents


def crossover(parent1, parent2):
    if len(parent1) != len(parent2) or len(parent1) < 2:
        return copy.deepcopy(parent1), copy.deepcopy(parent2) # No crossover if too short or different lengths
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(chromosome, mutation_rate, mutation_strength):
    mutated_chromosome = list(chromosome)
    for i in range(len(mutated_chromosome)):
        if random.random() < mutation_rate:
            mutation = random.uniform(-mutation_strength, mutation_strength)
            mutated_chromosome[i] += mutation
    return mutated_chromosome

##############################################################################
# MAIN GA LOOP
##############################################################################

def run_genetic_algorithm():
    global BASICFONT, BIGFONT # Ensure these are loaded for GA logging/display if needed
    # These should be initialized by main() before run_genetic_algorithm is called.

    random.seed(GA_SEED) # Seed for GA's own randomness (selection, mutation)
    
    population = initialize_population(POPULATION_SIZE, NUM_CHROMOSOME_FACTORS)
    best_overall_chromosome = None
    best_overall_fitness = -float('inf')

    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    log_entry(f"Starting GA: Seed={GA_SEED}, Pop_Size={POPULATION_SIZE}, Generations={NUM_GENERATIONS}, Plays_per_Eval={NUM_PLAYS_PER_EVALUATION}")
    log_entry(f"Chromosome factor order: lines_cleared, sum_height, holes_created, bumpiness, contact_points, lookahead_score_weight\n")

    for gen in range(NUM_GENERATIONS):
        fitness_scores = []
        print(f"\nGeneration {gen + 1}/{NUM_GENERATIONS}")

        current_gen_best_fitness = -float('inf')
        current_gen_best_chromosome = None

        for i, chromo in enumerate(population):
            print(f" Evaluating chromosome {i+1}/{POPULATION_SIZE}...", end="")
            # game_seed for simulate_game_for_fitness ensures piece consistency across evaluations
            # If VISUALIZE_GA_TRAINING, only visualize the first chromosome of the generation
            visualize_this_eval = VISUALIZE_GA_TRAINING and (i == 0) 
            
            fitness = simulate_game_for_fitness(chromo, NUM_PLAYS_PER_EVALUATION, GA_SEED, visualize=visualize_this_eval)
            fitness_scores.append(fitness)
            print(f" Fitness: {fitness}, Chromosome: {[f'{x:.3f}' for x in chromo]}")

            if fitness > current_gen_best_fitness:
                current_gen_best_fitness = fitness
                current_gen_best_chromosome = copy.deepcopy(chromo)

            if fitness > best_overall_fitness:
                best_overall_fitness = fitness
                best_overall_chromosome = copy.deepcopy(chromo)

        avg_fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0
        
        log_entry(f"Generation {gen + 1}: Avg Fitness={avg_fitness:.2f}, Max Fitness This Gen={current_gen_best_fitness}, "
                  f"Best Chromo This Gen: {[f'{x:.3f}' for x in (current_gen_best_chromosome or [])]}")
        log_entry(f"Best Overall Fitness so far: {best_overall_fitness}, Chromo: {[f'{x:.3f}' for x in (best_overall_chromosome or [])]}\n")

        print(f"Generation {gen + 1} Summary: Avg Fitness: {avg_fitness:.2f}, Max Fitness: {current_gen_best_fitness}")
        print(f"Best chromosome this generation: {[f'{x:.3f}' for x in (current_gen_best_chromosome or [])]}")
        print(f"Best overall chromosome so far: {[f'{x:.3f}' for x in (best_overall_chromosome or [])]} (Fitness: {best_overall_fitness})")

        parents = selection(population, fitness_scores, TOURNAMENT_SIZE)
        
        next_population = []
        # Elitism: Carry over the best chromosome from this generation directly
        if current_gen_best_chromosome:
            next_population.append(copy.deepcopy(current_gen_best_chromosome))

        # Fill the rest of the population with offspring
        while len(next_population) < POPULATION_SIZE:
            p1_idx = random.randrange(len(parents))
            p2_idx = random.randrange(len(parents))
            parent1 = parents[p1_idx]
            parent2 = parents[p2_idx]
            
            child1, child2 = crossover(parent1, parent2)
            
            next_population.append(mutate(child1, MUTATION_RATE, MUTATION_STRENGTH))
            if len(next_population) < POPULATION_SIZE:
                next_population.append(mutate(child2, MUTATION_RATE, MUTATION_STRENGTH))
        
        population = next_population[:POPULATION_SIZE]

    log_entry(f"\nGA Finished. Best Overall Chromosome: {[f'{x:.3f}' for x in (best_overall_chromosome or [])]} "
              f"with Fitness: {best_overall_fitness}")
    print(f"\nGA Finished. Best Overall Chromosome: {[f'{x:.3f}' for x in (best_overall_chromosome or [])]} "
          f"with Fitness: {best_overall_fitness}")

    if best_overall_chromosome:
        with open(OPTIMAL_CHROMOSOME_FILE, 'w') as f:
            f.write(','.join(map(str, best_overall_chromosome)))
        print(f"Optimal chromosome saved to {OPTIMAL_CHROMOSOME_FILE}")
    else:
        print("No optimal chromosome found (all evaluations might have failed).")


    return best_overall_chromosome

def log_entry(message):
    with open(LOG_FILE, 'a') as f:
        f.write(message + "\n")

##############################################################################
# MAIN GAME EXECUTION CONTROL
##############################################################################
# Global Pygame variables for main game display (manual or final GA run)
FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT = None, None, None, None

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT # For manual game or final GA visualized run
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    try:
        BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
        BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    except pygame.error as e:
        print(f"Error loading font in main: {e}")
        print("Make sure 'freesansbold.ttf' is in the same directory as the script.")
        terminate()
    pygame.display.set_caption('Tetris')

    if MANUAL_GAME:
        pygame.display.set_caption('Tetris - Manual Play')
        show_text_screen('Tetris')
        run_manual_game()
    else:
        pygame.display.set_caption('Tetris - GA Training')
        print("Starting Genetic Algorithm Training...")
        # Potentially show a "Training in progress..." message on screen if desired, but GA loop is blocking.
        # For now, console output is primary feedback during training.
        
        optimal_chromosome = run_genetic_algorithm()
        
        if optimal_chromosome:
            print("\n--- Running Final Test with Optimal Chromosome ---")
            pygame.display.set_caption('Tetris - GA Final Run')
            
            # For the final run, main display (DISPLAYSURF) will be used by simulate_game_for_fitness
            # if VISUALIZE_FINAL_RUN is true. simulate_game_for_fitness re-inits its own _SIM display vars
            # if visualize=True. This is a bit redundant.
            # Let's adjust: simulate_game_for_fitness should use the main DISPLAYSURF if visualizing the final run.

            final_score = simulate_game_for_fitness(optimal_chromosome, FINAL_RUN_PLAYS, GA_SEED, visualize=VISUALIZE_FINAL_RUN)

            log_entry(f"\nFinal Run ({FINAL_RUN_PLAYS} plays) with Optimal Chromosome {[f'{x:.3f}' for x in optimal_chromosome]}: Score = {final_score}")
            print(f"Final Score with Optimal Chromosome ({FINAL_RUN_PLAYS} plays): {final_score}")
            
            if VISUALIZE_FINAL_RUN:
                # Ensure the main display is active again if simulate_game_for_fitness used its own
               if not pygame.display.get_init(): # Check if the display module itself was quit
                    pygame.display.init()
                    # Re-initialize basic font if display was re-initialized
                    try:
                        BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
                        BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
                    except pygame.error as e:
                        print(f"Error re-loading font after GA final run: {e}")
                        terminate()
                    # Explicitly set the main display surface again for show_text_screen
                    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
                    pygame.display.set_caption('Tetris - GA Final Score')


                    show_text_screen(f'GA Final Score: {final_score}')
        else:
            print("GA training did not yield an optimal chromosome. Skipping final run.")
            if VISUALIZE_FINAL_RUN: # Or just VISUALIZE_GA_TRAINING
                 show_text_screen('GA Training Failed')

        # Wait for a key press before exiting if any visualization happened
        if VISUALIZE_FINAL_RUN or VISUALIZE_GA_TRAINING:
            print("Press any key to exit.")
            run_game = True
            while run_game:
                if check_key_press() is not None:
                    run_game = False
                pygame.display.update() # Keep screen responsive
                FPSCLOCK.tick() # Use main FPSCLOCK
                check_quit() # Allow quitting with ESC or window close

    terminate()


def run_manual_game():
    # This function uses global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT initialized in main()
    board = get_blank_board()
    last_movedown_time = time.time()
    last_moveside_time = time.time()
    last_fall_time = time.time()
    moving_down, moving_left, moving_right = False, False, False
    score = 0
    level, fall_freq = calc_level_and_fall_freq(score, is_ga_simulation=False)

    falling_piece = get_new_piece()
    next_piece = get_new_piece()

    while True:
        if falling_piece is None:
            falling_piece = next_piece
            next_piece = get_new_piece()
            last_fall_time = time.time()
            if not is_valid_position(board, falling_piece):
                show_text_screen(f'Game Over! Score: {score}') # Show final score
                return # Game Over

        check_quit() # Handles ESC and QUIT events

        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_p:
                    DISPLAYSURF.fill(BGCOLOR) # Uses global DISPLAYSURF
                    show_text_screen('Paused')
                    last_fall_time = time.time()
                    last_movedown_time = time.time()
                    last_moveside_time = time.time()
                elif event.key in (K_LEFT, K_a): moving_left = False
                elif event.key in (K_RIGHT, K_d): moving_right = False
                elif event.key in (K_DOWN, K_s): moving_down = False

            elif event.type == KEYDOWN:
                if event.key in (K_LEFT, K_a) and is_valid_position(board, falling_piece, adj_X=-1):
                    falling_piece['x'] -= 1
                    moving_left, moving_right = True, False
                    last_moveside_time = time.time()
                elif event.key in (K_RIGHT, K_d) and is_valid_position(board, falling_piece, adj_X=1):
                    falling_piece['x'] += 1
                    moving_right, moving_left = True, False
                    last_moveside_time = time.time()
                elif event.key in (K_UP, K_w): # Rotate clockwise
                    falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece['rotation'] = (falling_piece['rotation'] - 1 + len(PIECES[falling_piece['shape']])) % len(PIECES[falling_piece['shape']])
                elif event.key == K_q: # Rotate counter-clockwise
                    falling_piece['rotation'] = (falling_piece['rotation'] - 1 + len(PIECES[falling_piece['shape']])) % len(PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])
                elif event.key in (K_DOWN, K_s):
                    moving_down = True
                    if is_valid_position(board, falling_piece, adj_Y=1):
                        falling_piece['y'] += 1
                    last_movedown_time = time.time()
                elif event.key == K_SPACE: # Hard drop
                    moving_down, moving_left, moving_right = False, False, False
                    for i in range(1, BOARDHEIGHT):
                        if not is_valid_position(board, falling_piece, adj_Y=i):
                            falling_piece['y'] += i - 1
                            break
                    else: # If loop completed without break, piece might drop to bottom if board is empty
                        if is_valid_position(board, falling_piece, adj_Y=BOARDHEIGHT - 1 - falling_piece['y']):
                             falling_piece['y'] = BOARDHEIGHT -1 # simplistic drop to bottom, needs real check
                        # This part of hard drop might need more refinement to find exact landing spot.
                        # The for loop with break is more robust.
                        pass # The for loop already handled it
        
        if (moving_left or moving_right) and time.time() - last_moveside_time > MOVESIDEWAYSFREQ:
            if moving_left and is_valid_position(board, falling_piece, adj_X=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_X=1):
                falling_piece['x'] += 1
            last_moveside_time = time.time()

        if moving_down and time.time() - last_movedown_time > MOVEDOWNFREQ and is_valid_position(board, falling_piece, adj_Y=1):
            falling_piece['y'] += 1
            last_movedown_time = time.time()

        if time.time() - last_fall_time > fall_freq:
            if not is_valid_position(board, falling_piece, adj_Y=1): # Landed
                add_to_board(board, falling_piece)
                num_removed_lines = remove_complete_lines(board)
                if num_removed_lines == 1: score += 40
                elif num_removed_lines == 2: score += 120
                elif num_removed_lines == 3: score += 300
                elif num_removed_lines == 4: score += 1200
                level, fall_freq = calc_level_and_fall_freq(score, is_ga_simulation=False)
                falling_piece = None
            else: # Still falling
                falling_piece['y'] += 1
                last_fall_time = time.time()

        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, level)
        if next_piece: draw_next_piece(next_piece)
        if falling_piece: draw_piece(falling_piece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == "__main__":
    main()