import tensorflow as tf
import numpy as np

epsilon = 1e-7
config_inv_temp = 0.5
config_inv_temp_delta = 0.1


def em_routing(v, a_i, beta_v, beta_a, n_iterations=3):
    batch_size = v.shape[0]
    _, _, n_caps_j, mat_len = v.shape
    n_caps_j, mat_len = map(int, [n_caps_j, mat_len])
    n_caps_i = v.shape[1]

    a_i = tf.expand_dims(a_i, axis=-1)

    # Prior probabilities for routing
    r = tf.ones(shape=(batch_size, n_caps_i, n_caps_j, 1), dtype=tf.float32) / float(n_caps_j)
    r = tf.multiply(r, a_i)

    den = tf.reduce_sum(r, axis=1, keepdims=True) + epsilon

    # Mean: shape=(N, 1, Ch_j, mat_len)
    m_num = tf.reduce_sum(v * r, axis=1, keepdims=True)
    m = m_num / (den + epsilon)

    # Stddev: shape=(N, 1, Ch_j, mat_len)
    s_num = tf.reduce_sum(r * tf.square(v - m), axis=1, keepdims=True)
    s = s_num / (den + epsilon)

    # cost_h: shape=(N, 1, Ch_j, mat_len)
    cost = (beta_v + tf.math.log(tf.sqrt(s + epsilon) + epsilon)) * den
    # cost_h: shape=(N, 1, Ch_j, 1)
    cost = tf.reduce_sum(cost, axis=-1, keepdims=True)

    # calculates the mean and std_deviation of the cost, used for numerical stability
    cost_mean = tf.reduce_mean(cost, axis=-2, keepdims=True)
    cost_stdv = tf.sqrt(tf.reduce_sum(tf.square(cost - cost_mean), axis=-2, keepdims=True) / n_caps_j + epsilon)

    # calculates the activations for the capsules in layer j
    a_j = tf.sigmoid(float(config_inv_temp) * (beta_a + (cost_mean - cost) / (cost_stdv + epsilon)))

    def condition(mean, stdsqr, act_j, r_temp, counter):
        return tf.less(counter, n_iterations)

    def route(mean, stdsqr, act_j, r_temp, counter):
        exp = tf.reduce_sum(tf.square(v - mean) / (2 * stdsqr + epsilon), axis=-1)
        coef = 0 - .5 * tf.reduce_sum(tf.math.log(2 * np.pi * stdsqr + epsilon), axis=-1)
        log_p_j = coef - exp

        log_ap = tf.reshape(tf.math.log(act_j + epsilon), (batch_size, 1, n_caps_j)) + log_p_j
        r_ij = tf.nn.softmax(log_ap + epsilon)  # ap / (tf.reduce_sum(ap, axis=-1, keepdims=True) + epsilon)

        r_ij = tf.multiply(tf.expand_dims(r_ij, axis=-1), a_i)

        denom = tf.reduce_sum(r_ij, axis=1, keepdims=True) + epsilon
        m_numer = tf.reduce_sum(v * r_ij, axis=1, keepdims=True)
        mean = m_numer / (denom + epsilon)

        s_numer = tf.reduce_sum(r_ij * tf.square(v - mean), axis=1, keepdims=True)
        stdsqr = s_numer / (denom + epsilon)

        cost_h = (beta_v + tf.math.log(tf.sqrt(stdsqr) + epsilon)) * denom

        cost_h = tf.reduce_sum(cost_h, axis=-1, keepdims=True)
        cost_h_mean = tf.reduce_mean(cost_h, axis=-2, keepdims=True)
        cost_h_stdv = tf.sqrt(tf.reduce_sum(tf.square(cost_h - cost_h_mean), axis=-2, keepdims=True) / n_caps_j)

        inv_temp = config_inv_temp + counter * config_inv_temp_delta
        act_j = tf.sigmoid(inv_temp * (beta_a + (cost_h_mean - cost_h) / (cost_h_stdv + epsilon)))

        return mean, stdsqr, act_j, r_ij, tf.add(counter, 1)

    [mean, _, act_j, r_new, _] = tf.while_loop(condition, route, [m, s, a_j, r, 1.0])

    return tf.reshape(mean, (batch_size, n_caps_j, mat_len)), tf.reshape(act_j, (batch_size, n_caps_j, 1))


# Attention Routing layer
def em_routing_cond(v_v1, v_v2, a_i_v, v_f, a_i_f, beta_v_v, beta_a_v, beta_v_f, beta_a_f, n_iterations=3):
    batch_size = v_f.shape[0]
    _, _, n_caps_j, mat_len = v_f.shape
    n_caps_j, mat_len = map(int, [n_caps_j, mat_len])
    n_caps_i_f = v_f.shape[1]

    a_i_f = tf.expand_dims(a_i_f, axis=-1)

    # Prior probabilities for routing
    r_f = tf.ones(shape=(batch_size, n_caps_i_f, n_caps_j, 1), dtype=tf.float32) / float(n_caps_j)
    r_f = tf.multiply(r_f, a_i_f)

    den_f = tf.reduce_sum(r_f, axis=1, keepdims=True) + epsilon

    m_num_f = tf.reduce_sum(v_f * r_f, axis=1, keepdims=True)  # Mean: shape=(N, 1, Ch_j, mat_len)
    m_f = m_num_f / (den_f + epsilon)

    s_num_f = tf.reduce_sum(r_f * tf.square(v_f - m_f), axis=1, keepdims=True)  # Stddev: shape=(N, 1, Ch_j, mat_len)
    s_f = s_num_f / (den_f + epsilon)

    cost_f = (beta_v_f + tf.math.log(tf.sqrt(s_f + epsilon) + epsilon)) * den_f  # cost_h: shape=(N, 1, Ch_j, mat_len)
    cost_f = tf.reduce_sum(cost_f, axis=-1, keepdims=True)  # cost_h: shape=(N, 1, Ch_j, 1)

    # calculates the mean and std_deviation of the cost
    cost_mean_f = tf.reduce_mean(cost_f, axis=-2, keepdims=True)
    cost_stdv_f = tf.sqrt(tf.reduce_sum(tf.square(cost_f - cost_mean_f), axis=-2, keepdims=True) / n_caps_j + epsilon)

    # calculates the activations for the capsules in layer j for the frame capsules
    a_j_f = tf.sigmoid(float(config_inv_temp) * (beta_a_f + (cost_mean_f - cost_f) / (cost_stdv_f + epsilon)))

    def condition(mean_f, stdsqr_f, act_j_f, counter):
        return tf.less(counter, n_iterations)

    def route(mean_f, stdsqr_f, act_j_f, counter):
        # Performs E-step for frames
        exp_f = tf.reduce_sum(tf.square(v_f - mean_f) / (2 * stdsqr_f + epsilon), axis=-1)
        coef_f = 0 - .5 * tf.reduce_sum(tf.math.log(2 * np.pi * stdsqr_f + epsilon), axis=-1)
        log_p_j_f = coef_f - exp_f

        log_ap_f = tf.reshape(tf.math.log(act_j_f + epsilon), (batch_size, 1, n_caps_j)) + log_p_j_f
        r_ij_f = tf.nn.softmax(log_ap_f + epsilon)

        # Performs M-step for frames
        r_ij_f = tf.multiply(tf.expand_dims(r_ij_f, axis=-1), a_i_f)

        denom_f = tf.reduce_sum(r_ij_f, axis=1, keepdims=True) + epsilon
        m_numer_f = tf.reduce_sum(v_f * r_ij_f, axis=1, keepdims=True)
        mean_f = m_numer_f / (denom_f + epsilon)

        s_numer_f = tf.reduce_sum(r_ij_f * tf.square(v_f - mean_f), axis=1, keepdims=True)
        stdsqr_f = s_numer_f / (denom_f + epsilon)

        cost_h_f = (beta_v_f + tf.math.log(tf.sqrt(stdsqr_f + epsilon) + epsilon)) * denom_f

        cost_h_f = tf.reduce_sum(cost_h_f, axis=-1, keepdims=True)
        cost_h_mean_f = tf.reduce_mean(cost_h_f, axis=-2, keepdims=True)
        cost_h_stdv_f = tf.sqrt(
            tf.reduce_sum(
                tf.square(cost_h_f - cost_h_mean_f), axis=-2, keepdims=True
            ) / n_caps_j + epsilon
        )

        inv_temp = config_inv_temp + counter * config_inv_temp_delta
        act_j_f = tf.sigmoid(inv_temp * (beta_a_f + (cost_h_mean_f - cost_h_f) / (cost_h_stdv_f + epsilon)))

        return mean_f, stdsqr_f, act_j_f, tf.add(counter, 1)

    [mean_f_fin, _, act_j_f_fin, _] = tf.while_loop(condition, route, [m_f, s_f, a_j_f, 1.0])

    # performs m step for the video capsules
    a_i_v = tf.expand_dims(a_i_v, axis=-1)

    dist_v = tf.reduce_sum(tf.square(v_v1 - mean_f_fin), axis=-1)
    r_v = tf.expand_dims(tf.nn.softmax(0 - dist_v), axis=-1) * a_i_v

    den_v = tf.reduce_sum(r_v, axis=1, keepdims=True) + epsilon

    m_num_v = tf.reduce_sum(v_v2 * r_v, axis=1, keepdims=True)  # Mean: shape=(N, 1, Ch_j, mat_len)
    m_v = m_num_v / (den_v + epsilon)

    s_num_v = tf.reduce_sum(r_v * tf.square(v_v2 - m_v), axis=1, keepdims=True)  # Stddev: shape=(N, 1, Ch_j, mat_len)
    s_v = s_num_v / (den_v + epsilon)

    cost_v = (beta_v_v + tf.math.log(tf.sqrt(s_v + epsilon) + epsilon)) * den_v  # cost_h: shape=(N, 1, Ch_j, mat_len)
    cost_v = tf.reduce_sum(cost_v, axis=-1, keepdims=True)  # cost_h: shape=(N, 1, Ch_j, 1)

    # calculates the mean and std_deviation of the cost
    cost_mean_v = tf.reduce_mean(cost_v, axis=-2, keepdims=True)
    cost_stdv_v = tf.sqrt(
        tf.reduce_sum(
            tf.square(cost_v - cost_mean_v), axis=-2, keepdims=True
        ) / n_caps_j + epsilon
    )

    # calculates the activations for the capsules in layer j for the frame capsules
    a_j_v = tf.sigmoid(float(config_inv_temp) * (beta_a_v + (cost_mean_v - cost_v) / (cost_stdv_v + epsilon)))

    return (tf.reshape(m_v, (batch_size, n_caps_j, mat_len)), tf.reshape(a_j_v, (batch_size, n_caps_j, 1))), \
           (tf.reshape(mean_f_fin, (batch_size, n_caps_j, mat_len)), tf.reshape(act_j_f_fin, (batch_size, n_caps_j, 1)))


