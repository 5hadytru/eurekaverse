import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple platforms, ramps, and gaps of increasing difficulty"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform, ramp dimensions and gap lengths
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6  # Keep the platform width fixed
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.5 + 0.5 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, x_end, mid_y, height):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x_start:x_end, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        ramp_height = np.linspace(0, height, num=end_x-start_x)
        ramp_height = ramp_height[None, :]  # add a new axis for broadcasting to y
        ramp_height = ramp_height[::direction]  # reverse the ramp if direction is -1
        height_field[start_x:end_x, y1:y2] = ramp_height.T

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            # Add a platform
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        else:
            # Add a ramp
            direction = (-1) ** i  # Alternate slope directions
            add_ramp(cur_x, cur_x + platform_length, mid_y, height, direction)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        
        # Adding a gap between obstacles
        cur_x += platform_length + dx_min + np.random.randint(dx_max) + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals