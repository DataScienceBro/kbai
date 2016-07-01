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
            figure_image = Image.open(figure.visualFilename)
            if name.isdigit():
                self.options[name] = (figure, figure_image)
            else:
                self.input_figures[name] = (figure, figure_image)

    def solve2x2(self):

        # If A:B is unchanged, find the option that's the same as 'C'
        if ImageHelper.get_mse(
                self.input_figures['A'][1], self.input_figures['B'][1]) \
                < ImageHelper.MSE_SIMILARITY_THRESHOLD:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_mse(
                        self.input_figures['C'][1], optionImage) \
                        < ImageHelper.MSE_SIMILARITY_THRESHOLD:
                    return int(index)

        # If A:C is unchanged, find the option that's the same as 'B'
        if ImageHelper.get_mse(
                self.input_figures['A'][1], self.input_figures['C'][1]) \
                < ImageHelper.MSE_SIMILARITY_THRESHOLD:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_mse(
                        self.input_figures['B'][1], optionImage) \
                        < ImageHelper.MSE_SIMILARITY_THRESHOLD:
                    return int(index)

        # If A:B is a reflection, find the option that's the same reflection
        # of 'C'
        axis = ImageHelper.get_reflection_axis(self.input_figures['A'][1],
                                               self.input_figures['B'][1])
        if axis:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_reflection_axis(self.input_figures['C'][1],
                                                   optionImage) == axis:
                    #print 'Found using reflection'
                    return int(index)

        # If A:C is a reflection, find the option that's the same reflection
        # of 'B'
        axis = ImageHelper.get_reflection_axis(self.input_figures['A'][1],
                                               self.input_figures['C'][1])
        if axis:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_reflection_axis(self.input_figures['B'][1],
                                                   optionImage) == axis:
                    return int(index)

        # If A:B is a rotation, find the option that's the same angle
        # rotation of 'C'
        angle = ImageHelper.get_rotation_degrees(self.input_figures['A'][1],
                                                 self.input_figures['B'][1])
        if angle >= 0:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_rotation_degrees(self.input_figures['C'][1],
                                                    optionImage) == angle:
                    return int(index)

        # If A:C is a rotation, find the option that's the same angle
        # rotation of 'B'
        angle = ImageHelper.get_rotation_degrees(self.input_figures['A'][1],
                                                 self.input_figures['C'][1])
        if angle >= 0:
            for index, (option, optionImage) in self.options.iteritems():
                if ImageHelper.get_rotation_degrees(self.input_figures['B'][1],
                                                    optionImage) == angle:
                    return int(index)

        # If A:B has a fill's complement relationship, find the fill's
        # complement of C
        #fills_complement = ImageHelper.check_fills_complement(
        #    self.input_figures['A'][1], self.input_figures['B'][1])
        #if fills_complement != 0:
        #    best_option = None
        #    lowest_difference = float("inf")
        #    for index, (option, optionImage) in self.options.iteritems():
        #        current_complement = ImageHelper.check_fills_complement(
        #            self.input_figures['C'][1], optionImage)
        #        if abs(current_complement - fills_complement) < lowest_difference:
        #            lowest_difference = abs(current_complement - fills_complement)
        #            best_option = index
        #    if best_option:
        #        return int(best_option)

        best_ratio = None
        best_option_index = None
        best_option_image = None
        bw_ratio_AB = ImageHelper.get_black_white_ratio(self.input_figures['A'][1],
                                                     self.input_figures['B'][1])
        bw_ratio_AC = ImageHelper.get_black_white_ratio(self.input_figures['A'][1],
                                                     self.input_figures['C'][1])
        for index, (option, optionImage) in self.options.iteritems():
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