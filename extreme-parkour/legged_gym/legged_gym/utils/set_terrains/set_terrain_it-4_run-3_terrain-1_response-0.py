import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Zigzag sloped ramps and variable-height platforms to test balance and varied movement."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for platforms and ramps
    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    ramp_length = 1.0 - 0.15 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1 + 0.15 * difficulty, 0.35 + 0.25 * difficulty
    slope_width = m_to_idx(1.0)
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal at spawn

    cur_x = spawn_length
    for i in range(3):  # Add 3 platform-ramp pairs
        # Add a platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Add a ramp
        direction = (-1) ** i  # Alternate ramp direction (left/right)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * direction

        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)

        # Put goal in the center of the ramp
        goals[i+4] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        cur_x += ramp_length + dx + gap_length
    
    # Add final goal, fill remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals