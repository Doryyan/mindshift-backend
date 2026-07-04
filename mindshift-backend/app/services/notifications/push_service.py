"""
APNs (Apple Push Notification service) 推送通知服务。

使用 HTTP/2 协议通过 httpx 向 APNs 发送推送通知。
支持训练提醒、打卡提醒和挑战更新等通知类型。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, time as dt_time
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger

from app.core.config import settings


class NotificationType(str, Enum):
    """推送通知类型"""
    TRAINING_REMINDER = "training_reminder"
    CHECKIN_REMINDER = "checkin_reminder"
    WEEKLY_CHALLENGE = "weekly_challenge"
    STREAK_MILESTONE = "streak_milestone"


@dataclass
class NotificationTemplate:
    """通知模板"""
    title: str
    body: str


# ──────── 通知模板库 ────────

TEMPLATES: dict[NotificationType, NotificationTemplate] = {
    NotificationType.TRAINING_REMINDER: NotificationTemplate(
        title="训练时间到",
        body="今天的NLP训练等待着你！花5分钟，重塑一个心智习惯。"
    ),
    NotificationType.CHECKIN_REMINDER: NotificationTemplate(
        title="今日回顾",
        body="今天打卡了吗？记录你的觉察，看见你的成长。"
    ),
    NotificationType.WEEKLY_CHALLENGE: NotificationTemplate(
        title="本周挑战",
        body="本周挑战进行中！完成3次信念日记即可获得100XP奖励。"
    ),
    NotificationType.STREAK_MILESTONE: NotificationTemplate(
        title="里程碑达成",
        body="连续训练7天！你的感官敏锐度提升了15%，继续保持！"
    ),
}


class PushService:
    """
    APNs HTTP/2 推送服务。

    使用 JWT Token 认证方式（基于 APNs Key .p8 文件）。
    """

    # APNs 端点
    SANDBOX_URL = "https://api.sandbox.push.apple.com"
    PRODUCTION_URL = "https://api.push.apple.com"

    def __init__(
        self,
        key_id: str | None = None,
        team_id: str | None = None,
        key_path: str | None = None,
        bundle_id: str | None = None,
        is_production: bool = False,
    ):
        self.key_id = key_id or getattr(settings, "APNS_KEY_ID", "")
        self.team_id = team_id or getattr(settings, "APNS_TEAM_ID", "")
        self.key_path = key_path or getattr(settings, "APNS_KEY_PATH", "")
        self.bundle_id = bundle_id or getattr(settings, "APNS_BUNDLE_ID", "com.mindshift.app")
        self.is_production = is_production or getattr(settings, "APNS_IS_PRODUCTION", False)

        self._jwt_token: str | None = None
        self._jwt_expiry: float = 0

    @property
    def base_url(self) -> str:
        """根据环境返回对应的 APNs 端点"""
        return self.PRODUCTION_URL if self.is_production else self.SANDBOX_URL

    @property
    def configured(self) -> bool:
        """检查推送服务是否已配置"""
        return bool(self.key_id and self.team_id and self.key_path)

    def _load_private_key(self) -> str:
        """从 .p8 文件读取私钥"""
        key_file = Path(self.key_path)
        if not key_file.exists():
            raise FileNotFoundError(f"APNs key file not found: {self.key_path}")
        return key_file.read_text()

    def _generate_jwt(self) -> str:
        """
        生成 APNs 认证 JWT Token。

        使用 ES256 算法，有效期最多 1 小时。
        """
        import jwt

        now = int(time.time())
        if self._jwt_token and self._jwt_expiry > now + 60:
            return self._jwt_token

        payload = {
            "iss": self.team_id,
            "iat": now,
        }

        self._jwt_token = jwt.encode(
            payload,
            self._load_private_key(),
            algorithm="ES256",
            headers={"kid": self.key_id},
        )
        self._jwt_expiry = now + 3500  # ~58 分钟，留一点余地

        return self._jwt_token

    def _build_url(self, device_token: str) -> str:
        """构建 APNs 推送请求 URL"""
        return f"{self.base_url}/3/device/{device_token}"

    def _build_payload(
        self,
        template: NotificationTemplate,
        notification_type: NotificationType,
        badge: Optional[int] = None,
        custom_data: Optional[dict] = None,
    ) -> dict:
        """构建 APNs 推送 payload"""
        payload = {
            "aps": {
                "alert": {
                    "title": template.title,
                    "body": template.body,
                },
                "sound": "default",
                "category": notification_type.value,
            },
            "notification_type": notification_type.value,
        }

        if badge is not None:
            payload["aps"]["badge"] = badge

        if custom_data:
            payload.update(custom_data)

        return payload

    async def send_notification(
        self,
        device_token: str,
        notification_type: NotificationType,
        badge: Optional[int] = None,
        custom_data: Optional[dict] = None,
        template: Optional[NotificationTemplate] = None,
    ) -> dict:
        """
        向指定设备发送推送通知。

        Args:
            device_token: 设备推送令牌
            notification_type: 通知类型
            badge: App 图标角标数字
            custom_data: 自定义附加数据
            template: 自定义通知模板（不传则使用默认模板）

        Returns:
            包含 success/error 信息的字典
        """
        if not self.configured:
            logger.warning("PushService not configured, skipping notification")
            return {"success": False, "error": "PushService not configured"}

        template = template or TEMPLATES.get(notification_type)
        if not template:
            logger.error(f"Unknown notification type: {notification_type}")
            return {"success": False, "error": f"Unknown notification type: {notification_type}"}

        payload = self._build_payload(
            template=template,
            notification_type=notification_type,
            badge=badge,
            custom_data=custom_data,
        )

        try:
            jwt_token = self._generate_jwt()

            async with httpx.AsyncClient(http2=True) as client:
                response = await client.post(
                    self._build_url(device_token),
                    json=payload,
                    headers={
                        "Authorization": f"bearer {jwt_token}",
                        "apns-topic": self.bundle_id,
                        "apns-push-type": "alert",
                        "apns-priority": "10",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    logger.info(
                        f"Push notification sent: type={notification_type.value}, "
                        f"token={device_token[:8]}..."
                    )
                    return {"success": True, "apns_id": response.headers.get("apns-id")}
                else:
                    error_body = response.text
                    logger.error(
                        f"APNs error: status={response.status_code}, body={error_body}, "
                        f"type={notification_type.value}"
                    )

                    # 处理常见错误
                    if response.status_code == 410:
                        # Device token 失效，应该从数据库中移除
                        logger.warning(f"Device token expired/invalid: {device_token[:8]}...")
                        return {
                            "success": False,
                            "error": "DeviceTokenExpired",
                            "status_code": 410,
                        }

                    return {
                        "success": False,
                        "error": error_body,
                        "status_code": response.status_code,
                    }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending APNs notification: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending APNs notification: {e}")
            return {"success": False, "error": str(e)}

    # ──────── 便捷方法 ────────

    async def send_training_reminder(
        self, device_token: str, badge: Optional[int] = None
    ) -> dict:
        """发送每日训练提醒（晚8点）"""
        return await self.send_notification(
            device_token=device_token,
            notification_type=NotificationType.TRAINING_REMINDER,
            badge=badge,
        )

    async def send_checkin_reminder(
        self, device_token: str, badge: Optional[int] = None
    ) -> dict:
        """发送每日打卡提醒（晚9点）"""
        return await self.send_notification(
            device_token=device_token,
            notification_type=NotificationType.CHECKIN_REMINDER,
            badge=badge,
        )

    async def send_weekly_challenge(
        self, device_token: str, badge: Optional[int] = None
    ) -> dict:
        """发送每周挑战更新"""
        return await self.send_notification(
            device_token=device_token,
            notification_type=NotificationType.WEEKLY_CHALLENGE,
            badge=badge,
        )

    async def send_streak_milestone(
        self, device_token: str, streak_days: int, badge: Optional[int] = None
    ) -> dict:
        """发送连续训练里程碑通知"""
        # 根据连续天数自定义消息
        if streak_days == 7:
            body = "连续训练7天！你的感官敏锐度提升了15%，继续保持！"
        elif streak_days == 30:
            body = "连续训练30天！你已完成一个完整的心智训练周期，为你骄傲！"
        elif streak_days == 100:
            body = "连续训练100天！心智重塑不是终点，而是一段美好的旅程。"
        else:
            body = f"连续训练{streak_days}天！每一步都在塑造更好的自己。"

        template = NotificationTemplate(
            title="里程碑达成",
            body=body,
        )

        return await self.send_notification(
            device_token=device_token,
            notification_type=NotificationType.STREAK_MILESTONE,
            badge=badge,
            template=template,
            custom_data={"streak_days": streak_days},
        )

    async def send_batch_notifications(
        self,
        device_tokens: list[str],
        notification_type: NotificationType,
        badge: Optional[int] = None,
        custom_data: Optional[dict] = None,
    ) -> dict:
        """
        向多个设备批量发送推送通知。

        Returns:
            {"success": count, "failed": count, "details": [...]}
        """
        results = {"success": 0, "failed": 0, "details": []}

        for token in device_tokens:
            result = await self.send_notification(
                device_token=token,
                notification_type=notification_type,
                badge=badge,
                custom_data=custom_data,
            )
            results["details"].append({"token": token[:8] + "...", **result})
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1

        logger.info(
            f"Batch push complete: type={notification_type.value}, "
            f"success={results['success']}, failed={results['failed']}"
        )
        return results


# ──────── 全局单例 ────────

push_service = PushService()
