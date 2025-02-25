import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines narrow beams, ramps, and staggered platforms to increase the difficulty for the robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_beam(start_x, end_x, center_y, width, height):
        """Adds a narrow beam at specified x and y coordinates."""
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, center_y, width, height_diff, direction):
        """Adds a ramp at specified x and y coordinates."""
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        slant = np.linspace(0, height_diff, num=y2-y1 if direction else x2-x1)
        if direction:
            slant = slant[None, :]  # Ramp along y-axis
        else:
            slant = slant[:, None]  # Ramp along x-axis
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]  

    platform_length = 1.0 - 0.2 * difficulty
    platform_width = 0.4 + 0.2 * difficulty
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    platform_length, platform_width = m_to_idx(platform_length), m_to_idx(platform_width)
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    cur_x = spawn_length
    for i in range(6):  # Set up platforms, ramps, and narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 3 == 0:  # Build beam
            beam_width = m_to_idx(0.3)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, beam_width, beam_height)
        elif i % 3 == 1:  # Build ramp
            ramp_height_diff = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, ramp_height_diff, direction=(i % 2 == 0))
        else:  # Build platform
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, np.random.uniform(platform_height_min, platform_height_max))
            
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals