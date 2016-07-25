import numpy
#from matplotlib import pyplot


MSE_SIMILARITY_THRESHOLD = 2000
PERCENT_DIFF_THRESHOLD = 3.25
FILL_RATIO_DIFF_THRESHOLD = 0.25
FILL_RATIO_DIFF_MIN_THRESHOLD = 0.05
LOW_SIMILARITY_THRESHOLD = 0.95
HIGH_SIMILARITY_THRESHOLD = 0.97
HIGH_SIMILARITY_THRESHOLD_3x3 = 0.91
HIGH_SIMILARITY_THRESHOLD_OR = 0.96
HIGH_SIMILARITY_THRESHOLD_XOR = 0.965
HIGH_SIMILARITY_THRESHOLD_TOP_BOTTOM = 0.966
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


def get_3_way_xor(images):
    rows = images[0].shape[0]
    columns = images[0].shape[1]

    xor_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            if (images[0][i][j] == 0 and
                images[1][i][j] == 0 and
                images[2][i][j] == 0) or (
                    images[0][i][j] == 1 and
                    images[1][i][j] == 1 and
                    images[2][i][j] == 1):
                xor_matrix[i][j] = 0
            else:
                xor_matrix[i][j] = 1

    return xor_matrix


def get_pixel_count(image):
    rows = image.shape[0]
    columns = image.shape[1]

    visited = numpy.zeros((rows, columns), dtype=float)
    original_sum = numpy.sum(visited)

    for i in xrange(rows):
        for j in xrange(columns):
            if image[i][j] == 0 and visited[i][j] == 0:
                depth_first_search(image, i, j, visited)
                return abs(original_sum - numpy.sum(visited))
    return -1


def is_safe(image, i, j, visited):
    return i >= 0 and i < image.shape[0] \
        and j >= 0 and j < image.shape[1] \
        and image[i][j] == 0 and visited[i][j] == 0


def depth_first_search(image, i, j, visited):
    row_numbers = [-1, -1, -1, 0, 0, 1, 1, 1]
    column_numbers = [-1, 0, 1, -1, 1, -1, 0, 1]

    visited[i][j] = 1
    for k in xrange(len(row_numbers)):
        if is_safe(image, i + row_numbers[k], j + column_numbers[k], visited):
            depth_first_search(
                image, i + row_numbers[k], j + column_numbers[k], visited)


def get_islands(image):
    rows = image.shape[0]
    columns = image.shape[1]

    visited = numpy.zeros((rows, columns), dtype=float)
    count = 0

    for i in xrange(rows):
        for j in xrange(columns):
            if image[i][j] == 0 and visited[i][j] == 0:
                depth_first_search(image, i, j, visited)
                count += 1
    return count


def check_row_count(image1, image2, image3):
    num_islands = [get_islands(image1), get_islands(image2) , get_islands(image3)]
    num_islands.sort()
    if abs(num_islands[0] - num_islands[1]) == abs(num_islands[1] - num_islands[2]):
        return abs(num_islands[0] - num_islands[1])
    return -1


def get_or(image1, image2):
    rows = image1.shape[0]
    columns = image1.shape[1]

    or_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            if image1[i][j] == 1 and image2[i][j] == 1:
                or_matrix[i][j] = 1
    return or_matrix


def check_or(image1, image2, image3):
    or_matrix = get_or(image1, image2)
    if get_similarity_ratio(or_matrix, image3) > HIGH_SIMILARITY_THRESHOLD_OR:
        return True
    return False


def get_and(image1, image2):
    rows = image1.shape[0]
    columns = image1.shape[1]

    and_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            if image1[i][j] == 1 or image2[i][j] == 1:
                and_matrix[i][j] = 1
    return and_matrix


def check_and(image1, image2, image3):
    and_matrix = get_and(image1, image2)
    if get_similarity_ratio(and_matrix, image3) > HIGH_SIMILARITY_THRESHOLD_3x3:
        return True
    return False


def get_xor(image1, image2):
    rows = image1.shape[0]
    columns = image1.shape[1]

    xor_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            if (image1[i][j] == 1 and image2[i][j] == 1) or \
                    (image1[i][j] == 0 and image2[i][j] == 0):
                xor_matrix[i][j] = 1
            else:
                xor_matrix[i][j] = 0
    return xor_matrix


def check_xor(image1, image2, image3):
    xor_matrix = get_xor(image1, image2)
    if get_similarity_ratio(xor_matrix, image3) > HIGH_SIMILARITY_THRESHOLD_XOR:
        return True
    return False


def get_top_bottom(image1, image2):
    rows = image1.shape[0]
    columns = image1.shape[1]

    top_bottom_matrix = numpy.zeros((rows, columns), dtype=float)
    for i in xrange(rows):
        for j in xrange(columns):
            if i <= rows/2:
                top_bottom_matrix[i][j] = image1[i][j]
            else:
                top_bottom_matrix[i][j] = image2[i][j]

    return top_bottom_matrix


def check_top_bottom_row(image1, image2, image3):
    top_bottom_matrix = get_top_bottom(image1, image2)
    if get_similarity_ratio(top_bottom_matrix, image3) > HIGH_SIMILARITY_THRESHOLD_TOP_BOTTOM:
        return True
    return False


def get_pixel_difference(image1, image2):
    pixels1 = (image1.shape[0] * image1.shape[1]) - int(numpy.sum(image1))
    pixels2 = (image2.shape[0] * image2.shape[1]) - int(numpy.sum(image2))
    return abs(pixels1 - pixels2)


def check_pixel_difference(image1, image2, image3):
    image3_pixels = (image3.shape[0] * image3.shape[1]) - int(numpy.sum(image3))
    image1_2_pixels = get_pixel_difference(image1, image2)
    smaller, bigger = (image1_2_pixels, image3_pixels) if \
        image3_pixels > image1_2_pixels else (image3_pixels, image1_2_pixels)
    if 1 - (float(bigger - smaller) / bigger) > HIGH_SIMILARITY_THRESHOLD:
        return True