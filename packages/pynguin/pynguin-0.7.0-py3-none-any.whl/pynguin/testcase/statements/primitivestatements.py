#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2021 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
"""Provides primitive statements."""
import math
from abc import abstractmethod
from typing import Any, Generic, List, Optional, Set, Type, TypeVar

import pynguin.configuration as config
import pynguin.testcase.statements.statement as stmt
import pynguin.testcase.statements.statementvisitor as sv
import pynguin.testcase.testcase as tc
import pynguin.testcase.variable.variablereference as vr
import pynguin.testcase.variable.variablereferenceimpl as vri
from pynguin.analyses.seeding.constantseeding import (
    dynamic_constant_seeding,
    static_constant_seeding,
)
from pynguin.utils import randomness
from pynguin.utils.generic.genericaccessibleobject import GenericAccessibleObject

# pylint:disable=invalid-name
T = TypeVar("T")


class PrimitiveStatement(Generic[T], stmt.Statement):
    """Abstract primitive statement which holds a value."""

    def __init__(
        self,
        test_case: tc.TestCase,
        variable_type: Optional[Type],
        value: Optional[T] = None,
    ) -> None:
        super().__init__(test_case, vri.VariableReferenceImpl(test_case, variable_type))
        self._value = value
        if value is None:
            self.randomize_value()

    @property
    def value(self) -> Optional[T]:
        """Provides the primitive value of this statement.

        Returns:
            The primitive value
        """
        return self._value

    @value.setter
    def value(self, value: T) -> None:
        self._value = value

    def accessible_object(self) -> Optional[GenericAccessibleObject]:
        return None

    def mutate(self) -> bool:
        old_value = self._value
        while self._value == old_value and self._value is not None:
            self.delta()
        return True

    def get_variable_references(self) -> Set[vr.VariableReference]:
        return {self.ret_val}

    def replace(self, old: vr.VariableReference, new: vr.VariableReference) -> None:
        if self.ret_val == old:
            self.ret_val = new

    @abstractmethod
    def randomize_value(self) -> None:
        """Randomize the primitive value of this statement."""

    @abstractmethod
    def delta(self) -> None:
        """Add a random delta to the value."""

    def __repr__(self) -> str:
        return (
            f"PrimitiveStatement({self._test_case}, {self._ret_val}, "
            + f"{self._value})"
        )

    def __str__(self) -> str:
        return f"{self._value}: {self._ret_val}"

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, PrimitiveStatement):
            return False
        return self._ret_val == other._ret_val and self._value == other._value

    def __hash__(self) -> int:
        return 31 + hash(self._ret_val) + hash(self._value)


class IntPrimitiveStatement(PrimitiveStatement[int]):
    """Primitive Statement that creates an int."""

    def __init__(self, test_case: tc.TestCase, value: Optional[int] = None) -> None:
        super().__init__(test_case, int, value)

    def randomize_value(self) -> None:
        use_seed = (
            randomness.next_float()
            <= config.configuration.seeded_primitives_reuse_probability
        )
        if (
            config.configuration.dynamic_constant_seeding
            and dynamic_constant_seeding.has_ints
            and use_seed
            and config.configuration.constant_seeding
            and randomness.next_float()
            <= config.configuration.seeded_dynamic_values_reuse_probability
        ):
            self._value = dynamic_constant_seeding.random_int
        elif (
            config.configuration.constant_seeding
            and static_constant_seeding.has_ints
            and use_seed
        ):
            self._value = static_constant_seeding.random_int
        else:
            self._value = int(randomness.next_gaussian() * config.configuration.max_int)

    def delta(self) -> None:
        assert self._value is not None
        delta = math.floor(randomness.next_gaussian() * config.configuration.max_delta)
        self._value += delta

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return IntPrimitiveStatement(test_case, self._value)

    def __repr__(self) -> str:
        return f"IntPrimitiveStatement({self._test_case}, {self._value})"

    def __str__(self) -> str:
        return f"{self._value}: int"

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_int_primitive_statement(self)


class FloatPrimitiveStatement(PrimitiveStatement[float]):
    """Primitive Statement that creates a float."""

    def __init__(self, test_case: tc.TestCase, value: Optional[float] = None) -> None:
        super().__init__(test_case, float, value)

    def randomize_value(self) -> None:
        use_seed = (
            randomness.next_float()
            <= config.configuration.seeded_primitives_reuse_probability
        )
        if (
            config.configuration.dynamic_constant_seeding
            and dynamic_constant_seeding.has_floats
            and use_seed
            and config.configuration.constant_seeding
            and randomness.next_float()
            <= config.configuration.seeded_dynamic_values_reuse_probability
        ):
            self._value = dynamic_constant_seeding.random_float
        elif (
            config.configuration.constant_seeding
            and static_constant_seeding.has_floats
            and use_seed
        ):
            self._value = static_constant_seeding.random_float
        else:
            val = randomness.next_gaussian() * config.configuration.max_int
            precision = randomness.next_int(0, 7)
            self._value = round(val, precision)

    def delta(self) -> None:
        assert self._value is not None
        probability = randomness.next_float()
        if probability < 1.0 / 3.0:
            self._value += randomness.next_gaussian() * config.configuration.max_delta
        elif probability < 2.0 / 3.0:
            self._value += randomness.next_gaussian()
        else:
            self._value = round(self._value, randomness.next_int(0, 7))

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return FloatPrimitiveStatement(test_case, self._value)

    def __repr__(self) -> str:
        return f"FloatPrimitiveStatement({self._test_case}, {self._value})"

    def __str__(self) -> str:
        return f"{self._value}: float"

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_float_primitive_statement(self)


class StringPrimitiveStatement(PrimitiveStatement[str]):
    """Primitive Statement that creates a String."""

    def __init__(self, test_case: tc.TestCase, value: Optional[str] = None) -> None:
        super().__init__(test_case, str, value)

    def randomize_value(self) -> None:
        use_seed = (
            randomness.next_float()
            <= config.configuration.seeded_primitives_reuse_probability
        )
        if (
            config.configuration.dynamic_constant_seeding
            and dynamic_constant_seeding.has_strings
            and use_seed
            and config.configuration.constant_seeding
            and randomness.next_float()
            <= config.configuration.seeded_dynamic_values_reuse_probability
        ):
            self._value = dynamic_constant_seeding.random_string
        elif (
            config.configuration.constant_seeding
            and static_constant_seeding.has_strings
            and use_seed
        ):
            self._value = static_constant_seeding.random_string
        else:
            length = randomness.next_int(0, config.configuration.string_length + 1)
            self._value = randomness.next_string(length)

    def delta(self) -> None:
        assert self._value is not None
        working_on = list(self._value)
        p_perform_action = 1.0 / 3.0
        if randomness.next_float() < p_perform_action and len(working_on) > 0:
            working_on = self._random_deletion(working_on)

        if randomness.next_float() < p_perform_action and len(working_on) > 0:
            working_on = self._random_replacement(working_on)

        if randomness.next_float() < p_perform_action:
            working_on = self._random_insertion(working_on)

        self._value = "".join(working_on)

    @staticmethod
    def _random_deletion(working_on: List[str]) -> List[str]:
        p_per_char = 1.0 / len(working_on)
        return [char for char in working_on if randomness.next_float() >= p_per_char]

    @staticmethod
    def _random_replacement(working_on: List[str]) -> List[str]:
        p_per_char = 1.0 / len(working_on)
        return [
            randomness.next_char() if randomness.next_float() < p_per_char else char
            for char in working_on
        ]

    @staticmethod
    def _random_insertion(working_on: List[str]) -> List[str]:
        pos = 0
        if len(working_on) > 0:
            pos = randomness.next_int(0, len(working_on) + 1)
        alpha = 0.5
        exponent = 1
        while (
            randomness.next_float() <= pow(alpha, exponent)
            and len(working_on) < config.configuration.string_length
        ):
            exponent += 1
            working_on = working_on[:pos] + [randomness.next_char()] + working_on[pos:]
        return working_on

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return StringPrimitiveStatement(test_case, self._value)

    def __repr__(self) -> str:
        return f"StringPrimitiveStatement({self._test_case}, {self._value})"

    def __str__(self) -> str:
        return f"{self._value}: str"

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_string_primitive_statement(self)


