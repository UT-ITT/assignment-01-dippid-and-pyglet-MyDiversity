import pyglet
import os
from DIPPID import SensorUDP
from pyglet import window, shapes

# use UDP
PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

BLOCK_WIDTH = 74.5
BLOCK_HEIGHT = 10
NUMBER_OF_BLOCKS = 50 # every layer fits 10 blocks, for good appearance set multiples of 10

PADDLE_START_X = 360
PADDLE_START_Y = 100
BALL_START_X = 400
BALL_START_Y = 200
BALL_SPEED = 5

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

paddle = shapes.Rectangle(PADDLE_START_X, PADDLE_START_Y, 120, 20, (255, 255, 255))

block = shapes.Rectangle(0, 0, BLOCK_WIDTH, BLOCK_HEIGHT, (0, 0, 255))

ball = shapes.Circle(x = BALL_START_X, y = BALL_START_Y, radius = 10, color =(255, 255, 255))

# initial ball velocities
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED

# variable for gravity sensor value
gravity_y = 0

# Variable for game state
game_won = False
game_lost = False

# variable and label for score counter
score = 0
score_label = pyglet.text.Label(
    text = str(score),
    x = 390,
    y = 50,
    font_size = 24
)

# win screen
win_screen_label = pyglet.text.Label(
    "YOU WIN!",
    x = WINDOW_WIDTH // 2,
    y = WINDOW_HEIGHT // 2,
    anchor_x = "center",
    anchor_y = "center",
    font_size = 50,
    color = (0, 255, 0)
)

# lose screen
lose_screen_label = pyglet.text.Label(
    "GAME OVER!",
    x = WINDOW_WIDTH // 2,
    y = WINDOW_HEIGHT // 2,
    anchor_x = "center",
    anchor_y = "center",
    font_size = 50,
    color = (255, 0, 0)
)

# restart game label
restart_label = pyglet.text.Label(
    "PRESS 'ENTER' TO RESTART",
    x = WINDOW_WIDTH // 2,
    y = (WINDOW_HEIGHT // 2) - 100,
    anchor_x = "center",
)

# close game label
close_label = pyglet.text.Label(
    "PRESS 'Q' TO CLOSE",
    x = WINDOW_WIDTH // 2,
    y = (WINDOW_HEIGHT // 2) - 150,
    anchor_x = "center",
)

# create block data consisting of position and color of each block
def get_block_data(block_count):
    i = 0
    current_fade = 0 # fade value to change the block color
    block_list = [] # empty list to store future block positions
    next_x_pos = 5  # starting positions for block coordinates 
    next_y_pos = 550

    # dont allow too many blocks to keep the game playable
    if block_count > 100:
        raise ValueError(f"Block count of {block_count} is too large, stay below 100")

    # create and store position and color for every block 
    while i < block_count: 
        block_list.append(((next_x_pos, next_y_pos),(current_fade, 0, 255)))
        next_x_pos += block.width + 5       # add block length and some spare space
        if next_x_pos > WINDOW_WIDTH - block.width: # start new layer if next block exceeds window width
            next_y_pos -= 2 * block.height 
            next_x_pos = 5
            current_fade += 25
        i+=1
    return block_list

block_data = get_block_data(NUMBER_OF_BLOCKS)

# define how sensor gravity data is handled
def handle_gravity(data):
    global gravity_y

    # Check if the sensor has 'gravity' capability
    if(sensor.has_capability('gravity')):

        # get gravity value for y axis
        gravity_y = sensor.get_value('gravity')['y']

sensor.register_callback('gravity', handle_gravity)

# define restart function
def reset_game():
    global block_data, game_won, game_lost, NUMBER_OF_BLOCKS
    global ball_dx, ball_dy, BALL_START_X, BALL_START_Y, BALL_SPEED
    global PADDLE_START_X, PADDLE_START_Y, score

    # generate new block data
    block_data = get_block_data(NUMBER_OF_BLOCKS)

    # reset ball and paddle positions
    ball.x, ball.y = BALL_START_X, BALL_START_Y
    paddle.x, paddle.y = PADDLE_START_X, PADDLE_START_Y
    ball_dx, ball_dy = BALL_SPEED, BALL_SPEED
    
    # reset score
    score = 0
    score_label.text = str(score)

    # reset game states
    game_won = False
    game_lost = False

# update game state
def update(dt):
    global ball_dx, ball_dy, gravity_y, score, game_won, game_lost

    # apply movement
    ball.x += ball_dx
    ball.y += ball_dy
    paddle.x += gravity_y*1.5
    
    # keep paddle in bound
    if paddle.x < 0:
        paddle.x = 0

    if paddle.x + paddle.width > WINDOW_WIDTH:
        paddle.x = WINDOW_WIDTH - paddle.width

    # check for ball collision with game window
    if ball.x - ball.radius < 0 or ball.x + ball.radius > WINDOW_WIDTH:
        ball_dx *= -1

    if  ball.y + ball.radius > WINDOW_HEIGHT:
        ball_dy *= -1

    # bottom border -> result in loss
    if ball.y - ball.radius < 0:
        game_lost = True
        return

    # check for ball collision with paddle
    if (
        ball.x + ball.radius >= paddle.x and
        ball.x - ball.radius <= paddle.x + paddle.width and
        ball.y - ball.radius <= paddle.y + paddle.height and
        ball.y > paddle.y
    ):
        if ball_dy < 0 and ball.y > paddle.y:
            ball_dy *= -1

    # check for ball collision with blocks
    for item in block_data: 
        (block_x, block_y), color = item
        if ((ball.x + ball.radius >= block_x) and 
            (ball.x - ball.radius <= block_x + BLOCK_WIDTH) and
            (ball.y + ball.radius >= block_y) and
            (ball.y - ball.radius <= block_y + BLOCK_HEIGHT)):

            block_data.remove(item) # delete block after collision
            ball_dy *= -1
            score += 1
            score_label.text = str(score)
            break

    # check if any blocks are left, if not the game is won
    if len(block_data) == 0:
        game_won = True
        return

# run update function 60 times per second
pyglet.clock.schedule_interval(update, 1/60)

@win.event
def on_draw():
    win.clear()

    # draw win screen
    if game_won:
        win_screen_label.draw()
        restart_label.draw()
        close_label.draw()
        return
    
    # draw lose screen
    if game_lost:
        lose_screen_label.draw()
        restart_label.draw()
        close_label.draw()
        return
    
    # draw paddle and ball
    paddle.draw()
    ball.draw()

    # draw blocks
    for (posX, posY), color in block_data:
        block.x, block.y = posX, posY
        block.color = color
        block.draw()
    score_label.draw()

@win.event
def on_key_press(symbol, modifiers):
    global block_data, NUMBER_OF_BLOCKS, game_lost, game_won

    # set exit key
    if symbol == pyglet.window.key.Q:
        os._exit(0)
        
    # set restart key
    if (game_lost and symbol == pyglet.window.key.ENTER) or (game_won and symbol == pyglet.window.key.ENTER):
        reset_game()

pyglet.app.run()

