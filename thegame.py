#=====================================
#=******** LEAGUE OF BALLERZ******** =
#=        MADE BY AARON RUBIO        =
#=====================================
from tkinter import *
from time import *
from random import *
from math import *
from PIL import Image, ImageTk

root = Tk()
root.title("Basketball Shooting Game")
screen = Canvas(root, width=800, height=600, background="black")
screen.pack()

# Images
player1 = PhotoImage(file="Sprites/idle.png")
background001 = PhotoImage(file="Backgrounds/background001.png")
background002 = PhotoImage(file="Backgrounds/background002.png")
background004 = PhotoImage(file="Backgrounds/background004.png")
instructionsBackground = PhotoImage(file="Backgrounds/Instructionsbackground.png")

# Global variables
force_slider = None
angle_slider = None
timer_text = None
ball = None
player_sprite = None
score_text = None
game_over_text = None
restart_text = None
mainscreen = None
idle_sprite = None
windup_sprite = None
release_sprite = None
ball_sprite = None
score = 0
time_left = 0
obstacles = []  # List to store obstacle objects

def setInitialValues():
    global yGround, w, xStart, player_height, player_width, grav, falling_grav
    global shooting, animating_shot, score, shots_needed, game_time, time_left
    global timer_running, scored, game_over_flag, xSpeed, ySpeed, obstacles
    global hoop_x, hoop_y, backboard_x, backboard_top, backboard_bottom
    
    yGround = 500
    w = 40
    xStart = 130
    player_height = 80
    player_width = 50
    grav = 0.3
    falling_grav = 0.7
    shooting = False
    animating_shot = False
    score = 0
    shots_needed = 5
    game_time = 60
    time_left = game_time
    timer_running = True
    scored = False
    game_over_flag = False
    xSpeed = 0
    ySpeed = 0
    obstacles = []  # Clear obstacles when resetting game
    
    # Hoop and backboard positions
    hoop_x = 600
    hoop_y = 300
    backboard_x = hoop_x + 50
    backboard_top = hoop_y - 50
    backboard_bottom = hoop_y + 200

