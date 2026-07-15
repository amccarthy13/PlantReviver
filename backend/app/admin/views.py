"""SQLAdmin model views (ARCHITECTURE.md §12).

Users are editable so you can set `disabled_at` (ban) or `deleted_at`. Everything
else is read-only by default — the admin is for oversight, not data entry.
Entitlements are editable to allow manual comp/grant of premium.
"""

from sqladmin import ModelView

from app.models.entitlement import Entitlement
from app.models.plant import Plant
from app.models.subscription import Subscription
from app.models.usage_counter import UsageCounter
from app.models.user import User


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list = [
        User.id,
        User.email,
        User.apple_user_id,
        User.disabled_at,
        User.deleted_at,
        User.created_at,
    ]
    column_searchable_list = [User.email, User.apple_user_id]
    can_create = False
    can_edit = True
    can_delete = True


class PlantAdmin(ModelView, model=Plant):
    name_plural = "Plants"
    icon = "fa-solid fa-seedling"
    column_list = [
        Plant.id,
        Plant.user_id,
        Plant.name,
        Plant.next_watering_date,
        Plant.deleted_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class SubscriptionAdmin(ModelView, model=Subscription):
    name_plural = "Subscriptions"
    icon = "fa-solid fa-credit-card"
    column_list = [
        Subscription.id,
        Subscription.user_id,
        Subscription.product_id,
        Subscription.status,
        Subscription.expires_at,
        Subscription.environment,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class EntitlementAdmin(ModelView, model=Entitlement):
    name_plural = "Entitlements"
    icon = "fa-solid fa-key"
    column_list = [
        Entitlement.id,
        Entitlement.user_id,
        Entitlement.feature,
        Entitlement.active,
        Entitlement.source,
    ]
    can_create = True
    can_edit = True
    can_delete = True


class UsageCounterAdmin(ModelView, model=UsageCounter):
    name_plural = "Usage"
    icon = "fa-solid fa-gauge"
    column_list = [
        UsageCounter.id,
        UsageCounter.user_id,
        UsageCounter.feature,
        UsageCounter.period,
        UsageCounter.count,
    ]
    can_create = False
    can_edit = False
    can_delete = False


ALL_VIEWS: list[type[ModelView]] = [
    UserAdmin,
    PlantAdmin,
    SubscriptionAdmin,
    EntitlementAdmin,
    UsageCounterAdmin,
]
