from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseCart
from .collections import get_collection
from .datastructures import CartConfig
from .product_items import ProductItems


class Cart(BaseCart):
    product_multi_item_cls = ProductItems
    config_cls = CartConfig

    def _init_cart_extra(self) -> Dict[str, Any]:
        return {}

    def _calc_fee(self) -> Tuple[int, List[Dict[str, Any]]]:
        fee_items: List[Dict[str, Any]] = [
            {
                "name": "運費",
                "amount": 0,
            }
        ]
        return (sum(i["amount"] for i in fee_items), fee_items)

    def _calc_coupon_discounts(
        self, subtotal: int, coupon_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if coupon_code:
            coupon = get_collection("coupon").find_one(
                {
                    "code": coupon_code,
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "usage": {"$gt": 0},
                }
            )

            if coupon and subtotal > coupon["threshold"]:
                items.append(
                    {
                        "type": "coupon",
                        "name": coupon["name"],
                        "sales_amount": round(coupon["discount"] / self._tax_ratio, 7),
                        "amount": coupon["discount"],
                        "coupon": coupon,
                    }
                )

        return items

    def _calc_threshold_discounts(self, subtotal: int) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if get_collection("discount") is not None:
            discounts = get_collection("discount").find(
                {
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "threshold": {"$lte": subtotal},
                }
            )

            if discounts:
                discounts.sort((("threshold", -1),))
                for discount in discounts:
                    items.append(
                        {
                            "type": "discount",
                            "name": discount["name"],
                            "sales_amount": round(
                                discount["discount"] / self._tax_ratio, 7
                            ),
                            "amount": discount["discount"],
                            "discount": discount,
                        }
                    )
                    break

        return items

    def _calc_discounts(
        self, subtotal: int, coupon_code: Optional[str] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        items = []

        items += self._calc_coupon_discounts(subtotal, coupon_code)
        items += self._calc_threshold_discounts(subtotal)

        return sum([item["amount"] for item in items]), items
