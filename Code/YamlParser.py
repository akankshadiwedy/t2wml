from typing import Union

import yaml

from Code.ColumnExpression import ColumnExpression
from Code.ItemExpression import ItemExpression
from Code.RowExpression import RowExpression
from Code.ValueExpression import ValueExpression
from Code.bindings import bindings
from Code.BooleanEquation import BooleanEquation
from Code.EvalExpression import EvalExpression
from Code.t2wml_parser import parse_and_evaluate, generate_tree


class YAMLParser:
    def __init__(self, yaml_file_path: str):
        with open(yaml_file_path, 'r') as stream:
            self.yaml_data = yaml.safe_load(stream)

    def get_region(self, bindings: dict) -> dict:
        """
        This function parses the region specified in the YAML
        :return:
        """
        left = generate_tree(str(self.yaml_data['statementMapping']['region'][0]['left']))
        left.get_variable_cell_operator_arguments()
        right = generate_tree(str(self.yaml_data['statementMapping']['region'][0]['right']))
        right.get_variable_cell_operator_arguments()
        top = generate_tree(str(self.yaml_data['statementMapping']['region'][0]['top']))
        top.get_variable_cell_operator_arguments()
        bottom = generate_tree(str(self.yaml_data['statementMapping']['region'][0]['bottom']))
        bottom.get_variable_cell_operator_arguments()

        has_right = left.check_for_right()
        has_left = right.check_for_left()
        has_top = bottom.check_for_top()
        has_bottom = top.check_for_bottom()

        if not (has_left and has_right):
            if has_left and not has_right:
                left = self.iterate_on_variables(left, bindings)
                bindings['$left'] = left
                right = self.iterate_on_variables(right, bindings)
                bindings['$right'] = right
            elif has_right and not has_left:
                right = self.iterate_on_variables(right, bindings)
                bindings['$right'] = right
                left = self.iterate_on_variables(left, bindings)
                bindings['$left'] = left
            elif not has_left and not has_right:
                left = self.iterate_on_variables(left, bindings)
                right = self.iterate_on_variables(right, bindings)
                bindings['$left'] = left
                bindings['$right'] = right
        else:
            return {'error': 'Recursive definition of left and right region parameters'}

        if not (has_top and has_bottom):
            if has_top and not has_bottom:
                top = self.iterate_on_variables(top, bindings)
                bindings['$top'] = top
                bottom = self.iterate_on_variables(bottom, bindings)
                bindings['$bottom'] = bottom
            elif has_bottom and not has_top:
                bottom = self.iterate_on_variables(bottom, bindings)
                bindings['$bottom'] = bottom
                top = self.iterate_on_variables(top, bindings)
                bindings['$top'] = top
            elif not has_top and not has_bottom:
                top = self.iterate_on_variables(top, bindings)
                bottom = self.iterate_on_variables(bottom, bindings)
                bindings['$top'] = top
                bindings['$bottom'] = bottom
        else:
            return {'error': 'Recursive definition of top and bottom region parameters'}

        if 'skip_row' in self.yaml_data['statementMapping']['region'][0]:
            skip_row = list()
            for i in range(len(self.yaml_data['statementMapping']['region'][0]['skip_row'])):
                skip_row.append(generate_tree(self.yaml_data['statementMapping']['region'][0]['skip_row'][i]))
        else:
            skip_row = None

        if 'skip_column' in self.yaml_data['statementMapping']['region'][0]:
            skip_column = list()
            for i in range(len(self.yaml_data['statementMapping']['region'][0]['skip_column'])):
                skip_column.append(generate_tree(self.yaml_data['statementMapping']['region'][0]['skip_column'][i]))
        else:
            skip_column = None

        if 'skip_cell' in self.yaml_data['statementMapping']['region'][0]:
            skip_cell = list()
            for i in range(len(self.yaml_data['statementMapping']['region'][0]['skip_cell'])):
                skip_cell.append(generate_tree(self.yaml_data['statementMapping']['region'][0]['skip_cell'][i]))
        else:
            skip_cell = None

        return {'left': left, 'right': right, 'top': top, 'bottom': bottom, 'skip_row': skip_row,
                'skip_column': skip_column, 'skip_cell': skip_cell}

    def get_template_item(self) -> str:
        """
        This function returns the value of the item attribute of the template
        :return:
        """
        try:
            response = str(self.yaml_data['statementMapping']['template']['item'])
        except KeyError:
            response = None
        return response

    def get_template_value(self) -> str:
        """
        This function returns the value of the value attribute of the template
        :return:
        """
        try:
            response = str(self.yaml_data['statementMapping']['template']['value'])
        except KeyError:
            response = None
        return response

    def get_template_property(self) -> str:
        """
        This function returns the value of the property attribute of the template
        :return:
        """
        try:
            response = str(self.yaml_data['statementMapping']['template']['property'])
        except KeyError:
            response = None
        return response

    def get_qualifiers(self) -> str:
        """
        This function returns the value of the qualifier attribute of the template
        :return:
        """
        try:
            response = self.yaml_data['statementMapping']['template']['qualifier']
        except KeyError:
            response = None
        return response

    def resolve_template(self, template: str) -> None:
        """
        This function parses all the expressions of the template and replace them with their respective class objects
        :param template:
        :return:
        """
        # Resolve Template Item if needed
        template_item = self.get_template_item()
        if template_item:
            if not template_item.isalnum():
                template['item'] = generate_tree(template_item)
                template['item'].get_variable_cell_operator_arguments()

            else:
                template['item'] = template_item

        # Resolve Template Property if needed
        template_property = self.get_template_property()
        if template_property:
            if template_property and not template_property.isalnum():
                template['property'] = generate_tree(template_property)
                template['property'].get_variable_cell_operator_arguments()
            else:
                template['property'] = template_property

        # Resolve Template Value if needed
        template_value = self.get_template_value()
        if template_value:
            if not template_value.isalnum():
                template["value"] = generate_tree(template_value)
                template["value"].get_variable_cell_operator_arguments()
            else:
                template["value"] = template_value

        if template.get('qualifier', None):
            for i in range(len(template['qualifier'])):
                qualifier_value = str(template['qualifier'][i]['value'])
                if qualifier_value:
                    if not qualifier_value.isalnum():
                        template['qualifier'][i]['value'] = generate_tree(qualifier_value)
                        var = template['qualifier'][i]['value'].get_variable_cell_operator_arguments()
                    else:
                        template['qualifier'][i]['value'] = qualifier_value

    def get_template(self) -> dict:
        """
        This function resolves and returns the template
        :return:
        """
        template = self.yaml_data['statementMapping']['template']
        self.resolve_template(template)
        return template

    def get_code(self, bindings: dict) -> str:
        """
        This function resolves and returns the code
        :return:
        """
        if 'code' in self.yaml_data['statementMapping'].keys():
            code = self.yaml_data['statementMapping']['code']
            self.resolve_code(code)
            bindings['code'] = code
        else:
            code = None
        return code

    def resolve_code(self, code):
        """
        This function executes the functions in code and initializes their description
        :param code: code
        :return:
        """
        exec(code)


    def get_created_by(self) -> str:
        try:
            created_by = self.yaml_data['statementMapping']['created_by']
        except:
            created_by = 't2wml'
        return created_by

    def iterate_on_variables(self, parse_tree: Union[
        ItemExpression, ValueExpression, BooleanEquation, ColumnExpression, RowExpression, EvalExpression], bindings: dict) -> Union[
        int, str]:
        """
        This function checks if there are any variable iterators present in the parse tree.
        If yes it iterates on the variables to evaluate the parse tree.
        This function is only for Region Parameters viz, left, right, top and bottom.
        :param parse_tree:
        :param bindings:
        :return:
        """
        value = None
        if isinstance(parse_tree, (ItemExpression, ValueExpression, BooleanEquation, EvalExpression)):
            if parse_tree.variables:
                variables = list(parse_tree.variables)
                num_of_variables = len(variables)
                if num_of_variables == 1:
                    bindings[variables[0]] = 0
                    while not parse_tree.evaluate(bindings):
                        bindings[variables[0]] += 1
                    value = parse_tree.evaluate(bindings)
                    del bindings[variables[0]]
            else:
                value = parse_tree.evaluate(bindings)
        else:
            value = parse_tree.evaluate(bindings)
        return value
