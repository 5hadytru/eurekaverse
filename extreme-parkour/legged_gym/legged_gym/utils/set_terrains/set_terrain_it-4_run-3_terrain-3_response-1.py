import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple platforms, narrow beams, and ramps for the robot to climb on, balance, and jump across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(1.0)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.15 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    # Set up narrow beam dimensions
    beam_length = platform_length
    beam_width = m_to_idx(0.4 - 0.1 * difficulty)  # Narrower beams
    beam_height = 0.15 + 0.35 * difficulty

    # Set up ramp dimensions
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)
    ramp_width = m_to_idx(0.4 - 0.1 * difficulty)
    ramp_height = 0.2 + 0.5 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width * direction, mid_y + half_width * direction
        slant = np.linspace(0, ramp_height, num=x2 - x1)[::direction]
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    alternator = 0  # To alternate between different obstacles

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max)

        if alternator % 3 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        elif alternator % 3 == 1:
            add_narrow_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]
        else:
            direction = 1 if i % 4 < 2 else -1
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length
        alternator += 1

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals