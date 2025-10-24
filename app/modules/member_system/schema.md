# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `APIResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` | 响应状态码 |
| `message` | `str` | ❌ | `` | 响应消息 |
| `data` | `Optional[Any]` | ❌ | `` | 响应数据 |
| `timestamp` | `datetime` | ❌ | `` | 响应时间 |

---

## `ActivityList`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `activities` | `List[MemberActivityRead]` | ❌ | `` | 活动列表 |
| `pagination` | `PaginationInfo` | ❌ | `` | 分页信息 |

---

## `ActivityParticipationBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `progress_data` | `Optional[Dict[str, Any]]` | ❌ | `` | 进度数据 |

---

## `ActivityParticipationCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `progress_data` | `Optional[Dict[str, Any]]` | ❌ | `` | 进度数据 |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `activity_id` | `int` | ❌ | `` | 活动ID |

---

## `ActivityParticipationRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `progress_data` | `Optional[Dict[str, Any]]` | ❌ | `` | 进度数据 |
| `participation_id` | `int` | ❌ | `` | 参与ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `activity_id` | `int` | ❌ | `` | 活动ID |
| `participation_time` | `datetime` | ❌ | `` | 参与时间 |
| `status` | `ParticipationStatus` | ❌ | `` | 参与状态 |

---

## `ActivityParticipationResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` | 响应状态码 |
| `message` | `str` | ❌ | `` | 响应消息 |
| `data` | `Optional[ActivityParticipationRead]` | ❌ | `` | 活动参与数据 |
| `timestamp` | `datetime` | ❌ | `` | 响应时间 |

---

## `BenefitEligibility`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `user_id` | `int` | ❌ | `` | 用户ID |
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `benefit_name` | `str` | ❌ | `` | 权益名称 |
| `eligible` | `bool` | ❌ | `` | 是否有资格 |
| `level_required` | `bool` | ❌ | `` | 是否需要等级 |
| `usage_limit` | `int` | ❌ | `` | 使用限制 |
| `used_count` | `int` | ❌ | `` | 已使用次数 |
| `remaining_count` | `int` | ❌ | `` | 剩余次数 |
| `reset_cycle` | `Optional[str]` | ❌ | `` | 重置周期 |
| `next_reset_date` | `Optional[datetime]` | ❌ | `` | 下次重置时间 |

---

## `BenefitStatus`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `free_shipping` | `bool` | ❌ | `` | 免运费 |
| `birthday_gift` | `bool` | ❌ | `` | 生日礼品 |
| `priority_service` | `bool` | ❌ | `` | 优先服务 |
| `exclusive_events` | `bool` | ❌ | `` | 专属活动 |
| `points_multiplier` | `bool` | ❌ | `` | 积分倍数 |
| `custom_service` | `bool` | ❌ | `` | 专属客服 |

---

## `BenefitUsageBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 使用描述 |
| `benefit_value` | `Optional[float]` | ❌ | `` | 权益价值 |

---

## `BenefitUsageCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 使用描述 |
| `benefit_value` | `Optional[float]` | ❌ | `` | 权益价值 |
| `user_id` | `int` | ❌ | `` | 用户ID |

---

## `BenefitUsageList`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `usage_history` | `List[BenefitUsageRead]` | ❌ | `` | 使用历史 |
| `pagination` | `PaginationInfo` | ❌ | `` | 分页信息 |

---

## `BenefitUsageRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 使用描述 |
| `benefit_value` | `Optional[float]` | ❌ | `` | 权益价值 |
| `usage_id` | `int` | ❌ | `` | 使用记录ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `used_at` | `datetime` | ❌ | `` | 使用时间 |

---

## `BenefitUsageResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` | 响应状态码 |
| `message` | `str` | ❌ | `` | 响应消息 |
| `data` | `Optional[BenefitUsageRead]` | ❌ | `` | 权益使用数据 |
| `timestamp` | `datetime` | ❌ | `` | 响应时间 |

---

## `LevelInfo`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `level_id` | `int` | ❌ | `` | 等级ID |
| `level_name` | `str` | ❌ | `` | 等级名称 |
| `level_code` | `MemberLevelCode` | ❌ | `` | 等级代码 |
| `discount_rate` | `float` | ❌ | `` | 折扣率 |
| `point_multiplier` | `float` | ❌ | `` | 积分倍数 |

---

## `MemberActivityBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `str` | ❌ | `` | 活动标题 |
| `description` | `str` | ❌ | `` | 活动描述 |
| `activity_type` | `str` | ❌ | `` | 活动类型 |
| `start_time` | `datetime` | ❌ | `` | 开始时间 |
| `end_time` | `datetime` | ❌ | `` | 结束时间 |
| `max_participants` | `Optional[int]` | ❌ | `` | 最大参与人数 |
| `reward_config` | `Optional[Dict[str, Any]]` | ❌ | `` | 奖励配置 |
| `participation_rules` | `Optional[Dict[str, Any]]` | ❌ | `` | 参与规则 |

---

## `MemberActivityCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `str` | ❌ | `` | 活动标题 |
| `description` | `str` | ❌ | `` | 活动描述 |
| `activity_type` | `str` | ❌ | `` | 活动类型 |
| `start_time` | `datetime` | ❌ | `` | 开始时间 |
| `end_time` | `datetime` | ❌ | `` | 结束时间 |
| `max_participants` | `Optional[int]` | ❌ | `` | 最大参与人数 |
| `reward_config` | `Optional[Dict[str, Any]]` | ❌ | `` | 奖励配置 |
| `participation_rules` | `Optional[Dict[str, Any]]` | ❌ | `` | 参与规则 |

---

## `MemberActivityRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `str` | ❌ | `` | 活动标题 |
| `description` | `str` | ❌ | `` | 活动描述 |
| `activity_type` | `str` | ❌ | `` | 活动类型 |
| `start_time` | `datetime` | ❌ | `` | 开始时间 |
| `end_time` | `datetime` | ❌ | `` | 结束时间 |
| `max_participants` | `Optional[int]` | ❌ | `` | 最大参与人数 |
| `reward_config` | `Optional[Dict[str, Any]]` | ❌ | `` | 奖励配置 |
| `participation_rules` | `Optional[Dict[str, Any]]` | ❌ | `` | 参与规则 |
| `activity_id` | `int` | ❌ | `` | 活动ID |
| `current_participants` | `int` | ❌ | `` | 当前参与人数 |
| `status` | `ActivityStatus` | ❌ | `` | 活动状态 |
| `created_at` | `datetime` | ❌ | `` | 创建时间 |

---

## `MemberActivityUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `Optional[str]` | ❌ | `` | 活动标题 |
| `description` | `Optional[str]` | ❌ | `` | 活动描述 |
| `start_time` | `Optional[datetime]` | ❌ | `` | 开始时间 |
| `end_time` | `Optional[datetime]` | ❌ | `` | 结束时间 |
| `max_participants` | `Optional[int]` | ❌ | `` | 最大参与人数 |
| `status` | `Optional[ActivityStatus]` | ❌ | `` | 活动状态 |
| `reward_config` | `Optional[Dict[str, Any]]` | ❌ | `` | 奖励配置 |
| `participation_rules` | `Optional[Dict[str, Any]]` | ❌ | `` | 参与规则 |

---

## `MemberBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `nickname` | `Optional[str]` | ❌ | `` | 会员昵称，1-50个字符 |
| `birthday` | `Optional[date]` | ❌ | `` | 生日日期 |
| `preferences` | `Optional[Dict[str, Any]]` | ❌ | `` | 用户偏好设置 |

---

## `MemberCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `nickname` | `str` | ❌ | `` | 会员昵称，必填 |
| `birthday` | `Optional[date]` | ❌ | `` | 生日日期 |
| `preferences` | `Optional[Dict[str, Any]]` | ❌ | `` | 用户偏好设置 |

---

## `MemberProfileResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` | 响应状态码 |
| `message` | `str` | ❌ | `` | 响应消息 |
| `data` | `Optional[MemberWithDetails]` | ❌ | `` | 会员档案数据 |
| `timestamp` | `datetime` | ❌ | `` | 响应时间 |

---

## `MemberRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `nickname` | `Optional[str]` | ❌ | `` | 会员昵称，1-50个字符 |
| `birthday` | `Optional[date]` | ❌ | `` | 生日日期 |
| `preferences` | `Optional[Dict[str, Any]]` | ❌ | `` | 用户偏好设置 |
| `member_id` | `str` | ❌ | `` | 会员ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `level_id` | `int` | ❌ | `` | 会员等级ID |
| `total_spent` | `float` | ❌ | `` | 总消费金额 |
| `total_orders` | `int` | ❌ | `` | 总订单数 |
| `join_date` | `datetime` | ❌ | `` | 加入日期 |
| `last_active_at` | `Optional[datetime]` | ❌ | `` | 最后活跃时间 |
| `level_upgrade_date` | `Optional[datetime]` | ❌ | `` | 等级升级时间 |

---

## `MemberStatistics`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_spent` | `float` | ❌ | `` | 总消费金额 |
| `total_orders` | `int` | ❌ | `` | 总订单数 |
| `join_date` | `str` | ❌ | `` | 加入日期 |
| `last_active` | `Optional[str]` | ❌ | `` | 最后活跃时间 |

---

## `MemberUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `nickname` | `Optional[str]` | ❌ | `` | 会员昵称，1-50个字符 |
| `birthday` | `Optional[date]` | ❌ | `` | 生日日期 |
| `preferences` | `Optional[Dict[str, Any]]` | ❌ | `` | 用户偏好设置 |

---

## `MemberWithDetails`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `member_id` | `str` | ❌ | `` | 会员ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `level` | `LevelInfo` | ❌ | `` | 等级信息 |
| `points` | `PointSummary` | ❌ | `` | 积分信息 |
| `statistics` | `MemberStatistics` | ❌ | `` | 统计信息 |
| `benefits` | `BenefitStatus` | ❌ | `` | 权益状态 |
| `next_level` | `Optional[NextLevelInfo]` | ❌ | `` | 下一等级信息 |

---

## `MembershipBenefitBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `benefit_name` | `str` | ❌ | `` | 权益名称 |
| `description` | `Optional[str]` | ❌ | `` | 权益描述 |
| `usage_limit` | `Optional[int]` | ❌ | `` | 使用次数限制 |
| `reset_cycle` | `Optional[str]` | ❌ | `` | 重置周期 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |

---

## `MembershipBenefitRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `benefit_type` | `BenefitType` | ❌ | `` | 权益类型 |
| `benefit_name` | `str` | ❌ | `` | 权益名称 |
| `description` | `Optional[str]` | ❌ | `` | 权益描述 |
| `usage_limit` | `Optional[int]` | ❌ | `` | 使用次数限制 |
| `reset_cycle` | `Optional[str]` | ❌ | `` | 重置周期 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |
| `benefit_id` | `int` | ❌ | `` | 权益ID |
| `level_id` | `int` | ❌ | `` | 等级ID |

---

## `MembershipLevelBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `level_name` | `str` | ❌ | `` | 等级名称 |
| `level_code` | `MemberLevelCode` | ❌ | `` | 等级代码 |
| `required_spent` | `float` | ❌ | `` | 升级所需消费金额 |
| `discount_rate` | `float` | ❌ | `` | 折扣率 |
| `point_multiplier` | `float` | ❌ | `` | 积分倍数 |
| `description` | `Optional[str]` | ❌ | `` | 等级描述 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |

---

## `MembershipLevelRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `level_name` | `str` | ❌ | `` | 等级名称 |
| `level_code` | `MemberLevelCode` | ❌ | `` | 等级代码 |
| `required_spent` | `float` | ❌ | `` | 升级所需消费金额 |
| `discount_rate` | `float` | ❌ | `` | 折扣率 |
| `point_multiplier` | `float` | ❌ | `` | 积分倍数 |
| `description` | `Optional[str]` | ❌ | `` | 等级描述 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |
| `level_id` | `int` | ❌ | `` | 等级ID |

---

## `NextLevelInfo`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `level_name` | `str` | ❌ | `` | 等级名称 |
| `level_code` | `MemberLevelCode` | ❌ | `` | 等级代码 |
| `required_spent` | `float` | ❌ | `` | 升级所需消费 |
| `remaining_spent` | `float` | ❌ | `` | 剩余所需消费 |
| `progress_percentage` | `float` | ❌ | `` | 升级进度百分比 |

---

## `PaginationInfo`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `page` | `int` | ❌ | `` | 当前页码 |
| `limit` | `int` | ❌ | `` | 每页数量 |
| `total` | `int` | ❌ | `` | 总记录数 |
| `total_pages` | `int` | ❌ | `` | 总页数 |

---

## `PointSummary`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_points` | `int` | ❌ | `` | 总获得积分 |
| `available_points` | `int` | ❌ | `` | 可用积分 |
| `frozen_points` | `int` | ❌ | `` | 冻结积分 |
| `expiring_points` | `int` | ❌ | `` | 即将过期积分 |
| `expiring_date` | `Optional[datetime]` | ❌ | `` | 最近过期时间 |

---

## `PointTransactionBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `transaction_type` | `TransactionType` | ❌ | `` | 交易类型 |
| `event_type` | `EventType` | ❌ | `` | 事件类型 |
| `points` | `int` | ❌ | `` | 积分数量，正数为获得，负数为使用 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 交易描述 |

---

## `PointTransactionCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `transaction_type` | `TransactionType` | ❌ | `` | 交易类型 |
| `event_type` | `EventType` | ❌ | `` | 事件类型 |
| `points` | `int` | ❌ | `` | 积分数量，正数为获得，负数为使用 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 交易描述 |
| `user_id` | `int` | ❌ | `` | 用户ID |

---

## `PointTransactionList`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `summary` | `PointSummary` | ❌ | `` | 积分汇总 |
| `transactions` | `List[PointTransactionRead]` | ❌ | `` | 交易记录 |
| `pagination` | `PaginationInfo` | ❌ | `` | 分页信息 |

---

## `PointTransactionRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `transaction_type` | `TransactionType` | ❌ | `` | 交易类型 |
| `event_type` | `EventType` | ❌ | `` | 事件类型 |
| `points` | `int` | ❌ | `` | 积分数量，正数为获得，负数为使用 |
| `reference_id` | `Optional[str]` | ❌ | `` | 关联订单或活动ID |
| `description` | `Optional[str]` | ❌ | `` | 交易描述 |
| `transaction_id` | `str` | ❌ | `` | 交易ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `balance_after` | `int` | ❌ | `` | 交易后余额 |
| `expiry_date` | `Optional[datetime]` | ❌ | `` | 过期时间 |
| `created_at` | `datetime` | ❌ | `` | 创建时间 |

---

## `PointTransactionResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` | 响应状态码 |
| `message` | `str` | ❌ | `` | 响应消息 |
| `data` | `Optional[PointTransactionRead]` | ❌ | `` | 积分交易数据 |
| `timestamp` | `datetime` | ❌ | `` | 响应时间 |

---

## `SystemConfigBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `config_key` | `str` | ❌ | `` | 配置键 |
| `config_value` | `str` | ❌ | `` | 配置值 |
| `description` | `Optional[str]` | ❌ | `` | 配置描述 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |

---

## `SystemConfigCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `config_key` | `str` | ❌ | `` | 配置键 |
| `config_value` | `str` | ❌ | `` | 配置值 |
| `description` | `Optional[str]` | ❌ | `` | 配置描述 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |

---

## `SystemConfigRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `config_key` | `str` | ❌ | `` | 配置键 |
| `config_value` | `str` | ❌ | `` | 配置值 |
| `description` | `Optional[str]` | ❌ | `` | 配置描述 |
| `is_active` | `bool` | ❌ | `` | 是否激活 |
| `config_id` | `int` | ❌ | `` | 配置ID |
| `created_at` | `datetime` | ❌ | `` | 创建时间 |
| `updated_at` | `Optional[datetime]` | ❌ | `` | 更新时间 |

---

## `SystemConfigUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `config_value` | `Optional[str]` | ❌ | `` | 配置值 |
| `description` | `Optional[str]` | ❌ | `` | 配置描述 |
| `is_active` | `Optional[bool]` | ❌ | `` | 是否激活 |

---

## `UserActivityList`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `activities` | `List[Dict[str, Any]]` | ❌ | `` | 参与的活动 |
| `pagination` | `PaginationInfo` | ❌ | `` | 分页信息 |

---

