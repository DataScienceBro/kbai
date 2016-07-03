import numpy
#from matplotlib import pyplot


MSE_SIMILARITY_THRESHOLD = 2000
PERCENT_DIFF_THRESHOLD = 3.25
FILL_RATIO_DIFF_THRESHOLD = 0.25
FILL_RATIO_DIFF_MIN_THRESHOLD = 0.05
LOW_SIMILARITY_THRESHOLD = 0.95
HIGH_SIMILARITY_THRESHOLD = 0.98
HIGH_SIMILARITY_THRESHOLD_3x3 = 0.90
PIXEL_RATIO_THRESHOLD = 0.95
TRANSLATION_THRESHOLD = 0.90


def get_binary_image(image):
        image_map = numpy.array(image, dtype=numpy.uint8)

        for i in xrange(image_map.shape[0]):
            for j in xrange(image_map.shape[1]):
                image_map[i][j] /= 255
        return image_map


# Assumes the two images are the same shape
def get_similarity_ratio(binary_img1, binary_img2):
    rows = binary_img1.shape[0]
    columns = binary_img1.shape[1]

    difference_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            # use float to prevent overflow in case of negatives
            difference_matrix[i][j] = \
                abs(float(binary_img1[i][j]) - float(binary_img2[i][j]))

    difference_ratio = numpy.sum(difference_matrix) / float(rows * columns)
    return 1 - difference_ratio


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
def get_rotation_degrees(binary_image1, binary_image2):
    for k in xrange(4):
        if get_similarity_ratio(numpy.rot90(binary_image1, k), binary_image2) \
                > HIGH_SIMILARITY_THRESHOLD:
            return 90 * k
    return -1


# Rotates figure1 and measures similarity of result against figure2
def rotate_and_score(angle, figure1, figure2):
    k = angle / 90
    return get_similarity_ratio(
        numpy.rot90(figure1, k), figure2
    )


# Returns axis of reflection (x or y) if the images are reflections. Else False.
def get_reflection_axis(binary_image1, binary_image2):
    if get_similarity_ratio(numpy.fliplr(binary_image1), binary_image2) \
            > HIGH_SIMILARITY_THRESHOLD:
        return 'y'
    if get_similarity_ratio(numpy.flipud(binary_image1), binary_image2) \
            > HIGH_SIMILARITY_THRESHOLD:
        return 'x'
    return False


# Reflects figure1 and measures similarity of result against figure2
def reflect_and_score(axis, figure1, figure2):
    if axis == 'y':
        return get_similarity_ratio(
            numpy.fliplr(figure1),
            figure2
        )
    else:
        return get_similarity_ratio(
            numpy.flipud(figure1),
            figure2
        )


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
        get_percent_diff(numpy.bitwise_and(figure1_bw, figure2_bw),
                         figure1_bw) < PERCENT_DIFF_THRESHOLD:
        return percent_diff
    percent_diff = get_percent_diff(difference12, figure1_bw)
    if percent_diff < PERCENT_DIFF_THRESHOLD and \
        get_percent_diff(numpy.bitwise_and(figure1_bw, figure2_bw),
                         figure2_bw) < PERCENT_DIFF_THRESHOLD:
        return -percent_diff

    return 0


def find_difference(figure1, figure2):
    rows = figure1.shape[0]
    columns = figure2.shape[1]

    difference_matrix = numpy.zeros((rows, columns), dtype=float)

    for i in xrange(rows):
        for j in xrange(columns):
            difference_matrix[i][j] = \
                abs(float(figure1[i][j]) - float(figure2[i][j]))
    return difference_matrix


def get_difference_score(difference_matrix, figure1, figure2):
    difference_1_2 = find_difference(figure1, figure2)
    return get_similarity_ratio(difference_matrix, difference_1_2)


def get_pixel_ratio(figure1, figure2):
    sum1 = numpy.sum(figure1)
    sum2 = numpy.sum(figure2)
    return float(sum1) / sum2


def verify_increasing_black_pixels(figure1, figure2):
    sum1 = numpy.sum(figure1)
    sum2 = numpy.sum(figure2)
    return sum1 > sum2


def get_translation_axis(figure1, figure2):
    # Check for horizontal translation
    rows = figure1.shape[0]
    columns = figure1.shape[1]

    figure1_horizontal = numpy.zeros((rows, columns), dtype=float)
    for row_index, row in enumerate(figure1_horizontal):
        for column_index in xrange(columns/2):
            if column_index < columns/2:
                row[column_index], row[column_index + columns/2] = \
                    figure1[row_index][column_index + columns/2], \
                    figure1[row_index][column_index]
    if get_similarity_ratio(figure1_horizontal, figure2) > \
            TRANSLATION_THRESHOLD:
        return 'horizontal'

    figure1_vertical = figure1[len(figure1)/2:] + figure1[:len(figure1)/2]
    #pyplot.plot(figure1_translated)
    if get_similarity_ratio(figure1_vertical, figure2) > \
            TRANSLATION_THRESHOLD:
        return 'vertical'
    return False


def get_translation(figure, axis):
    if axis == 'vertical':
        figure_vertical = figure[len(figure)/2:] + figure[:len(figure)/2]
        return figure_vertical
    else:
        rows = figure.shape[0]
        columns = figure.shape[1]

        figure_horizontal = numpy.zeros((rows, columns), dtype=float)
        for row_index, row in enumerate(figure_horizontal):
            for column_index in xrange(columns/2):
                if column_index < columns/2:
                    row[column_index], row[column_index + columns/2] = \
                        figure[row_index][column_index + columns/2], \
                        figure[row_index][column_index]
        return figure_horizontal