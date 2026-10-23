"""astrbot_plugin_ignore_user

按用户 ID 拦截指定用户的消息：名单内用户发送的任何消息（私聊、群聊）
都会在进入 AI 处理流程之前被直接拦截，机器人不予回复。

名单在 AstrBot 管理面板的插件配置页中维护（_conf_schema.json 中的
blocked_qq 配置项），无需修改代码。
"""

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_ignore_user",
    "bhdhdjdjzjizi-arch",
    "按用户 ID 拦截指定用户的消息，机器人不予回复",
    "1.1.0",
    "https://github.com/bhdhdjdjzjizi-arch/astrbot_plugin_ignore_user",
)
class IgnoreUserPlugin(Star):
    """用户消息拦截插件。

    以最高优先级监听全部消息事件：若发送者在拦截名单中，
    立即终止该事件，使其不进入后续任何处理（包括 AI 回复与指令）。
    """

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config

    def _blocked_set(self) -> set[str]:
        """读取当前拦截名单（每次调用都取最新配置，面板改完即生效）。"""
        if not self.config:
            return set()
        raw = self.config.get("blocked_qq", []) or []
        return {str(item).strip() for item in raw if str(item).strip()}

    @filter.event_message_type(filter.EventMessageType.ALL, priority=1000)
    async def block_user(self, event: AstrMessageEvent):
        sender = str(event.get_sender_id()).strip()
        if sender and sender in self._blocked_set():
            if not self.config or self.config.get("enable_block_log", True):
                logger.info(f"[ignore_user] blocked message from {sender}")
            event.stop_event()
