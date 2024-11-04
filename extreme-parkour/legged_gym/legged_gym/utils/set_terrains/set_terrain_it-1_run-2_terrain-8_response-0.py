import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of steps and gentle slopes for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and heights for steps and slopes
    step_length = 0.6 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.6 + 0.1 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.2 + 0.2 * difficulty
    slope_height_min = 0.05
    slope_height_max = 0.15 + 0.1 * difficulty
    
    gap_length = 0.2 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_slope(start_x, end_x, mid_y, height_change):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height_change, num=x2-x1)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + gap_length
    next_goal_idx = 1

    for i in range(4):  # Set up 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    for i in range(3):  # Set up 3 slopes
        slope_height_change = np.random.uniform(slope_height_min, slope_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_slope(cur_x, cur_x + step_length + dx, mid_y + dy, slope_height_change)

        # Put goal in the center of the slope
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    # Add final goal on flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals