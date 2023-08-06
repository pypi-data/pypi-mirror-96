"""Class implementation for number value interface.
"""

from typing import Any
from typing import Union

from apyscript.expression import expression_file_util
from apyscript.html import html_util
from apyscript.type.copy_interface import CopyInterface
from apyscript.type.variable_name_interface import VariableNameInterface
from apyscript.validation import number_validation


class NumberValueInterface(CopyInterface):

    _initial_value: Union[int, float, Any]
    _value: Union[int, float]

    def __init__(
            self, value: Union[int, float, Any], type_name: str) -> None:
        """
        Class for number value interface.

        Parameters
        ----------
        value : int or float or NumberValueInterface
            Initial number value.
        type_name : str
            This instance expression's type name (e.g., int, number).
        """
        number_validation.validate_num(num=value)
        self._initial_value = value
        if isinstance(value, NumberValueInterface):
            value_ = value._value
        else:
            value_ = value
        self._value = value_
        self._type_name = type_name

    def append_constructor_expression(self) -> None:
        """
        Append current value's constructor expression to file.
        """
        if isinstance(self._initial_value, NumberValueInterface):
            value_: Union[int, float, str] = self._initial_value.variable_name
        else:
            value_ = self.value
        expression: str = (
            f'var {self.variable_name} = {value_};'
        )
        expression = html_util.wrap_expression_by_script_tag(
            expression=expression)
        expression_file_util.append_expression(expression=expression)

    @property
    def value(self) -> Union[int, float, Any]:
        """
        Get current number value.

        Returns
        -------
        value : int or float
            Current number value.
        """
        return self._value

    @value.setter
    def value(self, value: Union[int, float, Any]) -> None:
        """
        Set number value.

        Parameters
        ----------
        value : int or float or NumberValueInterface
            Any number value to set.
        """
        self.set_value_and_skip_expression_appending(value=value)
        if isinstance(value, NumberValueInterface):
            self.append_value_setter_expression(value=value)
        else:
            self.append_value_setter_expression(value=self._value)

    def set_value_and_skip_expression_appending(
            self, value: Union[int, float, Any]) -> None:
        """
        Update value attribute and skip expression appending.

        Parameters
        ----------
        value : int or float or NumberValueInterface
            Any number value to set.
        """
        number_validation.validate_num(num=value)
        if isinstance(value, NumberValueInterface):
            value_ = value._value
        else:
            value_ = value
        self._value = value_

    def append_value_setter_expression(
            self, value: Union[int, float, Any]) -> None:
        """
        Append value's setter expresion to file.

        Parameters
        ----------
        value : int or float or NumberValueInterface
            Any number value to set.
        """
        if isinstance(value, NumberValueInterface):
            right_value: Union[str, int, float] = value.variable_name
        else:
            right_value = value
        expression: str = (
            f'{self.variable_name} = {right_value};'
        )
        expression = html_util.wrap_expression_by_script_tag(
            expression=expression)
        expression_file_util.append_expression(expression=expression)

    def _get_arithmetic_expression_right_value(
            self, other: Any) -> Union[int, float, str]:
        """
        Get a arithmetic expression's right value (e.g., variable name,
        actual integer, or float value).

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value of arithmetic expression.

        Returns
        -------
        right_value : int or float or str
            If other is instance of NumberValueInterface,
            then variable name will be set. Otherwise, int or float
            value will be set.
        """
        if isinstance(other, NumberValueInterface):
            return other.variable_name
        return other  # type: ignore

    def __add__(self, other: Union[int, float, Any]) -> Any:
        """
        Method for addition.

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value to add.

        Returns
        -------
        result : NumberValueInterface
            Addition result value.
        """
        if isinstance(other, NumberValueInterface):
            value: Union[int, float, Any] = self._value + other.value
        else:
            value = self._value + other
        result: NumberValueInterface = self._copy()
        result.set_value_and_skip_expression_appending(value=value)
        self._append_addition_expression(result=result, other=other)
        return result

    def _append_addition_expression(
            self, result: VariableNameInterface,
            other: Union[int, float, Any]) -> None:
        """
        Append addition expression to file.

        Parameters
        ----------
        result : NumberValueInterface
            Addition result value.
        other : int or float or NumberValueInterface
            Other value to add.
        """
        right_value: Union[int, float, str] = \
            self._get_arithmetic_expression_right_value(other=other)
        expression: str = (
            f'var {result.variable_name} = '
            f'{self.variable_name} + {right_value};'
        )
        expression_file_util.wrap_by_script_tag_and_append_expression(
            expression=expression)

    def __sub__(self, other: Union[int, float, Any]) -> Any:
        """
        Method for subtraction.

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value to subtract.

        Returns
        -------
        result : NumberValueInterface
            Subtraction result value.
        """
        if isinstance(other, NumberValueInterface):
            value: Union[int, float, Any] = self._value - other.value
        else:
            value = self._value - other
        result: NumberValueInterface = self._copy()
        result.set_value_and_skip_expression_appending(value=value)
        self._append_subtraction_expression(result=result, other=other)
        return result

    def _append_subtraction_expression(
            self, result: VariableNameInterface,
            other: Union[int, float, Any]) -> None:
        """
        Append subtraction expression to file.

        Parameters
        ----------
        result : NumberValueInterface
            Subtraction result value.
        other : int or float or NumberValueInterface
            Other value to subtract.
        """
        right_value: Union[int, float, str] = \
            self._get_arithmetic_expression_right_value(other=other)
        expression: str = (
            f'var {result.variable_name} = '
            f'{self.variable_name} - {right_value};'
        )
        expression_file_util.wrap_by_script_tag_and_append_expression(
            expression=expression)

    def __mul__(self, other: Union[int, float, Any]) -> Any:
        """
        Method for multiplication.

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value to multiply.

        Returns
        -------
        result : NumberValueInterface
            Multiplication result value.
        """
        if isinstance(other, NumberValueInterface):
            value: Union[int, float, Any] = self._value * other.value
        else:
            value = self._value * other
        result: NumberValueInterface = self._copy()
        result.set_value_and_skip_expression_appending(value=value)
        self._append_multiplication_expression(result=result, other=other)
        return result

    def _append_multiplication_expression(
            self, result: VariableNameInterface,
            other: Union[int, float, Any]) -> None:
        """
        Append multiplication expression to file.

        Parameters
        ----------
        result : NumberValueInterface
            Multiplication result value.
        other : int or float or NumberValueInterface
            Other value to multiply.
        """
        right_value: Union[int, float, str] = \
            self._get_arithmetic_expression_right_value(other=other)
        expression: str = (
            f'var {result.variable_name} = '
            f'{self.variable_name} * {right_value};'
        )
        expression_file_util.wrap_by_script_tag_and_append_expression(
            expression=expression)

    def __truediv__(self, other: Union[int, float, Any]) -> Any:
        """
        Method for true division (return floating point number).

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value for true division.

        Returns
        -------
        result : Number
            True division result value.
        """
        from apyscript.type.number import Number
        result: Number = Number(value=self)
        if isinstance(other, NumberValueInterface):
            value: Union[int, float, Any] = result._value / other.value
        else:
            value = result._value / other
        result.set_value_and_skip_expression_appending(value=value)
        self._append_true_division_expression(result=result, other=other)
        return result

    def _append_true_division_expression(
            self, result: VariableNameInterface,
            other: Union[int, float, Any]) -> None:
        """
        Append true division expression to file.

        Parameters
        ----------
        result : NumberValueInterface
            True division result value.
        other : int or float or NumberValueInterface
            Other value for true division.
        """
        right_value: Union[int, float, str] = \
            self._get_arithmetic_expression_right_value(other=other)
        expression: str = (
            f'{result.variable_name} = {result.variable_name} / '
            f'{right_value};'
        )
        expression_file_util.wrap_by_script_tag_and_append_expression(
            expression=expression)

    def __floordiv__(self, other: Union[int, float, Any]) -> Any:
        """
        Method for floor division (return integer).

        Parameters
        ----------
        other : int or float or NumberValueInterface
            Other value for floor division.

        Returns
        -------
        result : Int
            Floor division result value.
        """
        from apyscript.type.int import Int
        result: Int = Int(value=self)
        if isinstance(other, NumberValueInterface):
            value: Union[int, float, Any] = self._value // other.value
        else:
            value = self._value // other
        result.set_value_and_skip_expression_appending(value=value)
        self._append_floor_division_expression(result=result, other=other)
        return result

    def _append_floor_division_expression(
            self, result: VariableNameInterface,
            other: Union[int, float, Any]) -> None:
        """
        Append floor division expression to file.

        Parameters
        ----------
        result : NumberValueInterface
            Floor division result value.
        other : int or float or NumberValueInterface
            Other value for floor division.
        """
        right_value: Union[int, float, str] = \
            self._get_arithmetic_expression_right_value(other=other)
        expression: str = (
            f'{result.variable_name} = '
            f'parseInt({result.variable_name} / {right_value});'
        )
        expression_file_util.wrap_by_script_tag_and_append_expression(
            expression=expression)