def reset_ball():
    global xSpeed, ySpeed, scored, ball
    xSpeed = 0
    ySpeed = 0
    scored = False
    screen.coords(ball, xStart, yGround - player_height - w // 2)
    screen.itemconfig(ball, state='hidden')

def reset_player_sprite():
    global player_sprite
    screen.itemconfig(player_sprite, image=idle_sprite)

def create_obstacle():
    """Create a single moving obstacle"""
    xR = randint(300, 550)  # Randomize x position
    yR = randint(0, 400)    # Randomize y position
    w = 20
    h = 110
    yspeed = uniform(1, 2)
    box = screen.create_rectangle(xR, yR, xR + w, yR + h, fill="white")
    
    obstacle = {
        'body': box,
        'x': xR,
        'y': yR,
        'w': w,
        'h': h,
        'yspeed': yspeed 
    }
    
    return obstacle

def animate_obstacles():
    global obstacles
    
    for obstacle in obstacles:
        # Update position
        obstacle['y'] += obstacle['yspeed']
        
        # Boundary checks
        if obstacle['y'] + obstacle['h'] >= 600 or obstacle['y'] <= 0:
            obstacle['yspeed'] = obstacle['yspeed']*-1.0
        
        # Move the obstacle
        screen.coords(obstacle['body'], 
                      obstacle['x'], obstacle['y'], 
                      obstacle['x'] + obstacle['w'], 
                      obstacle['y'] + obstacle['h'])
    
    # Next animation frame if obstacles exist
    if obstacles:
        root.after(30, animate_obstacles)

def animate_shot():
    global animating_shot

    def show_release_pose():
        screen.itemconfig(player_sprite, image=release_sprite)

    def show_ball():
        screen.itemconfig(ball, state='normal')

    screen.itemconfig(player_sprite, image=windup_sprite)
    screen.itemconfig(ball, state='hidden')
    
    # Schedule the actions
    root.after(200, show_release_pose)
    root.after(200, show_ball)
    root.after(400, stay_in_release_pose)
    root.after(400, set_animating_shot_false)
    root.after(400, start_ball_motion)

def stay_in_release_pose():
    screen.itemconfig(player_sprite, image=release_sprite)

def set_animating_shot_false():
    global animating_shot
    animating_shot = False

def start_ball_motion():
    global shooting, xSpeed, ySpeed
    if not shooting:
        shooting = True
        force = force_slider.get()
        angle = angle_slider.get()
        angle_radians = radians(angle)
        xSpeed = force * cos(angle_radians)
        ySpeed = -force * sin(angle_radians)

def shoot(event):
    global animating_shot
    if not game_over_flag and not animating_shot and not shooting:
        animating_shot = True
        screen.itemconfig(ball, state='hidden')
        animate_shot()

def main_loop():
    global shooting, score, xSpeed, ySpeed, scored, time_left, timer_running, obstacles
    
    if shooting == True:
        x1, y1 = screen.coords(ball)
        
        x1 += xSpeed
        ySpeed += grav
        y1 += ySpeed
        
        screen.coords(ball, x1, y1)
        
        # Obstacle collision detection
        ball_size = w
        for obstacle in obstacles:
            if (obstacle['x'] < x1 + ball_size and 
                obstacle['x'] + obstacle['w'] > x1 and 
                obstacle['y'] < y1 + ball_size and 
                obstacle['y'] + obstacle['h'] > y1):
                # Bounce back with reduced speed
                xSpeed = -xSpeed * 0.7
                ySpeed = -ySpeed * 0.7
        
        # Scoring logic(When the ball goes through the rim)
        if hoop_x <= x1 + w / 2 <= hoop_x + 50 and hoop_y + 25 <= y1 + w / 2 <= hoop_y + 30 and not scored:
            score += 1
            screen.itemconfig(score_text, text=f"Score: {score}")
            scored = True
            screen.itemconfig(ball, state='normal')
            
            # Add an obstacle for each score
            if len(obstacles) < score:
                new_obstacle = create_obstacle()
                obstacles.append(new_obstacle)
                
                # Start obstacle animation
                if len(obstacles) == 1:
                    animate_obstacles()
            
            if score >= shots_needed:
                game_over()
        
        # Collision detection(Ball bounceing off the rim)
        if (hoop_x <= x1 + w / 2 <= hoop_x + 50 and hoop_y - 5 <= y1 + w / 2 <= hoop_y + 25):
            if not scored:
                xSpeed = -xSpeed * 0.7
                ySpeed = -ySpeed * 0.7
        
        if (backboard_x - 5 <= x1 + w / 2 <= backboard_x + 5 and backboard_top <= y1 + w / 2 <= backboard_bottom):
            xSpeed = -xSpeed * 0.8
        
        if y1 + w >= yGround:
            shooting = False
            reset_ball()
            reset_player_sprite()
    
    root.after(20, main_loop)

def timer_update():
    global time_left, timer_running
    if timer_running and time_left > 0 and not game_over_flag:
        time_left -= 1
        screen.itemconfig(timer_text, text=f"Time: {time_left}s")
        root.after(1000, timer_update)
    elif time_left == 0 and not game_over_flag:
        timer_running = False
        game_over()

def game_over():
    global game_over_flag
    game_over_flag = True
        
    if score == 5:
        screen.delete("all")
        screen.create_text(400, 300, text="Winner!", fill="red", font=("Arial", 60))
        screen.create_text(400, 365, text="Press 'R' to Restart", fill="white", font=("Arial", 20))
    else:
        screen.delete("all")
        screen.create_text(400, 300, text="Game Over!", fill="red", font=("Arial", 60))
        screen.create_text(400, 365, text="Press 'R' to Restart", fill="white", font=("Arial", 20))

def reset_game(event):
    global score, time_left, game_over_flag, timer_running, obstacles
    
    # Clear all canvas elements
    screen.delete("all")
    
    # Destroy existing sliders to avoid duplicates
    if force_slider:
        force_slider.destroy()
    if angle_slider:
        angle_slider.destroy()
    
    # Reset game variables
    score = 0
    time_left = game_time
    game_over_flag = False
    timer_running = True
    obstacles = [] 
    
    # Return to main screen
    screen.create_image(0, 0, image=background001, anchor="nw")
    startScreen()

def startScreen():
    root.bind("<Button-1>", startScreenClick)
    
def drawObjects():
    global idle_sprite, windup_sprite, release_sprite, ball_sprite, ball
    global score_text, timer_text, game_over_text, restart_text
    global force_slider, angle_slider, player_sprite
    
    # Load sprites
    idle_sprite = PhotoImage(file="Sprites/idle.png")
    windup_sprite = PhotoImage(file="Sprites/windup.png")
    release_sprite = PhotoImage(file="Sprites/release.png")
    ball_sprite = PhotoImage(file="Sprites/basketball.png")
    
    # Draw game elements
    screen.create_oval(hoop_x, hoop_y, hoop_x + 50, hoop_y + 25, outline="red", width=6)
    screen.create_line(hoop_x + 50, backboard_top, hoop_x + 50, backboard_bottom, fill="white", width=10)
    screen.create_line(0, yGround, 800, yGround, fill="white", width=2)
    
    # Create sprites
    player_sprite = screen.create_image(xStart, yGround - player_height // 2, image=idle_sprite)
    ball = screen.create_image(xStart, yGround - player_height - w // 2, image=ball_sprite, state='hidden')
    screen.tag_lower(ball, player_sprite)
    
    # Create UI elements
    score_text = screen.create_text(50, 50, text=f"Score: {score}", fill="white", font=("Arial", 20))
    timer_text = screen.create_text(750, 50, text=f"Time: {time_left}s", fill="white", font=("Arial", 20))
    
    # Create sliders
    force_slider = Scale(root, from_=5, to_=30, orient=HORIZONTAL, label="Force (Speed)", length=200)
    force_slider.set(8)
    force_slider.pack(pady=20)
    
    angle_slider = Scale(root, from_=0, to_=90, orient=HORIZONTAL, label="Angle (Degrees)", length=200)
    angle_slider.set(60)
    angle_slider.pack(pady=20)
    
    

def startScreenClick(event):
    xMouse = event.x
    yMouse = event.y
    
    # ONE PLAYER button
    if 490 <= xMouse <= 720 and 180 <= yMouse <= 250:
        screen.delete("all")  # Clear screen
        runGame()
    
    # TWO PLAYER button
    elif 490 <= xMouse <= 720 and 285 <= yMouse <= 345:
        screen.delete("all")
        screen.create_image(0, 0, image=background004, anchor="nw")
        # Use after instead of sleep to avoid freezing the UI
        root.after(2000, return_to_main_menu)
    
    # INSTRUCTIONS button
    elif 490 <= xMouse <= 720 and 390 <= yMouse <= 445:
        screen.delete("all")
        screen.create_image(0, 0, image=instructionsBackground, anchor="nw")
        # Add a back button or timeout to return to main menu
        root.after(7500, return_to_main_menu)

def return_to_main_menu():
    screen.delete("all")
    screen.create_image(0, 0, image=background001, anchor="nw")

def runGame():
    setInitialValues()
    drawObjects()
    main_loop()
    timer_update()

def startScreen():
    root.bind("<Button-1>", startScreenClick)

# Initialize game
mainscreen = screen.create_image(0, 0, image=background001, anchor="nw")
root.bind("<space>", shoot)
root.bind("<r>", reset_game)
startScreen()

root.mainloop()
