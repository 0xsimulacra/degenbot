import enum
from decimal import Decimal
from fractions import Fraction
from typing import Any, Callable, Sequence

from ..erc20_token import Erc20Token
from ..uniswap.v2_liquidity_pool import LiquidityPool
from ..uniswap.v3_liquidity_pool import V3LiquidityPool
from .conditional_action import ConditionalAction
from .token_price_conditions import (
    TokenPriceEquals,
    TokenPriceGreaterThan,
    TokenPriceGreaterThanOrEqual,
    TokenPriceLessThan,
    TokenPriceLessThanOrEqual,
)


class ComparisonModes(enum.Enum):
    LESS_THAN = enum.auto()
    LESS_THAN_OR_EQUAL = enum.auto()
    EQUALS = enum.auto()
    GREATER_THAN_OR_EQUAL = enum.auto()
    GREATER_THAN = enum.auto()


class UniswapLimitOrder(ConditionalAction):
    def __init__(
        self,
        pool: LiquidityPool | V3LiquidityPool,
        buy_token: Erc20Token,
        mode: ComparisonModes,
        price_target: int | float | Decimal | Fraction,
        actions: Sequence[Callable[[], Any]],
    ):
        """
        A Uniswap limit order, conditionally executed against the price of `token` in the given
        `pool`.
        """

        # Convert int or float price targets to Decimal values so the inverse operation does not
        # introduce floating point error
        if isinstance(price_target, float):
            target_rate = Decimal.from_float(price_target)
        elif isinstance(price_target, int):
            target_rate = Decimal(price_target)
        else:
            target_rate = 1 / price_target

        match mode:
            case ComparisonModes.LESS_THAN:
                self.condition = TokenPriceLessThan(
                    token=buy_token,
                    pool=pool,
                    target=target_rate,
                )
            case ComparisonModes.LESS_THAN_OR_EQUAL:
                self.condition = TokenPriceLessThanOrEqual(
                    token=buy_token,
                    pool=pool,
                    target=target_rate,
                )
            case ComparisonModes.EQUALS:
                self.condition = TokenPriceEquals(
                    token=buy_token,
                    pool=pool,
                    target=target_rate,
                )
            case ComparisonModes.GREATER_THAN_OR_EQUAL:
                self.condition = TokenPriceGreaterThanOrEqual(
                    token=buy_token,
                    pool=pool,
                    target=target_rate,
                )
            case ComparisonModes.GREATER_THAN:
                self.condition = TokenPriceGreaterThan(
                    token=buy_token,
                    pool=pool,
                    target=target_rate,
                )
            case _:
                raise ValueError(f"Unknown price mode {mode} specified")

        self.actions = actions

    @classmethod
    def from_nominal_price(
        cls,
        pool: LiquidityPool | V3LiquidityPool,
        buy_token: Erc20Token,
        mode: ComparisonModes,
        price_target: int | float | Decimal | Fraction,
        actions: Sequence[Callable[[], Any]],
    ) -> "UniswapLimitOrder":
        """
        Build a Uniswap limit order using a nominal price target. Translates nominal values to
        absolute values for the given token by correcting for decimal places.

        e.g. a price target of 100.00 USDC is translated to 100.00 * 10**6
        """

        absolute_price = price_target * 10**buy_token.decimals

        return cls(
            pool=pool,
            buy_token=buy_token,
            mode=mode,
            price_target=absolute_price,
            actions=actions,
        )