class BytesPrimitiveStatement(PrimitiveStatement[bytes]):
    """Primitive Statement that creates bytes."""

    def __init__(self, test_case: tc.TestCase, value: Optional[bytes] = None) -> None:
        super().__init__(test_case, bytes, value)

    def randomize_value(self) -> None:
        length = randomness.next_int(0, config.configuration.bytes_length + 1)
        self._value = randomness.next_bytes(length)

    def delta(self) -> None:
        assert self._value is not None
        working_on = list(self._value)
        p_perform_action = 1.0 / 3.0
        if randomness.next_float() < p_perform_action and len(working_on) > 0:
            working_on = self._random_deletion(working_on)

        if randomness.next_float() < p_perform_action and len(working_on) > 0:
            working_on = self._random_replacement(working_on)

        if randomness.next_float() < p_perform_action:
            working_on = self._random_insertion(working_on)

        self._value = bytes(working_on)

    @staticmethod
    def _random_deletion(working_on: List[int]) -> List[int]:
        p_per_char = 1.0 / len(working_on)
        return [char for char in working_on if randomness.next_float() >= p_per_char]

    @staticmethod
    def _random_replacement(working_on: List[int]) -> List[int]:
        p_per_char = 1.0 / len(working_on)
        return [
            randomness.next_byte() if randomness.next_float() < p_per_char else byte
            for byte in working_on
        ]

    @staticmethod
    def _random_insertion(working_on: List[int]) -> List[int]:
        pos = 0
        if len(working_on) > 0:
            pos = randomness.next_int(0, len(working_on) + 1)
        alpha = 0.5
        exponent = 1
        while (
            randomness.next_float() <= pow(alpha, exponent)
            and len(working_on) < config.configuration.bytes_length
        ):
            exponent += 1
            working_on = working_on[:pos] + [randomness.next_byte()] + working_on[pos:]
        return working_on

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return BytesPrimitiveStatement(test_case, self._value)

    def __repr__(self) -> str:
        return f"BytesPrimitiveStatement({self._test_case}, {self._value!r})"

    def __str__(self) -> str:
        return f"{self._value!r}: bytes"

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_bytes_primitive_statement(self)


class BooleanPrimitiveStatement(PrimitiveStatement[bool]):
    """Primitive Statement that creates a boolean."""

    def __init__(self, test_case: tc.TestCase, value: Optional[bool] = None) -> None:
        super().__init__(test_case, bool, value)

    def randomize_value(self) -> None:
        self._value = bool(randomness.RNG.getrandbits(1))

    def delta(self) -> None:
        assert self._value is not None
        self._value = not self._value

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return BooleanPrimitiveStatement(test_case, self._value)

    def __repr__(self) -> str:
        return f"BooleanPrimitiveStatement({self._test_case}, {self._value})"

    def __str__(self) -> str:
        return f"{self._value}: bool"

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_boolean_primitive_statement(self)


class NoneStatement(PrimitiveStatement):
    """A statement serving as a None reference."""

    def clone(self, test_case: tc.TestCase, offset: int = 0) -> stmt.Statement:
        return NoneStatement(test_case, self.ret_val.variable_type)

    def accept(self, visitor: sv.StatementVisitor) -> None:
        visitor.visit_none_statement(self)

    def randomize_value(self) -> None:
        pass

    def delta(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"NoneStatement({self._test_case})"

    def __str__(self) -> str:
        return "None"
