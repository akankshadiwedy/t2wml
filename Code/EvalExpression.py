class EvalExpression:
    def __init__(self) -> None:
        self.value_expression = None
        self.symbol = None
        self.string_expression = None
        self.variables = None


    def get_variable_cell_operator_arguments(self) -> set:
        self.variables = set()
        if self.value_expression:
            self.variables = self.value_expression.get_variable_cell_operator_arguments()
            return self.variables


    def evaluate(self, bindings: dict):
        """
        This function returns the evaluated value of the not null members
        :param bindings:
        :return: evaluated return for the string python code
        """
        arg_list = []
        if self.value_expression:
            response = self.value_expression.evaluate(bindings)
            arg_list.append(response)
            # for i in self.expression:
            #     arg_list.append(i.evaluate(bindings))
        if self.symbol:
            if bindings['code'] is not None:
                function = bindings['code']
                exec(function)
                result = eval(str(self.symbol) + "(*arg_list)")
                print(result)
                return result
            else:
                return None
        elif self.string_expression:
            function = str(self.string_expression)
            result = eval(function)(*arg_list)
            print(result)
            return result
        else:
            return None

    def evaluate_and_get_cell(self, bindings: dict) -> tuple:
        """
        This function returns the evaluated value of the not null members
        :param bindings:
        :return: str or int based on the type of expression
        """
        arg_list = []
        if self.value_expression:
            ce, re, response = self.value_expression.evaluate_and_get_cell(bindings)
            arg_list.append(response)
            # for i in self.expression:
            #     arg_list.append(i.evaluate_and_get_cell(bindings))
        if self.symbol:
            if bindings['code'] is not None:
                function = bindings['code']
                exec(function)
                result = eval(str(self.symbol)+"(*arg_list)")
                print(result)
                return ce, re, result
            else:
                return None, None, None
        elif self.string_expression:
            function = self.string_expression
            result = eval(function)(*arg_list)
            print(result)
            return ce, re, result
        else:
            return None, None, None

    def check_for_left(self) -> bool:
        """
        this function checks if $left is present as a column variable at any leaf
        :return:
        """
        has_left = False
        if self.value_expression:
            for i in self.value_expression:
                has_left = has_left or self.value_expression.check_for_left()
        return has_left

    def check_for_right(self) -> bool:
        """
        this function checks if $right is present as a column variable at any leaf
        :return:
        """
        has_right = False
        if self.value_expression:
            for i in self.value_expression:
                has_right = has_right or self.value_expression.check_for_right()
        return has_right

    def check_for_top(self) -> bool:
        """
        this function checks if $top is present as a column variable at any leaf
        :return:
        """
        has_top = False
        if self.value_expression:
            for i in self.value_expression:
                has_top = has_top or self.value_expression.check_for_top()
        return has_top

    def check_for_bottom(self) -> bool:
        """
        this function checks if $bottom is present as a column variable at any leaf
        :return:
        """
        has_bottom = False
        if self.value_expression:
            for i in self.value_expression:
                has_bottom = has_bottom or self.value_expression.check_for_bottom()
        return has_bottom
