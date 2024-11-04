import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Platforms with alternating heights and narrow bridges for advanced stability and height navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.6  # meters
    platform_length = m_to_idx(platform_length)
    bridge_width_min, bridge_width_max = 0.3, 0.5
    bridge_width_min, bridge_width_max = m_to_idx(bridge_width_min), m_to_idx(bridge_width_max)
    platform_width_range = (0.8 - 0.3 * difficulty, 1.1 - 0.2 * difficulty)  # Decreasing platform width with difficulty
    platform_width = np.random.uniform(*platform_width_range)
    platform_width = m_to_idx(platform_width)
    platform_height_range = (0.1 + 0.3 * difficulty, 0.4 + 0.4 * difficulty)  # Increasing height with difficulty
    gap_length = 0.2 + 0.4 * difficulty  # Increasing gap length with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_field[x1-1, mid_y]  # Extend the previous platform height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initial platform
    initial_platform_height = np.random.uniform(*platform_height_range)
    cur_x = spawn_length
    add_platform(cur_x, cur_x + platform_length, mid_y, initial_platform_height)
    cur_x += platform_length

    for i in range(6):  # Set up 6 platforms and 5 bridges
        # Add bridge
        bridge_width = np.random.uniform(bridge_width_min, bridge_width_max)
        add_bridge(cur_x, cur_x + gap_length, mid_y, bridge_width)
        
        # Update current x to end of bridge
        cur_x += gap_length

        # Add platform of varying height
        platform_height = np.random.uniform(*platform_height_range)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Update current x to end of platform
        cur_x += platform_length + dx

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals