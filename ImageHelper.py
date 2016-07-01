import numpy


MSE_SIMILARITY_THRESHOLD = 2000
PERCENT_DIFF_THRESHOLD = 3.25
FILL_RATIO_DIFF_THRESHOLD = 0.25
FILL_RATIO_DIFF_MIN_THRESHOLD = 0.05


def get_mse(figure1, figure2):
    figure1_arr = numpy.array(figure1)
    figure2_arr = numpy.array(figure2)
    err = numpy.sum((figure1_arr.astype("float")
                     - figure2_arr.astype("float")) ** 2)
    err /= float(figure1_arr.shape[0] * figure1_arr.shape[1])
    return err


def get_percent_diff(figure1, figure2):
    figure1_arr = numpy.array(figure1)
    figure2_arr = numpy.array(figure2)
    err = numpy.sum((figure1_arr.astype("float")
                     - figure2_arr.astype("float")) ** 2)
    err /= float(figure1_arr.shape[0] * figure1_arr.shape[1])
    return err * 100


def get_black_white_ratio(figure1, figure2):
    figure1_bw = get_bw_image(figure1)
    figure2_bw = get_bw_image(figure2)
    #figure1_arr = numpy.array(figure1).copy()
    #figure1_gray = figure1_arr.convert('L')
    #figure1_bw = numpy.asarray(figure1_gray).copy()
    #figure2_arr = numpy.array(figure2).copy()
    #figure2_gray = figure2_arr.convert('L')
    #figure2_bw = numpy.asarray(figure2_gray).copy()
    figure1_arr = figure1_bw.reshape(figure1_bw.shape[0] * figure1_bw.shape[1])
    figure2_arr = figure2_bw.reshape(figure2_bw.shape[0] * figure2_bw.shape[1])
    figure1_ratio = 0
    figure2_ratio = 0
    for pixel in figure1_arr:
        figure1_ratio += 1 if pixel == 1 else 0
    for pixel in figure2_arr:
        figure2_ratio += 1 if pixel == 1 else 0
    return float(figure2_ratio)/figure1_ratio


# Returns angle of rotation if the images are rotations. Else -1.
def get_rotation_degrees(figure1, figure2):
    figure1_arr = numpy.array(figure1)
    figure2_arr = numpy.array(figure2)
    for k in xrange(4):
        if get_mse(numpy.rot90(figure1_arr, k), figure2_arr) \
                < MSE_SIMILARITY_THRESHOLD:
            return 90 * k
    return -1


# Returns axis of reflection (x or y) if the images are reflections. Else False.
def get_reflection_axis(figure1, figure2):
    figure1_arr = numpy.array(figure1)
    figure2_arr = numpy.array(figure2)
    if get_mse(numpy.fliplr(figure1_arr), figure2_arr) \
            < MSE_SIMILARITY_THRESHOLD:
        return 'y'
    if get_mse(numpy.flipud(figure1_arr), figure2_arr) \
            < MSE_SIMILARITY_THRESHOLD:
        return 'x'
    return False


def get_bw_image(figure):
    figure_gray = figure.convert('L')
    figure_bw = numpy.asarray(figure_gray).copy()
    figure_bw[figure_bw < 128] = 1
    figure_bw[figure_bw >= 128] = 0
    return figure_bw


def check_fills_complement(figure1, figure2):
    figure1_bw = get_bw_image(figure1)
    figure2_bw = get_bw_image(figure2)
    #figure1_gray = figure1.convert('L')
    #figure1_bw = numpy.asarray(figure1_gray).copy()
    #figure2_gray = figure2.convert('L')
    #figure2_bw = numpy.asarray(figure2_gray).copy()
    #
    ## Dark area = 1, Light area = 0
    #figure1_bw[figure1_bw < 128] = 1
    #figure1_bw[figure1_bw >= 128] = 0
    #figure2_bw[figure2_bw < 128] = 1
    #figure2_bw[figure2_bw >= 128] = 0

    difference21 = figure2_bw - figure1_bw
    difference12 = figure1_bw - figure2_bw
    # 0 - 1 = 255 because of rollover.
    difference21[difference21 > 10] = 0
    difference12[difference12 > 10] = 0

    percent_diff = get_percent_diff(difference21, figure2_bw)
    if percent_diff < PERCENT_DIFF_THRESHOLD and \
                    get_percent_diff(
                            numpy.bitwise_and(figure1_bw, figure2_bw),
                            figure1_bw) < PERCENT_DIFF_THRESHOLD:
        return percent_diff
    percent_diff = get_percent_diff(difference12, figure1_bw)
    if percent_diff < PERCENT_DIFF_THRESHOLD and \
                    get_percent_diff(
                            numpy.bitwise_and(figure1_bw, figure2_bw),
                            figure2_bw) < PERCENT_DIFF_THRESHOLD:
        return -percent_diff

    return 0