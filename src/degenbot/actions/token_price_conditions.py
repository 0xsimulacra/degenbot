from decimal import Decimal
from fractions import Fraction

from ..erc20_token import Erc20Token
from ..uniswap.v2_liquidity_pool import LiquidityPool
from ..uniswap.v3_liquidity_pool import V3LiquidityPool
from .baseclasses import BaseCondition


class TokenPriceCondition(BaseCondition):
    def __init__(
        self,
        token: Erc20Token,
        pool: LiquidityPool | V3LiquidityPool,
        target: int | float | Decimal | Fraction,
    ):
        """
        An abstract condition that can access the instantaneous price of `token` in terms of the
        other token held by `pool`. The price is absolute, i.e. it reflects the full decimal
        precision for the ERC-20 token contract.

        Derived classes should override the `__call__` method to implement boolean conditions
        related to this price.
        """

        self.token = token
        self.pool = pool
        self.target = target

    @property
    def price(self) -> Fraction:
        return self.pool.get_absolute_price(self.token)

    def update_target(
        self,
        price: int | float | Decimal | Fraction,
    ) -> None:
        self.target = price


class TokenPriceLessThan(TokenPriceCondition):
    def __call__(self) -> bool:
        return self.price < self.target


class TokenPriceLessThanOrEqual(TokenPriceCondition):
    def __call__(self) -> bool:
        return self.price <= self.target


class TokenPriceEquals(TokenPriceCondition):
    def __call__(self) -> bool:
        return self.price == self.target


class TokenPriceGreaterThan(TokenPriceCondition):
    def __call__(self) -> bool:
        return self.price > self.target


class TokenPriceGreaterThanOrEqual(TokenPriceCondition):
    def __call__(self) -> bool:
        return self.price > self.target
