import pygame
import time
import math
from utils import scale_image, blit_rotate_center

# Load images for the game environment and cars
GRASS = pygame.image.load("imgs/grass.jpg")
TRACK = pygame.image.load("imgs/track.png")
TRACK_BORDER = pygame.image.load("imgs/track-border.png")

# Load and config the finish line
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH) # Create the Mask for the collide
FINISH_POSITION = (517, 862)

# Load the mask
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

# Load and scale car images
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.4)
PURPLE_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.4)

# Set the width and height of the window based on the track size
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Set the window caption
pygame.display.set_caption("Crazy cars!")

# Frames per second setting for game loop
FPS = 60

PATH = [(871, 972), (964, 908), (1001, 784), (987, 710), (915, 678), (854, 630), (877, 431), (964, 403), (994, 293), (943, 187), (873, 136), (715, 130), (651, 186), (622, 254), (621, 599), (576, 671), (498, 689), (416, 629), (389, 392), (334, 334), (164, 325), (103, 410), (95, 473), (93, 837), (137, 922), (207, 955), (352, 961), (533, 967)]
# This points have been got with 'if event.type == pygame.MOUSEBUTTONDOWN:...' (see down in code)
# Making cliks on the track to draw red points to indicate to our car computer its track.

class AbstractCar:
    # Abstract car class to define basic properties and methods for all cars
    IMG = None
    START_POS = (0, 0)
    def __init__(self, max_vel, rotation_vel):
        # Initialize car properties such as image, maximum velocity, rotation velocity, position, etc.
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 270
        self.x, self.y = self.START_POS
        self.acceleration = 0.2

    def rotate(self, left=False, right=False):
        # Rotate the car left or right by adjusting its angle
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel
    
    def draw(self, win):
        # Draw the car on the window, rotated to its current angle
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        # Increase the car's velocity up to its maximum and move it forward
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        # Decrese the car's velocity down to its minimun and move it Bakward
        # Of course a backward move in a car is smaller than a forward move (/2)
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        # Calculate the new position of the car based on its velocity and angle
        radians = math.radians(self.angle)
        v_x = self.vel * math.sin(radians)  # Calculate velocity component along x-axis
        v_y = self.vel * math.cos(radians)  # Calculate velocity component along y-axis
        
        # Update the car's position
        self.y -= v_y
        self.x -= v_x

    def collide(self, mask, x=0, y=0):
        # In Pygame, a mask is a black and white representation of an image that
        # allows for more accurate collision detection. Non-transparent pixels
        # are considered as part of the mask.

        car_mask = pygame.mask.from_surface((self.img)) #Create a mask for our image(car)
        
        offset = (int(self.x - x), int(self.y- y))
        # The offset(displacement) is the difference in (x, y) coordinates between
        # the current object and another object with which we want to check the collision.
        # self.x and self.y represent the coordinates of the current object, while x
        # and y are the coordinates of the other object.
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
        # or None if there is no collision.


    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 270
        self.vel = 0


class PlayerCar(AbstractCar):
    # Player car subclass inheriting from AbstractCar
    IMG = RED_CAR
    START_POS = (580, 885)  # Initial starting position of the player car

    def reduce_speed(self):
        # Reduce the car's speed gradually, simulating friction or coasting
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class ComputerCar(AbstractCar):
    IMG = PURPLE_CAR
    START_POS = (580, 945)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        self.draw_points(win)

def draw(win, images, player_car, computer_car):
    # Draw all the images (backgrounds, tracks, etc.) onto the window
    for img, pos in images:
        win.blit(img, pos)

    # Draw the player car on top of the images
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
    if keys[pygame.K_s]:  # Move forward if 'W' is pressed
        moved = True
        player_car.move_backward()

    # If no movement keys are pressed, reduce the car's speed
    if not moved:
        player_car.reduce_speed()



# Main game loop
run = True

clock = pygame.time.Clock()  # Clock to manage frames per second
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION)]  # List of images to be drawn each frame
player_car = PlayerCar(6, 6)  # Create a player car with specific max velocity and rotation velocity
computer_car = ComputerCar(6, 6, PATH)


while run:
    clock.tick(FPS)  # Ensure the game runs at the specified frames per second
    
    draw(WIN, images, player_car, computer_car)  # Draw all game elements each frame

    for event in pygame.event.get():
        # Check for the QUIT event to stop the game loop
        if event.type == pygame.QUIT:
            run = False
            break

        # # This code is to draw the points ofe the computer car(the PATH=[])
        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    pos = pygame.mouse.get_pos()
        #    computer_car.path.append(pos)

    move_player(player_car)

    if player_car.collide(TRACK_BORDER_MASK) != None:
        #print("COLLIDE")
        player_car.bounce()

    finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if finish_poi_collide != None:
        #print("FINISH!!!")
        print(finish_poi_collide) # This way we can see the coordinates when the car across the finish  line
        if finish_poi_collide[0] == 31: 
            player_car.bounce()
            # If coor-x == 3 then bounce!! (in finish line)
        else:
            player_car.reset()
            print("FINISH!!!")


print(computer_car.path)
pygame.quit()  # Quit pygame and close the game window


