import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()  # Initialize font module

# Load images for the game environment and cars
GRASS = pygame.image.load("imgs/grass.jpg")  # Background image
TRACK = pygame.image.load("imgs/track.png")  # Main track image
TRACK_BORDER = pygame.image.load("imgs/track-border.png")  # Track border image for collision detection

# Load and config the finish line
FINISH = pygame.image.load("imgs/finish.png")  # Finish line image
FINISH_MASK = pygame.mask.from_surface(FINISH)  # Create the Mask for the collide
FINISH_POSITION = (517, 862)  # Finish line position

# Load the mask for track border collisions
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

# Load and scale car images
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.4)  # Load and scale red car image
PURPLE_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.4)  # Load and scale purple car image

# Set the width and height of the window based on the track size
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Create game window with dimensions of track image

# Set the window caption
pygame.display.set_caption("Crazy cars!")  # Set title of the game window

MAIN_FONT = pygame.font.SysFont("comicsans", 44)  # Define font for text display

# Frames per second setting for game loop
FPS = 60  # Game loop will run at 60 frames per second

# Path for the computer car
PATH = [
    (936, 936), (990, 745), (867, 649), (861, 445), (994, 312), (924, 175), (715, 149), 
    (627, 261), (610, 640), (489, 683), (392, 557), (373, 372), (254, 328), (139, 349), 
    (97, 561), (91, 839), (226, 940), (539, 953)
]
# Points clicked on the track to create the path for the computer-controlled car. This points have been got with 'if event.type == pygame.MOUSEBUTTONDOWN:...' (see down in code)
# Making cliks on the track to draw red points to indicate to our car computer its track.


class GameInfo:
    LEVELS = 10  # Total number of levels in the game
    
    def __init__(self, level=1):
        self.level = level  # Current level of the game
        self.started = False  # Flag to check if the level has started
        self.level_start_time = 0  # Time when the level started
    
    def next_level(self):
        self.level += 1  # Increment the level
        self.started = False  # Reset the started flag

    def reset(self):
        self.level = 1  # Reset to the first level
        self.started = False  # Reset the started flag
        self.level_start_time = 0  # Reset the level start time

    def game_finished(self):
        return self.level > self.LEVELS  # Check if the current level exceeds the total number of levels

    def start_level(self):
        self.started = True  # Set the started flag to true
        self.level_start_time = time.time()  # Record the time when the level starts

    def get_level_time(self):
        if not self.started:
            return 0  # If the level has not started, return 0
        return round(time.time() - self.level_start_time)  # Return the elapsed time since the level started


class AbstractCar:
    # Abstract car class to define basic properties and methods for all cars
    IMG = None  # Placeholder for car image
    START_POS = (0, 0)  # Placeholder for starting position

    def __init__(self, max_vel, rotation_vel):
        # Initialize car properties such as image, maximum velocity, rotation velocity, position, etc.
        self.img = self.IMG
        self.max_vel = max_vel  # Maximum velocity of the car
        self.vel = 0  # Current velocity of the car
        self.rotation_vel = rotation_vel  # Rotation velocity of the car
        self.angle = 270  # Initial angle (facing up)
        self.x, self.y = self.START_POS  # Starting position of the car
        self.acceleration = 0.2  # Acceleration rate of the car

    def rotate(self, left=False, right=False):
        # Rotate the car left or right by adjusting its angle
        if left:
            self.angle += self.rotation_vel  # Rotate left
        elif right:
            self.angle -= self.rotation_vel  # Rotate right
    
    def draw(self, win):
        # Draw the car on the window, rotated to its current angle
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move(self):
        # Calculate the new position of the car based on its velocity and angle
        radians = math.radians(self.angle)
        
        # Calculate velocity component along x-axis and y-axis
        v_x = self.vel * math.sin(radians)  
        v_y = self.vel * math.cos(radians)  

        # Update the car's position
        self.y -= v_y
        self.x -= v_x

    def move_forward(self):
        # Increase the car's velocity up to its maximum and move it forward
        self.vel = min(self.vel + self.acceleration, self.max_vel)  # Limit velocity to max_vel
        self.move()  # Move the car based on current velocity and angle

    def move_backward(self):
        # Decrease the car's velocity down to its minimum and move it backward
        # A backward move in a car is slower than a forward move (/2)
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)  # Limit backward velocity to half of max_vel
        self.move()
    def collide(self, mask, x=0, y=0):
        # In Pygame, a mask is a black and white representation of an image that
        # allows for more accurate collision detection. Non-transparent pixels
        # are considered as part of the mask.

        if self.img is None:
            raise ValueError("La imagen no se ha cargado correctamente.")
        car_mask = pygame.mask.from_surface((self.img)) #Create a mask for our image(car)
        
        offset = (int(self.x - x), int(self.y- y))
        # The offset(displacement) is the difference in (x, y) coordinates between
        # the current object and another object with which we want to check the collision.
        # self.x and self.y represent the coordinates of the current object(car), while x
        # and y are the coordinates of the other object(track-border).
        # We use int() to convert the coordinates to integers, since masks work with
        # integers and not floats.
        
        poi = mask.overlap(car_mask, offset)
        # The overlap method of the mask passed as an argument (mask) is called here.
        # This method compares the current object's mask (car_mask) with the passed
        # mask to determine if they overlap, using the offset calculated above.
        # mask.overlap(car_mask, offset) returns None if there is no overlap between
        # the masks (i.e. no collision), or a tuple with the coordinates of the
        # Point of Intersection (POI) if there is a collision.
        
        return poi
        # Return the point where the two masks overlap (if there is collision)

    def reset(self):
        # Reset the car to its initial position and settings
        self.x, self.y = self.START_POS  # Reset position
        self.angle = 270  # Reset angle to initial value
        self.vel = 0  # Reset velocity


class PlayerCar(AbstractCar):
    # Player car subclass inheriting from AbstractCar
    IMG = RED_CAR  # Image for the player car
    START_POS = (580, 885)  # Initial starting position of the player car

    def reduce_speed(self):
        # Reduce the car's speed gradually, simulating friction or coasting
        self.vel = max(self.vel - self.acceleration / 2, 0)  # Decrease velocity with a limit at zero
        self.move()  # Move the car based on current reduced velocity

    def bounce(self):
        # Reverse the car's velocity direction on collision (bounce effect)
        self.vel = -self.vel  # Invert velocity
        self.move()  # Move the car backward based on current velocity


class ComputerCar(AbstractCar):
    # Computer-controlled car subclass inheriting from AbstractCar
    IMG = PURPLE_CAR  # Image for the computer car
    START_POS = (580, 945)  # Initial starting position of the computer car

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)  # Initialize inherited properties
        self.path = path  # Path points for the computer car to follow
        self.current_point = 0  # Index of the current path point
        self.vel = max_vel  # Set initial velocity to max velocity

    def draw_points(self, win):
        # Draw red points on the track for guiding the computer car. 
        # These points are saved in path[]
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)  # Draw small red circles at each path point

    def draw(self, win):
        super().draw(win)  # Draw the computer car
        #self.draw_points(win) # Uncomment to draw the red points of the computer car path

    def calculate_angle(self):
        # Calculate the angle needed for the car to move towards the next point in its path
        target_x, target_y = self.path[self.current_point]  # Get target point coordinates
        x_diff = target_x - self.x  # Calculate difference in x
        y_diff = target_y - self.y  # Calculate difference in y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2  # Set angle to 90 degrees if y difference is zero
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)  # Calculate angle using arctangent

        if target_y > self.y:
            desired_radian_angle += math.pi  # Adjust angle if the target is below the car

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)  # Calculate difference between current and desired angles

        if difference_in_angle >= 180:
            difference_in_angle -= 360  # Normalize angle to the range (-180, 180)

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))  # Rotate left towards target
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))  # Rotate right towards target

    def update_path_point(self):
        # Update the current path point if the car has reached it
        target = self.path[self.current_point]  # Get current target point
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())  # Create rectangle for collision detection
        if rect.collidepoint(*target):  # Check if the car's rectangle collides with the target point
            self.current_point += 1  # Move to the next point

    def move(self):
        # Move the car towards the next point in the path
        if self.current_point >= len(self.path):
            # Stop moving if the path is finished
            return
        
        self.calculate_angle()  # Calculate the angle to turn towards the next path point
        self.update_path_point()  # Update the target point if necessary
        super().move()  # Move the car

    def next_level(self, level):
        # Prepare the computer car for the next level
        self.reset()  # Reset car to start position
        self.vel = self.max_vel + (level - 1) * 0.2  # Increase velocity slightly for higher levels
        self.current_point = 0  # Reset to the first point in the path


def draw(win, images, player_car, computer_car, game_info):
    # Draw all the images (backgrounds, tracks, etc.) onto the window
    for img, pos in images:
        win.blit(img, pos)  # Draw each image at its specified position

    # Render text for the level, time, and velocity
    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (218, 247, 166))
    win.blit(level_text, (10, 10))  # Display current level

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}", 1, (218, 247, 166))
    win.blit(time_text, (10, 60))  # Display elapsed time for the current level

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel)} px/s", 1, (218, 247, 166))
    win.blit(vel_text, (10, 110))  # Display player's car velocity
 
    # Draw the player and computer cars on top of the images
    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()  # Update the display to show the new frame


def move_player(player_car):
    keys = pygame.key.get_pressed()  # Check which keys are currently pressed
    moved = False  # Variable to track if the car has moved

    # Rotate or move the car based on key presses
    if keys[pygame.K_a]:  # Rotate left if 'A' is pressed
        player_car.rotate(left=True)
    if keys[pygame.K_d]:  # Rotate right if 'D' is pressed
        player_car.rotate(right=True)
    if keys[pygame.K_w]:  # Move forward if 'W' is pressed
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:  # Move backward if 'S' is pressed
        moved = True
        player_car.move_backward()

    # If no movement keys are pressed, reduce the car's speed
    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car, computer_car, game_info):
    # Check for collisions between the player car and the track border
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()  # Bounce the car back if a collision is detected

    # Check if the computer car has reached the finish line
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        # Display loss message if computer reaches finish line
        print("Computer win!!")
        blit_text_center(WIN, MAIN_FONT, "You lost!!")
        pygame.display.update()
        pygame.time.wait(5000)  # Pause for a moment before restarting
        game_info.reset()  # Reset game info for a new game
        player_car.reset()  # Reset player car
        computer_car.reset()  # Reset computer car

    # Check if the player car has reached the finish line
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        print(player_finish_poi_collide)  # Log coordinates when crossing the finish line
        if player_finish_poi_collide[0] == 31: 
            player_car.bounce()  # Bounce back if hitting the finish line border
        else:
            game_info.next_level()  # Advance to the next level
            player_car.reset()  # Reset player car position and settings
            computer_car.next_level(game_info.level)  # Prepare computer car for next level
            print("FINISH!!!")


# Main game loop
run = True

clock = pygame.time.Clock()  # Clock to manage frames per second
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION)]  # List of images to be drawn each frame
player_car = PlayerCar(6, 6)  # Create a player car with specific max velocity and rotation velocity
computer_car = ComputerCar(4, 6, PATH)  # Create a computer car with max velocity, rotation velocity, and a path
game_info = GameInfo()  # Initialize game information object

while run:
    clock.tick(FPS)  # Ensure the game runs at the specified frames per second
    
    draw(WIN, images, player_car, computer_car, game_info)  # Draw all game elements each frame

    while not game_info.started:
        # Display message to start the level
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            # Check for the QUIT event to stop the game loop
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()  # Start the level on any key press

    for event in pygame.event.get():
        # Check for the QUIT event to stop the game loop
        if event.type == pygame.QUIT:
            run = False
            break

        # Uncomment this code to draw points for the computer car path dynamically
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     pos = pygame.mouse.get_pos()
        #     computer_car.path.append(pos)

    move_player(player_car)  # Handle player car movement
    computer_car.move()  # Handle computer car movement
    handle_collision(player_car, computer_car, game_info)  # Handle collision detection

    if game_info.game_finished():
        # Display win message if game is finished
        blit_text_center(WIN, MAIN_FONT, "You won the game!!")
        pygame.time.wait(5000)
        game_info.reset()  # Reset game info for a new game
        player_car.reset()  # Reset player car
        computer_car.reset()  # Reset computer car


print(computer_car.path)  # Print path points for debugging
pygame.quit()  # Quit pygame and close the game window

