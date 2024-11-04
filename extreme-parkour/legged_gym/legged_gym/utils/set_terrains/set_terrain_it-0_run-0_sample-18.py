import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams with varied widths for the robot to balance on and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set beam dimensions
    beam_length = 2.0 - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width_min, beam_width_max = 0.4, 1.0 - 0.6 * difficulty
    beam_height = 0.2 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -m_to_idx(0.2) * difficulty, m_to_idx(0.2) * difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_width = np.random.uniform(beam_width_min, beam_width_max)

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, beam_height)

        # Put goal in the center of the beam
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap for difficulty
        gap_length = 0.2 + 0.5 * difficulty
        gap_length = m_to_idx(gap_length)
        cur_x += beam_length + dx + gap_length

    # Set final goal at the end of the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals