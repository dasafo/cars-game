import pygame

def scale_image(img, factor):
    """
    Function to scale images in our game.
    """
    # Calculate the new size for the image by multiplying the original width and height
    # by the scaling factor.
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    
    # Return the scaled image using pygame's transform.scale method.
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_Left, angle):
    # Rotate the original image by the given angle.
    rotated_image = pygame.transform.rotate(image, angle)

    # When we rotate the original image, the size of the image's rectangle can change
    # based on how it's rotated around the top left corner. To keep the rotation 
    # centered on the image's initial center, we adjust its rectangle.
    # Get a new rectangle for the rotated image. The new rectangle is positioned so
    # that its center matches the center of the original image's rectangle.
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_Left).center)

    # Draw the rotated image onto the window (win) at the new top-left position
    # of the adjusted rectangle.
    win.blit(rotated_image, new_rect.topleft)

def blit_text_center(win, font, text):
    render = font.render(text, 1 , (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2))

