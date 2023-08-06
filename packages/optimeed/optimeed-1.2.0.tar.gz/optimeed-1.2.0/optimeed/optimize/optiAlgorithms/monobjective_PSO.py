from .pyswarm import MyMapEvaluator, MyMultiprocessEvaluator, pso

from optimeed.core.tools import indentParagraph  # isNonePrintMessage, printIfShown, SHOW_ERROR, SHOW_WARNING
from .algorithmInterface import AlgorithmInterface
from optimeed.core import Option_class
from optimeed.optimize.optiAlgorithms.convergence.evolutionaryConvergence import EvolutionaryConvergence


class Monobjective_PSO(AlgorithmInterface, Option_class):
    NUMBER_OF_CORES = 1

    def __init__(self):
        super().__init__()
        self.maxTime = None  # set by set_maxtime
        self.callback_on_evaluation = None  # set by set_evaluationFunction
        self.evaluationFunction = None  # set by set_evaluationFunction
        self.add_option(self.NUMBER_OF_CORES, "Number of cores", 1)
        self.theConvergence = EvolutionaryConvergence(is_monobj=True)

    def compute(self, initialVectorGuess, listOfOptimizationVariables):
        nbr_cores = self.get_optionValue(self.NUMBER_OF_CORES)
        # Set the evaluator
        if nbr_cores == 1:
            theEvaluator = MyMapEvaluator(self.evaluationFunction, self.callback_on_evaluation)
        else:
            theEvaluator = MyMultiprocessEvaluator(self.evaluationFunction, self.callback_on_evaluation, nbr_cores)

        # Get lower bounds and upper bounds
        lb = [optiVariable.get_min_value() for optiVariable in listOfOptimizationVariables]
        ub = [optiVariable.get_max_value() for optiVariable in listOfOptimizationVariables]

        # Run the optimization algorithm
        kwargs = dict()
        optimal_parameters, _function_value, is_feasible = pso(lb, ub, initialVectorGuess, theEvaluator, self.maxTime,
                                                               callback_generation=self.theConvergence.set_points_at_step,
                                                               **kwargs)
        return [optimal_parameters]

    def set_evaluationFunction(self, evaluationFunction, callback_on_evaluate, numberOfObjectives, _numberOfConstraints):
        if numberOfObjectives > 1:
            ValueError("Optimization algorithm does not support true multiobjective.")

        self.evaluationFunction = evaluationFunction
        self.callback_on_evaluation = callback_on_evaluate

    def set_maxtime(self, maxTime):
        self.maxTime = maxTime

    def __str__(self):
        theStr = ''
        theStr += "Custom PSO\n"
        theStr += indentParagraph(str(self.Options), indent_level=1)
        return theStr

    def get_convergence(self):
        return self.theConvergence
