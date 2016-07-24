# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
import ImageHelper
import numpy
#from matplotlib import pyplot


AGENT_ANSWER_THRESHOLD = 0


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.input_figures = {}
        self.options = {}
        pass

    def store_inputs(self, problem):
        for name, figure in problem.figures.iteritems():
            figure_image = Image.open(figure.visualFilename).convert("L")
            binary_image = ImageHelper.get_binary_image(figure_image)
            if name.isdigit():
                self.options[name] = (figure, figure_image, binary_image)
            else:
                self.input_figures[name] = (figure, figure_image, binary_image)

    def check_unchanged2x2(self, image1, image2, image3):
        """
        Verifies whether image1:image2 are similar or not.
        If so, returns image in options that is most similar to image3.
        Else returns -1
        """
        if ImageHelper.get_similarity_ratio(
                image1, image2) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            max_option_index = None
            max_option_score = 0
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(
                    image3, binary_image
                )
                if not max_option_score or option_score > max_option_score:
                    max_option_index = index
                    max_option_score = option_score
            if max_option_score > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                return int(max_option_index)
        return -1

    def check_reflection(self, image1, image2, image3):
        """
        Verifies whether image1:image2 are reflections or not.
        If so, returns image in options that is a reflection of image3.
        Else returns -1
        """
        axis = ImageHelper.get_reflection_axis(image1, image2)

        if axis:
            max_option_index = None
            max_option_score = 0
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.reflect_and_score(
                    axis, image3, binary_image)

                if not max_option_score or option_score > max_option_score:
                    max_option_index = index
                    max_option_score = option_score

            if max_option_score > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                return int(max_option_index)
        return -1

    def check_rotation(self, image1, image2, image3):
        """
        Verifies whether image1:image2 are rotations or not.
        If so, returns image in options that is a similar rotation of image3.
        Else returns -1
        """
        angle = ImageHelper.get_rotation_degrees(image1, image2)
        if angle >= 0:
            max_option_index = None
            max_option_score = 0
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.rotate_and_score(
                    angle, image3, binary_image)
                if not max_option_score or option_score > max_option_score:
                    max_option_index = index
                    max_option_score = option_score
            if max_option_score > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                return int(max_option_index)
        return -1

    def check_subtraction(self, image1, image2, image3):
        """
        Verifies whether image1:image2 are different by a constant difference
        or not.
        If so, returns image in options that is different from image3 by the
        same constant difference.
        Else returns -1
        """
        difference_a_b = ImageHelper.find_difference(image1, image2)
        max_subtraction_score = None
        max_subtraction_index = -1
        for index, (option, optionImage, binary_image) in \
                self.options.iteritems():
            subtraction_score = ImageHelper.get_difference_score(
                difference_a_b, image3, binary_image)
            if not max_subtraction_score or subtraction_score > \
                    max_subtraction_score:
                max_subtraction_score = subtraction_score
                max_subtraction_index = index
        if max_subtraction_score > ImageHelper.LOW_SIMILARITY_THRESHOLD:
            return int(max_subtraction_index)
        return -1

    def solve2x2(self):

        # If A:B is unchanged, find the option that's the same as 'C'
        #print 'Checking for unchanged'
        unchanged_a_b_index = self.check_unchanged2x2(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2])
        if unchanged_a_b_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_a_b_index

        unchanged_a_c_index = self.check_unchanged2x2(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['B'][2])
        if unchanged_a_b_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_a_c_index

        #print 'Checking for reflection'
        # If A:B is a reflection, find the option that's the same reflection
        # of 'C'
        reflection_a_b_index = self.check_reflection(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2]
        )
        if reflection_a_b_index > AGENT_ANSWER_THRESHOLD:
            return reflection_a_b_index

        reflection_a_c_index = self.check_reflection(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['B'][2]
        )
        if reflection_a_c_index > AGENT_ANSWER_THRESHOLD:
            return reflection_a_c_index

        #print 'Checking for rotation'
        # If A:B is a rotation, find the option that's the same angle
        # rotation of 'C'
        rotation_a_b_index = self.check_rotation(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2]
        )
        if rotation_a_b_index > AGENT_ANSWER_THRESHOLD:
            return rotation_a_b_index

        rotation_a_c_index = self.check_rotation(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['B'][2]
        )
        if rotation_a_c_index > AGENT_ANSWER_THRESHOLD:
            return rotation_a_c_index

        #print 'Checking for subtraction'
        # Check for: if B = A - x, then D = C - x
        # Find x (x = A - B)
        subtraction_a_b_index = self.check_subtraction(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2]
        )
        if subtraction_a_b_index > AGENT_ANSWER_THRESHOLD:
            return subtraction_a_b_index

        subtraction_a_c_index = self.check_subtraction(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['B'][2]
        )
        if subtraction_a_c_index > AGENT_ANSWER_THRESHOLD:
            return subtraction_a_c_index

        #print 'Checking for fill:unfilled'
        # Check if A:B or A:C is filled:unfilled or vice versa
        best_ratio = None
        best_option_index = None
        best_option_image = None
        bw_ratio_ab = ImageHelper.get_black_white_ratio(
            self.input_figures['A'][1], self.input_figures['B'][1])
        bw_ratio_ac = ImageHelper.get_black_white_ratio(
            self.input_figures['A'][1], self.input_figures['C'][1])
        for index, (option, optionImage, binary_image) in \
                self.options.iteritems():
            current_ratio = ImageHelper.get_black_white_ratio(
                self.input_figures['C'][1], optionImage)
            if not best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_ab)
                best_option_index = index
                best_option_image = optionImage
            if abs(current_ratio - bw_ratio_ab) < best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_ab)
                best_option_index = index
                best_option_image = optionImage
            current_ratio = ImageHelper.get_black_white_ratio(
                self.input_figures['B'][1], optionImage)
            if abs(current_ratio - bw_ratio_ac) < best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_ac)
                best_option_index = index
                best_option_image = optionImage

        # Do a sanity check on answer
        if best_ratio < ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
            ratio_a_b = \
                ImageHelper.get_black_white_ratio(self.input_figures['C'][1],
                                                  best_option_image)
            ratio_a_c = \
                ImageHelper.get_black_white_ratio(self.input_figures['B'][1],
                                                  best_option_image)

            if abs(ratio_a_b - bw_ratio_ab) > \
                    ImageHelper.FILL_RATIO_DIFF_THRESHOLD and \
                    abs(ratio_a_c - bw_ratio_ac) > \
                    ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
                return -1

            if abs(ratio_a_b - bw_ratio_ab) < \
                    ImageHelper.FILL_RATIO_DIFF_MIN_THRESHOLD or \
                    abs(ratio_a_c - bw_ratio_ac) < \
                    ImageHelper.FILL_RATIO_DIFF_MIN_THRESHOLD:
                return int(best_option_index)
            return int(best_option_index)

        return -1

    def check_unchanged3x3(self, image1, image2, image3, image4):
        """
        Verifies whether image1:image2:image3 are similar or not
        If so, returns image in options that is most similar to image4
        Else return -1
        """
        if ImageHelper.get_similarity_ratio(
            image1, image2
        ) > ImageHelper.HIGH_SIMILARITY_THRESHOLD and \
                ImageHelper.get_similarity_ratio(image2, image3) > \
                ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            max_option_index = None
            max_option_score = 0
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(
                    image4, binary_image
                )
                if not max_option_score or option_score > max_option_score:
                    max_option_index = index
                    max_option_score = option_score
            if max_option_score > ImageHelper.HIGH_SIMILARITY_THRESHOLD_3x3:
                return int(max_option_index)
        return -1

    def check_unchangeddiag(self, image1, image2):
        """
        Verifies whether image1:image2 are similar or not
        If so, returns image in options that is most similar to image2
        Else return -1
        """
        if ImageHelper.get_similarity_ratio(
            image1, image2
        ) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            max_option_index = None
            max_option_score = 0
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(
                    image2, binary_image
                )
                if not max_option_score or option_score > max_option_score:
                    max_option_index = index
                    max_option_score = option_score
            if max_option_score > ImageHelper.HIGH_SIMILARITY_THRESHOLD_3x3:
                return int(max_option_index)
        return -1


    def check_pixel_ratio3x3(self, image1, image2, image3, image4, image5):
        pixel_ratio12 = ImageHelper.get_pixel_ratio(image1, image2)
        pixel_ratio23 = ImageHelper.get_pixel_ratio(image2, image3)
        pixel_ratio_similarity = \
            float(min(pixel_ratio12, pixel_ratio23)) / max(
                pixel_ratio12, pixel_ratio23)
        if pixel_ratio_similarity > ImageHelper.PIXEL_RATIO_THRESHOLD:
            # number of pixels increase consistently
            pixel_ratio45 = ImageHelper.get_pixel_ratio(image4, image5)
            best_pixel_score = None
            best_pixel_index = -1
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                pixel_ratio5 = ImageHelper.get_pixel_ratio(image5, binary_image)
                pixel_ratio_score = float(min(pixel_ratio5, pixel_ratio45)) / \
                    max(pixel_ratio45, pixel_ratio5)
                if not best_pixel_score or pixel_ratio_score > best_pixel_score:
                    best_pixel_score = pixel_ratio_score
                    best_pixel_index = index
            if best_pixel_score > ImageHelper.PIXEL_RATIO_THRESHOLD:
                return int(best_pixel_index)
        return -1

    def check_pixel_ratio3x3_rxc(self, image1, image2, image3, image4):
        pixel_ratio12 = ImageHelper.get_pixel_ratio(image1, image2)
        pixel_ratio34 = ImageHelper.get_pixel_ratio(image3, image4)
        pixel_ratio_similarity = \
            float(min(pixel_ratio12, pixel_ratio34)) / max(
                pixel_ratio12, pixel_ratio34)
        if pixel_ratio_similarity > ImageHelper.PIXEL_RATIO_THRESHOLD:
            # number of pixels increase consistently
            best_pixel_score = None
            best_pixel_index = -1
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                pixel_ratio5 = ImageHelper.get_pixel_ratio(image4, binary_image)
                pixel_ratio_score = float(min(pixel_ratio5, pixel_ratio12)) / \
                    max(pixel_ratio12, pixel_ratio5)
                if not best_pixel_score or pixel_ratio_score > best_pixel_score:
                    best_pixel_score = pixel_ratio_score
                    best_pixel_index = index
            if best_pixel_score > ImageHelper.PIXEL_RATIO_THRESHOLD:
                return int(best_pixel_index)
        return -1

    def check_pixel_ratio3x3_diag(self, image1, image2):
        pixel_ratio12 = ImageHelper.get_pixel_ratio(image1, image2)
        best_pixel_score_diff = None
        best_pixel_index = -1
        for index, (option, optionImage, binary_image) in \
                self.options.iteritems():
            pixel_ratio_diag = ImageHelper.get_pixel_ratio(image2, binary_image)
            pixel_ratio_similarity = \
                float(min(pixel_ratio_diag, pixel_ratio12)) / \
                max(pixel_ratio12, pixel_ratio_diag)
            # Pixel ratio should be as close to 1 as possible
            if not best_pixel_score_diff or pixel_ratio_similarity > best_pixel_score_diff:
                best_pixel_score_diff = pixel_ratio_similarity
                best_pixel_index = index
        return int(best_pixel_index)

    def check_increasing_black_pixels_rxc(self, image1, image2, image3, image4):
        if (ImageHelper.verify_increasing_black_pixels(image1, image2) and
                ImageHelper.verify_increasing_black_pixels(image3, image4)):
            options = []
            black_pixel_sum2 = numpy.sum(image2)
            black_pixel_sum4 = numpy.sum(image4)
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                black_pixel_sum = numpy.sum(binary_image)
                if black_pixel_sum < black_pixel_sum2 and \
                        black_pixel_sum < black_pixel_sum4:
                    options.append(index)
            if len(options) == 1:
                return int(options[0])
        return -1

    def check_increasing_black_pixels(self, image1, image2, image3, image4,
                                      image5):
        if (ImageHelper.verify_increasing_black_pixels(image1, image2) and
                ImageHelper.verify_increasing_black_pixels(image2, image3) and
                ImageHelper.verify_increasing_black_pixels(image4, image5)):
            options = []
            black_pixel_sum2 = numpy.sum(image2)
            black_pixel_sum5 = numpy.sum(image5)
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                black_pixel_sum = numpy.sum(binary_image)
                if black_pixel_sum < black_pixel_sum2 and \
                        black_pixel_sum < black_pixel_sum5:
                    options.append(index)
            if len(options) == 1:
                return int(options[0])
        return -1

    def check_translation(self, image1, image2, image3, image4, image5):
        axis1 = ImageHelper.get_translation_axis(image1, image2)
        axis2 = ImageHelper.get_translation_axis(image3, image4)
        if axis1 and axis1 == axis2:
            best_translation_score = None
            best_translation_index = -1
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                translated_option = ImageHelper.get_translation(binary_image,
                                                                axis1)
                translated_score = ImageHelper.get_similarity_ratio(
                    image5, translated_option)
                if not best_translation_score or translated_score > \
                        best_translation_score:
                    best_translation_score = translated_score
                    best_translation_index = index
            if best_translation_score >= ImageHelper.TRANSLATION_THRESHOLD:
                return int(best_translation_index)
        return -1

    def check_3_way_xor(self, row1, row2, row3):
        row1_result = ImageHelper.get_3_way_xor(row1)
        row2_result = ImageHelper.get_3_way_xor(row2)

        if ImageHelper.get_similarity_ratio(row1_result, row2_result) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            best_3_way_xor_score = None
            best_3_way_xor_index = -1
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                row3_result = ImageHelper.get_3_way_xor(row3 + [binary_image])
                option_score = ImageHelper.get_similarity_ratio(row3_result, row2_result)
                if not best_3_way_xor_score or option_score > best_3_way_xor_score:
                    best_3_way_xor_score = option_score
                    best_3_way_xor_index = index
            if best_3_way_xor_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_3_way_xor_index)
        return -1

    def eliminate_options_in_question(self):
        possible_options = ['1', '2', '3', '4', '5', '6', '7', '8']
        possible_inputs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for index, (option, optionImage, binary_image) in \
                self.options.iteritems():
            for letter in possible_inputs:
                if ImageHelper.get_similarity_ratio(binary_image, self.input_figures[letter][2]) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                    possible_options.remove(index)
                    possible_inputs.remove(letter)
                    break
            #if binary_image in self.input_figures:
            #    possible_options.remove(index)
        if len(possible_options) == 1:
            return int(possible_options[0])

    def check_row_or(self, row1, row2, row3):
        if ImageHelper.check_or(row1[0], row1[1], row1[2]) or ImageHelper.check_or(row2[0], row2[1], row2[2]):
            # Find best option for row3
            best_or_score = None
            best_or_index = -1
            or_matrix = ImageHelper.get_or(row3[0], row3[1])
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(binary_image, or_matrix)
                if not best_or_score or option_score > best_or_score:
                    best_or_score = option_score
                    best_or_index = index
            if best_or_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_or_index)
        return -1

    def check_pixel_difference(self, row1, row2, row3):
        if ImageHelper.check_pixel_difference(row1[0], row1[1], row1[2]) and ImageHelper.check_pixel_difference(row2[0], row2[1], row2[2]):
            best_pixel_diff_score = None
            best_pixel_diff_index = -1
            pixel_diff = ImageHelper.get_pixel_difference(row3[0], row3[1])
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_pixels = (binary_image.shape[0] * binary_image.shape[1]) - numpy.sum(binary_image)
                smaller, bigger = (pixel_diff, option_pixels) if option_pixels > pixel_diff else (option_pixels, pixel_diff)
                option_score = 1 - (float(bigger - smaller) / bigger)
                if not best_pixel_diff_score or option_score >= best_pixel_diff_score:
                    best_pixel_diff_score = option_score
                    best_pixel_diff_index = index
            if best_pixel_diff_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_pixel_diff_index)
        return -1

    def check_row_and(self, row1, row2, row3):
        if ImageHelper.check_and(row1[0], row1[1], row1[2]) and ImageHelper.check_and(row2[0], row2[1], row2[2]):
            # Find best option for row3
            best_and_score = None
            best_and_index = -1
            and_matrix = ImageHelper.get_and(row3[0], row3[1])
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(binary_image, and_matrix)
                if not best_and_score or option_score > best_and_score:
                    best_and_score = option_score
                    best_and_index = index
            if best_and_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_and_index)
        return -1

    def check_xor(self, row1, row2, row3):
        if ImageHelper.check_xor(row1[0], row1[1], row1[2]) and ImageHelper.check_xor(row2[0], row2[1], row2[2]):
            best_xor_score = None
            best_xor_index = -1
            xor_matrix = ImageHelper.get_xor(row3[0], row3[1])
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(binary_image, xor_matrix)
                if not best_xor_score or option_score > best_xor_score:
                    best_xor_score = option_score
                    best_xor_index = index
            if best_xor_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_xor_index)
        return -1

    def check_top_bottom(self, row1, row2, row3):
        if ImageHelper.check_top_bottom_row(row1[0], row1[1], row1[2]) and ImageHelper.check_top_bottom_row(row2[0], row2[1], row2[2]):
            best_top_bottom_score = None
            best_top_bottom_index = -1
            top_bottom_matrix = ImageHelper.get_top_bottom(row3[0], row3[1])
            for index, (option, optionImage, binary_image) in \
                    self.options.iteritems():
                option_score = ImageHelper.get_similarity_ratio(binary_image, top_bottom_matrix)
                if not best_top_bottom_score or option_score > best_top_bottom_score:
                    best_top_bottom_score = option_score
                    best_top_bottom_index = index
            if best_top_bottom_score >= ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(best_top_bottom_index)
        return -1

    def solve3x3(self):

        # Check for any row or column being unchanged
        #print 'Checking unchanged'
        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2],
            self.input_figures['H'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_horizontal_index

        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['D'][2],
            self.input_figures['E'][2],
            self.input_figures['F'][2],
            self.input_figures['H'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_horizontal_index

        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['D'][2],
            self.input_figures['F'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_horizontal_index

        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['B'][2],
            self.input_figures['E'][2],
            self.input_figures['H'][2],
            self.input_figures['F'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            return unchanged_horizontal_index

        # Check for reflections
        #print 'Checking reflections'
        reflection_index = self.check_reflection(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['G'][2]
        )
        if reflection_index > AGENT_ANSWER_THRESHOLD:
            return reflection_index

        reflection_index = self.check_reflection(
            self.input_figures['A'][2],
            self.input_figures['G'][2],
            self.input_figures['C'][2]
        )
        if reflection_index > AGENT_ANSWER_THRESHOLD:
            return reflection_index

        # Check for increasing black pixels
        # If C > F and G > H, then I has to be of higher pixels than F and H
        #print 'Check increasing pixels'
        pixels_increasing_index = self.check_increasing_black_pixels_rxc(
            self.input_figures['C'][2],
            self.input_figures['F'][2],
            self.input_figures['G'][2],
            self.input_figures['H'][2]
        )
        if pixels_increasing_index > AGENT_ANSWER_THRESHOLD:
            return pixels_increasing_index

        pixels_increasing_index = self.check_increasing_black_pixels(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2],
            self.input_figures['G'][2],
            self.input_figures['H'][2]
        )
        if pixels_increasing_index > AGENT_ANSWER_THRESHOLD:
            return pixels_increasing_index

        pixels_increasing_index = self.check_increasing_black_pixels(
            self.input_figures['A'][2],
            self.input_figures['D'][2],
            self.input_figures['G'][2],
            self.input_figures['C'][2],
            self.input_figures['H'][2]
        )
        if pixels_increasing_index > AGENT_ANSWER_THRESHOLD:
            return pixels_increasing_index

        # Check for translation
        #print 'Checking for translation'
        translation_index = self.check_translation(
            self.input_figures['A'][2],
            self.input_figures['C'][2],
            self.input_figures['D'][2],
            self.input_figures['F'][2],
            self.input_figures['G'][2]
        )
        if translation_index > AGENT_ANSWER_THRESHOLD:
            return translation_index

        #translation_index = self.check_translation(
        #    self.input_figures['D'][2],
        #    self.input_figures['F'][2],
        #    self.input_figures['G'][2]
        #)
        #if translation_index > AGENT_ANSWER_THRESHOLD:
        #    return translation_index

        translation_index = self.check_translation(
            self.input_figures['A'][2],
            self.input_figures['G'][2],
            self.input_figures['B'][2],
            self.input_figures['H'][2],
            self.input_figures['C'][2]
        )
        if translation_index > AGENT_ANSWER_THRESHOLD:
            return translation_index

        # Check for pixel ratios
        #print 'Checking pixel ratios'
        pixel_ratio_index = self.check_pixel_ratio3x3_rxc(
            self.input_figures['C'][2],
            self.input_figures['F'][2],
            self.input_figures['G'][2],
            self.input_figures['H'][2]
        )
        if pixel_ratio_index > AGENT_ANSWER_THRESHOLD:
            return pixel_ratio_index

        #print 'Checking pixel ratio 3x3'
        pixel_ratio_index = self.check_pixel_ratio3x3(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2],
            self.input_figures['G'][2],
            self.input_figures['H'][2]
        )
        if pixel_ratio_index > AGENT_ANSWER_THRESHOLD:
            return pixel_ratio_index

        #print 'Checking pixel ratio diag'
        pixel_ratio_index = self.check_pixel_ratio3x3_diag(
            self.input_figures['A'][2],
            self.input_figures['E'][2],
        )
        if pixel_ratio_index > AGENT_ANSWER_THRESHOLD:
            return pixel_ratio_index

        return -1

    def solve3x3D(self):
        # Check for any row or column being unchanged
        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['A'][2],
            self.input_figures['B'][2],
            self.input_figures['C'][2],
            self.input_figures['H'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            #print 'Items on each row are equal'
            return unchanged_horizontal_index

        unchanged_horizontal_index = self.check_unchanged3x3(
            self.input_figures['D'][2],
            self.input_figures['E'][2],
            self.input_figures['F'][2],
            self.input_figures['H'][2]
        )
        if unchanged_horizontal_index > AGENT_ANSWER_THRESHOLD:
            #print 'Items on each row are equal'
            return unchanged_horizontal_index

        unchanged_diagonal_index = self.check_unchangeddiag(
            self.input_figures['A'][2],
            self.input_figures['E'][2]
        )
        if unchanged_diagonal_index > AGENT_ANSWER_THRESHOLD:
            #print 'Items on diagonal are equal'
            return unchanged_diagonal_index

        # Check for 3 way XOR
        #print 'Checking 3 way XOR'
        xor_index = self.check_3_way_xor(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]]
        )
        if xor_index > AGENT_ANSWER_THRESHOLD:
            #print 'Ternary XOR on each row is same'
            return xor_index

        # Check for 3 way XOR, but with diagonals
        xor_index = self.check_3_way_xor(
            [self.input_figures['B'][2],
             self.input_figures['F'][2],
             self.input_figures['G'][2]],
            [self.input_figures['C'][2],
             self.input_figures['D'][2],
             self.input_figures['H'][2]],
            [self.input_figures['A'][2],
             self.input_figures['E'][2]]
        )
        if xor_index > AGENT_ANSWER_THRESHOLD:
            #print 'Ternary XOR on diagonals is same'
            return xor_index

        # Check for 3 way XOR, but with diagonals (other side)
        xor_index = self.check_3_way_xor(
            [self.input_figures['C'][2],
             self.input_figures['E'][2],
             self.input_figures['G'][2]],
            [self.input_figures['A'][2],
             self.input_figures['F'][2],
             self.input_figures['H'][2]],
            [self.input_figures['B'][2],
             self.input_figures['D'][2]]
        )
        if xor_index > AGENT_ANSWER_THRESHOLD:
            #print 'Ternary XOR on other diagonals is same'
            return xor_index

        # If an option is an image in the question, we might be able to discard
        # it
        elimination_index = self.eliminate_options_in_question()
        if elimination_index > AGENT_ANSWER_THRESHOLD:
            #print 'Process of elimination worked'
            return elimination_index
        return -1

    def solve3x3E(self):

        # Check if pixels(A) - pixels(B) = pixels(C)
        pixel_difference_index = self.check_pixel_difference(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]]
        )
        if pixel_difference_index > AGENT_ANSWER_THRESHOLD:
            #print '784'
            return pixel_difference_index

        top_bottom_index = self.check_top_bottom(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]]
        )
        if top_bottom_index > AGENT_ANSWER_THRESHOLD:
            #print '813'
            return top_bottom_index

        # Check if A or B == C and D or E == F
        row_or_index = self.check_row_or(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]])
        if row_or_index > AGENT_ANSWER_THRESHOLD:
            #print '798'
            return row_or_index

        # Check if top of first + bottom of second == third

        top_bottom_index = self.check_top_bottom(
            [self.input_figures['B'][2],
             self.input_figures['A'][2],
             self.input_figures['C'][2]],
            [self.input_figures['E'][2],
             self.input_figures['D'][2],
             self.input_figures['F'][2]],
            [self.input_figures['H'][2],
             self.input_figures['G'][2]]
        )
        if top_bottom_index > AGENT_ANSWER_THRESHOLD:
            #print '827'
            return top_bottom_index

        top_bottom_index = self.check_top_bottom(
            [self.input_figures['A'][2],
             self.input_figures['D'][2],
             self.input_figures['G'][2]],
            [self.input_figures['B'][2],
             self.input_figures['E'][2],
             self.input_figures['H'][2]],
            [self.input_figures['C'][2],
             self.input_figures['F'][2]]
        )
        if top_bottom_index > AGENT_ANSWER_THRESHOLD:
            #print '841'
            return top_bottom_index

        top_bottom_index = self.check_top_bottom(
            [self.input_figures['D'][2],
             self.input_figures['A'][2],
             self.input_figures['G'][2]],
            [self.input_figures['E'][2],
             self.input_figures['B'][2],
             self.input_figures['H'][2]],
            [self.input_figures['F'][2],
             self.input_figures['C'][2]]
        )
        if top_bottom_index > AGENT_ANSWER_THRESHOLD:
            #print '855'
            return top_bottom_index

        # Check if A and B == C and D and E == F
        row_and_index = self.check_row_and(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]])
        if row_and_index > AGENT_ANSWER_THRESHOLD:
            #print '869'
            return row_and_index

        # Check if xor of first two elements == last element
        xor_index = self.check_xor(
            [self.input_figures['A'][2],
             self.input_figures['D'][2],
             self.input_figures['G'][2]],
            [self.input_figures['B'][2],
             self.input_figures['E'][2],
             self.input_figures['H'][2]],
            [self.input_figures['C'][2],
             self.input_figures['F'][2]])
        if xor_index > AGENT_ANSWER_THRESHOLD:
            #print '883'
            return xor_index

        xor_index = self.check_xor(
            [self.input_figures['A'][2],
             self.input_figures['B'][2],
             self.input_figures['C'][2]],
            [self.input_figures['D'][2],
             self.input_figures['E'][2],
             self.input_figures['F'][2]],
            [self.input_figures['G'][2],
             self.input_figures['H'][2]])
        if xor_index > AGENT_ANSWER_THRESHOLD:
            #print '896'
            return xor_index

        return -1

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):

        # Separate inputs from options
        self.store_inputs(problem)

        if problem.problemType == '2x2':
            answer = self.solve2x2()
        elif 'Problems D' in problem.problemSetName:
            answer = self.solve3x3D()
        elif 'Problems E' in problem.problemSetName:
            answer = self.solve3x3E()
        else:
            answer = self.solve3x3()
        print problem.name, answer
        return answer