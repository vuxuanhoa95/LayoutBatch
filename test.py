def get_tile_color(tile_number):
    """
    Determine the color of a tile given its tile_number (0 to 63).
    Returns 'white' for white tiles and 'black' for black tiles.
    """
    row = tile_number // 8  # Integer division to get the row index (0-7)
    col = tile_number % 8   # Modulus to get the column index (0-7)
    
    # Tiles with even row and even column or odd row and odd column are white
    if (row % 2 == 0 and col % 2 == 0) or (row % 2 != 0 and col % 2 != 0):
        return 'white'
    else:
        return 'black'

# Generate a list of numbers for tiles of the same color (e.g., white or black)
color_to_find = 'white'  # Change to 'black' for black tiles
tiles_of_same_color = [i for i in range(64) if get_tile_color(i) == color_to_find]

print(f"Tile numbers of {color_to_find} tiles: {tiles_of_same_color}")
