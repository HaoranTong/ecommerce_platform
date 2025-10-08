"""
验证码服务模块

功能描述：提供验证码生成、存储、验证和清理功能
主要功能：
- 生成随机6位数字验证码
- 在Redis中存储验证码（5分钟有效期）
- 验证验证码是否正确
- 防止验证码重复使用
"""

import random
import string
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, status

from app.core.redis_client import get_redis_connection


class VerificationCodeService:
    """验证码服务类"""

    # 验证码有效期（秒）
    CODE_EXPIRY = 300  # 5分钟

    # 验证码长度
    CODE_LENGTH = 6

    @staticmethod
    def generate_code() -> str:
        """
        生成6位随机数字验证码

        Returns:
            str: 6位数字字符串
        """
        return "".join(random.choices(string.digits, k=VerificationCodeService.CODE_LENGTH))

    @staticmethod
    def _get_code_key(email: str, code_type: str = "register") -> str:
        """
        生成验证码的Redis key

        Args:
            email: 邮箱地址
            code_type: 验证码类型（register/login/reset_password等）

        Returns:
            str: Redis key
        """
        return f"verification_code:{code_type}:{email}"

    @staticmethod
    async def store_code(email: str, code: str, code_type: str = "register") -> None:
        """
        将验证码存储到Redis

        Args:
            email: 邮箱地址
            code: 验证码
            code_type: 验证码类型

        Raises:
            HTTPException: Redis连接失败时抛出
        """
        try:
            redis_client = await get_redis_connection()
            key = VerificationCodeService._get_code_key(email, code_type)
            await redis_client.setex(
                key,
                VerificationCodeService.CODE_EXPIRY,
                code
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"验证码存储失败: {str(e)}"
            )

    @staticmethod
    async def verify_code(email: str, code: str, code_type: str = "register") -> bool:
        """
        验证验证码是否正确

        Args:
            email: 邮箱地址
            code: 用户提交的验证码
            code_type: 验证码类型

        Returns:
            bool: 验证码正确返回True，否则返回False

        Note:
            验证成功后会删除验证码，防止重复使用
        """
        try:
            redis_client = await get_redis_connection()
            key = VerificationCodeService._get_code_key(email, code_type)
            
            # 获取存储的验证码
            stored_code = await redis_client.get(key)
            
            if not stored_code:
                return False
            
            # 验证码匹配
            if stored_code == code:
                # 验证成功后删除验证码，防止重复使用
                await redis_client.delete(key)
                return True
            
            return False
        except Exception:
            # Redis连接失败时，不阻塞业务流程，返回False
            return False

    @staticmethod
    async def delete_code(email: str, code_type: str = "register") -> None:
        """
        删除验证码（清理）

        Args:
            email: 邮箱地址
            code_type: 验证码类型
        """
        try:
            redis_client = await get_redis_connection()
            key = VerificationCodeService._get_code_key(email, code_type)
            await redis_client.delete(key)
        except Exception:
            # 清理失败不影响业务
            pass

    @staticmethod
    async def send_verification_code(email: str, code_type: str = "register") -> str:
        """
        生成验证码并发送（完整流程）

        Args:
            email: 邮箱地址
            code_type: 验证码类型

        Returns:
            str: 生成的验证码（用于测试环境，生产环境应返回成功消息）

        Note:
            实际生产环境中，应该通过邮件服务发送验证码，
            此处返回验证码仅用于开发和测试
        """
        # 生成验证码
        code = VerificationCodeService.generate_code()
        
        # 存储到Redis
        await VerificationCodeService.store_code(email, code, code_type)
        
        # TODO: 集成邮件服务，发送验证码到用户邮箱
        # await EmailService.send_verification_code(email, code)
        
        # 开发环境返回验证码（生产环境应该只返回"发送成功"）
        return code