def create_coords_mat(pose, rel_center, dim_capsules):
    """
        :param pose: the incoming map of pose matrices, shape (N, ..., Ch_i, 16) where ... is the dimensions of the map can
        be 1, 2 or 3 dimensional.
        :param rel_center: whether or not the coordinates are relative to the center of the map
        :param dim_capsules:
        :return: returns the coordinates (padded to 16) fir the incoming capsules
        """
    batch_size = pose.shape[0]
    shape_list = [int(x) for x in pose.shape[1:-2]]
    ch = int(pose.shape[-2])
    n_dims = len(shape_list)

    if n_dims == 3:
        d, h, w = shape_list
    elif n_dims == 2:
        d = 1
        h, w = shape_list
    else:
        d, h = 1, 1
        w = shape_list[0]

    subs = [0, 0, 0]
    if rel_center:
        subs = [int(d / 2), int(h / 2), int(w / 2)]

    c_mats = []
    if n_dims >= 3:
        c_mats.append(tf.tile(tf.reshape(tf.range(d, dtype=tf.float32),
                                         (1, d, 1, 1, 1, 1)), [batch_size, 1, h, w, ch, 1]) - subs[0])
    if n_dims >= 2:
        c_mats.append(tf.tile(tf.reshape(tf.range(h, dtype=tf.float32),
                                         (1, 1, h, 1, 1, 1)), [batch_size, d, 1, w, ch, 1]) - subs[1])
    if n_dims >= 1:
        c_mats.append(tf.tile(tf.reshape(tf.range(w, dtype=tf.float32),
                                         (1, 1, 1, w, 1, 1)), [batch_size, d, h, 1, ch, 1]) - subs[2])
    add_coords = tf.concat(c_mats, axis=-1)
    add_coords = tf.cast(tf.reshape(add_coords, (batch_size, d * h * w, ch, n_dims)), dtype=tf.float32)

    mdim2 = dim_capsules * dim_capsules
    zeros = tf.zeros((batch_size, d * h * w, ch, mdim2 - n_dims))

    return tf.concat([zeros, add_coords], axis=-1)
