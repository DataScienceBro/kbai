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
import numpy
import ImageHelper


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

    def solve2x2(self):

        # If A:B is unchanged, find the option that's the same as 'C'
        print 'Checking for unchanged'
        if ImageHelper.get_similarity_ratio(
                self.input_figures['A'][2],
                self.input_figures['B'][2]) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_similarity_ratio(
                    self.input_figures['C'][2], binary_image
                ) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                    return int(index)

        # If A:C is unchanged, find the option that's the same as 'B'
        if ImageHelper.get_similarity_ratio(
                self.input_figures['A'][2],
                self.input_figures['C'][2]) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_similarity_ratio(
                    self.input_figures['B'][2], binary_image
                ) > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                    return int(index)

        print 'Checking for reflection'
        # If A:B is a reflection, find the option that's the same reflection
        # of 'C'
        axis = ImageHelper.get_reflection_axis(self.input_figures['A'][2],
                                                 self.input_figures['B'][2])

        if axis:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_reflection_axis(
                        self.input_figures['C'][2], binary_image) == axis:
                    return int(index)

        # If A:C is a reflection, find the option that's the same reflection
        # of 'B'
        axis = ImageHelper.get_reflection_axis(self.input_figures['A'][2],
                                                 self.input_figures['C'][2])

        if axis:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_reflection_axis(
                        self.input_figures['B'][2], binary_image) == axis:
                    return int(index)

        print 'Checking for rotation'
        # If A:B is a rotation, find the option that's the same angle
        # rotation of 'C'
        angle = ImageHelper.get_rotation_degrees(self.input_figures['A'][2],
                                                  self.input_figures['B'][2])
        if angle >= 0:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_rotation_degrees(self.input_figures['C'][2],
                                                     binary_image) == angle:
                    return int(index)

        # If A:C is a rotation, find the option that's the same angle
        # rotation of 'B'
        angle = ImageHelper.get_rotation_degrees(self.input_figures['A'][2],
                                                  self.input_figures['C'][2])
        if angle >= 0:
            for index, (option, optionImage, binary_image) in self.options.iteritems():
                if ImageHelper.get_rotation_degrees(self.input_figures['B'][2],
                                                     binary_image) == angle:
                    return int(index)

        print 'Checking for subtraction'
        # Check for: if B = A - x, then D = C - x
        # Find x (x = A - B)
        difference_a_b = ImageHelper.find_difference(self.input_figures['A'][2],
                                                     self.input_figures['B'][2])
        for index, (option, optionImage, binary_image) in self.options.iteritems():
            difference_c_option = ImageHelper.find_difference(self.input_figures['C'][2],
                                                              binary_image)
            if ImageHelper.get_similarity_ratio(
                    difference_a_b, difference_c_option) \
                    > ImageHelper.LOW_SIMILARITY_THRESHOLD:
                return int(index)

        # Check for: if C = A - x, then D = B - x
        difference_a_c = ImageHelper.find_difference(self.input_figures['A'][2],
                                                     self.input_figures['C'][2])
        for index, (option, optionImage, binary_image) in self.options.iteritems():
            difference_b_option = ImageHelper.find_difference(self.input_figures['B'][2],
                                                              binary_image)
            if ImageHelper.get_similarity_ratio(
                    difference_a_c, difference_b_option) \
                    > ImageHelper.HIGH_SIMILARITY_THRESHOLD:
                return int(index)

        print 'Checking for fill:unfilled'
        # Check if A:B or A:C is filled:unfilled or vice versa
        best_ratio = None
        best_option_index = None
        best_option_image = None
        bw_ratio_AB = ImageHelper.get_black_white_ratio(self.input_figures['A'][1],
                                                     self.input_figures['B'][1])
        bw_ratio_AC = ImageHelper.get_black_white_ratio(self.input_figures['A'][1],
                                                     self.input_figures['C'][1])
        for index, (option, optionImage, binary_image) in self.options.iteritems():
            current_ratio = ImageHelper.get_black_white_ratio(
                self.input_figures['C'][1], optionImage)
            if not best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_AB)
                best_option_index = index
                best_option_image = optionImage
            if abs(current_ratio - bw_ratio_AB) < best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_AB)
                best_option_index = index
                best_option_image = optionImage
            current_ratio = ImageHelper.get_black_white_ratio(
                self.input_figures['B'][1], optionImage)
            if abs(current_ratio - bw_ratio_AC) < best_ratio:
                best_ratio = abs(current_ratio - bw_ratio_AC)
                best_option_index = index
                best_option_image = optionImage

        # Do a sanity check on answer
        if best_ratio < ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
            ratioAB = ImageHelper.get_black_white_ratio(self.input_figures['C'][1], best_option_image)
            ratioAC = ImageHelper.get_black_white_ratio(self.input_figures['B'][1], best_option_image)

            if abs(ratioAB - bw_ratio_AB) > \
                    ImageHelper.FILL_RATIO_DIFF_THRESHOLD and \
                            abs(ratioAC - bw_ratio_AC) > \
                            ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
                return -1

            if abs(ratioAB - bw_ratio_AB) < \
                    ImageHelper.FILL_RATIO_DIFF_MIN_THRESHOLD or \
                            abs(ratioAC - bw_ratio_AC) < \
                            ImageHelper.FILL_RATIO_DIFF_MIN_THRESHOLD:
                return int(best_option_index)
            #if abs(ratioAB - bw_ratio_AB) > ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
            #    return -1
            #if abs(ratioAC - bw_ratio_AC) > ImageHelper.FILL_RATIO_DIFF_THRESHOLD:
            #    return -1
            return int(best_option_index)

        return -1

    def solve3x3(self):
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
        else:
            answer = self.solve3x3()
        print problem.name, answer
        return answer